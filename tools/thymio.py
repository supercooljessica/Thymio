#!/usr/bin/env python3
"""Talk to a Thymio (real or simulated) through Thymio Suite's device manager.

Thymio Suite must be open. Run it through the launcher in the repo folder:
"thymio" on Windows (".\\thymio" in PowerShell), "./thymio.sh" on macOS/Linux.

  thymio list
  thymio load shinchan_bot.aesl
  thymio stop
  thymio read prox.horizontal state
  thymio watch prox.horizontal state --seconds 5
  thymio set detect=800 leds.top=0,32,0
  thymio size shinchan_bot.aesl
  thymio trail playgrounds/arena_chase.playground shinchan=shinchan_bot.aesl victim=sim_victim.aesl

With several robots connected, pick one with --robot and part of its name,
e.g. --robot shinchan. Only one program can control a robot at a time,
so disconnect Aseba Studio from it before load, stop, set, size or trail.
"""

import argparse
import os
import sys
import threading
import time
import xml.etree.ElementTree as ET

from tdmclient import ClientAsync
from tdmclient.clientasync import NodeLockError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trail  # noqa: E402

BYTECODE_WORDS = 1534

STATUS_NAMES = {0: "unknown", 1: "connected", 2: "available", 3: "busy",
                4: "ready", 5: "disconnected"}


def read_program(path):
    """Aseba source from an .aesl file (Aseba Studio) or a plain .aseba file."""
    if not path.lower().endswith(".aesl"):
        with open(path) as f:
            return f.read()
    root = ET.parse(path).getroot()
    if root.findall("constant") or root.findall("event"):
        sys.exit(f"{path}: global constants and events are not supported yet")
    nodes = root.findall("node")
    if len(nodes) != 1:
        sys.exit(f"{path}: expected one <node>, found {len(nodes)}")
    return nodes[0].text or ""


def parse_assignment(text):
    """'name=1' -> ('name', [1]); 'name=1,2,3' -> ('name', [1, 2, 3])."""
    name, sep, value = text.partition("=")
    if not sep:
        sys.exit(f"expected name=value, got {text!r}")
    return name, [int(v) for v in value.split(",")]


def give_up():
    print("No answer from the robot. Did the simulator or Thymio Suite close?",
          file=sys.stderr, flush=True)
    os._exit(1)


def show(node, names):
    parts = []
    for name in names:
        if name not in node.var:
            sys.exit(f"no variable {name!r} on this robot")
        value = node.var[name]
        parts.append(f"{name}={value[0] if len(value) == 1 else value}")
    print("  ".join(parts), flush=True)


async def wait_for_robot(client, seconds=5):
    """True once a robot shows up. (tdmclient's own wait_for_node timeout
    never runs out while Thymio Suite keeps sending messages.)"""
    deadline = time.monotonic() + seconds
    while not client.nodes and time.monotonic() < deadline:
        await client.sleep(0.1)
    return bool(client.nodes)


async def find_node(client, robot):
    if not await wait_for_robot(client):
        sys.exit("No robot found. Is Thymio Suite open, and the robot or simulator on?")
    await client.sleep(0.5)  # let the rest of the robot list arrive
    nodes = [n for n in client.nodes
             if robot is None or robot.lower() in n.props["name"].lower()]
    if not nodes:
        sys.exit(f"No robot named like {robot!r}. Try: tools/thymio.py list")
    if len(nodes) > 1:
        names = "\n  ".join(n.props["name"] for n in nodes)
        sys.exit(f"Several robots, pick one with --robot:\n  {names}")
    return nodes[0]


async def lock(node):
    try:
        return await node.lock()
    except NodeLockError:
        sys.exit("Robot is busy. Disconnect it in Aseba Studio (or other apps) first.")


async def bytecode_words(node, program):
    """Words of robot program memory a program uses, to within 2.

    The compiler only says whether a program fits, so pad it with 2-word
    lines until it stops fitting, and compare with an empty program."""
    async def fits(src, pad):
        text = "var size_pad\n" + src + "\n" + "size_pad = 1\n" * pad
        return await node.compile(text, load=False) is None

    async def room(src):
        lo, hi = 0, BYTECODE_WORDS
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if await fits(src, mid):
                lo = mid
            else:
                hi = mid - 1
        return lo

    error = await node.compile(program, load=False)
    if error is not None:
        return None, error
    return (await room("") - await room(program)) * 2, None


def parse_trail_sets(texts, names):
    """'shinchan.t90=1482' -> ('shinchan', 't90', [1482])."""
    out = []
    for text in texts:
        target, _, assignment = text.partition(".")
        if target not in names or "=" not in assignment:
            sys.exit(f"--set needs ROBOT.variable=value with ROBOT one of {', '.join(names)}, got {text!r}")
        out.append((target, *parse_assignment(assignment)))
    return out


async def run_trail(client, args):
    arena = trail.read_arena(args.arena)
    robots = {r["name"]: r for r in arena["robots"]}
    jobs = []
    for job in args.programs:
        name, sep, path = job.rpartition("=")
        if not sep:
            if len(robots) != 1:
                sys.exit(f"This arena has several robots; write ROBOT=FILE with ROBOT one of {', '.join(robots)}")
            name = next(iter(robots))
        if name not in robots:
            sys.exit(f"No robot named {name!r} in {args.arena}; robots: {', '.join(robots)}")
        jobs.append((name, path, trail.instrument(read_program(path))))
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        found = {n.props["name"].split(" on ")[0]: n for n in client.nodes}
        if all(name in found for name, _, _ in jobs):
            break
        await client.sleep(0.2)
    else:
        sys.exit("Not all robots found. Is the simulator open with " + args.arena + "?")
    sets = [(found[r], {var: val}) for r, var, val in parse_trail_sets(args.set, list(robots))]
    print(f"Recording {args.seconds:.0f} s ...", flush=True)
    events = await trail.record(client, [(found[name], src) for name, _, src in jobs], args.seconds, sets, lock)
    tracks = []
    for (name, path, src), ev in zip(jobs, events):
        tracks.append((f"{name} ({os.path.basename(path)})", trail.rebuild(ev, robots[name], args.k, args.w),
                       "trc_ev[3] = state" in src))
        print(f"{name}: {len(ev)} wheel updates")
    title = args.title or f"Trail in {os.path.basename(args.arena)}"
    trail.write_svg(args.out, arena, tracks, args.solid, title, args.k, args.w)
    print(f"Wrote {args.out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--robot", help="part of the robot's name")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show connected robots")
    sub.add_parser("load", help="compile and run a program").add_argument("file")
    sub.add_parser("stop", help="stop the running program")
    sub.add_parser("read", help="print variables once").add_argument("names", nargs="+")
    watch = sub.add_parser("watch", help="print variables repeatedly")
    watch.add_argument("names", nargs="+")
    watch.add_argument("--seconds", type=float, default=5)
    watch.add_argument("--every", type=float, default=0.2, help="seconds between lines")
    sub.add_parser("set", help="change variables").add_argument("assignments", nargs="+")
    sub.add_parser("size", help="words of robot memory a program uses").add_argument("file")
    tr = sub.add_parser("trail", help="record robots in the simulator and draw their trails (SVG)")
    tr.add_argument("arena", help=".playground file the simulator was just opened with")
    tr.add_argument("programs", nargs="+", help="ROBOT=FILE for each robot (just FILE if the arena has one robot)")
    tr.add_argument("--seconds", type=float, default=120)
    tr.add_argument("--out", default="trail.svg")
    tr.add_argument("--set", action="append", default=[], metavar="ROBOT.VAR=VALUE",
                    help="change a variable right after the programs start")
    tr.add_argument("--solid", type=float, default=100, help="draw faded after this many seconds")
    tr.add_argument("--title")
    tr.add_argument("--k", type=float, default=0.332, help="mm/s per motor speed unit (simulator: 0.332)")
    tr.add_argument("--w", type=float, default=94.9, help="mm between the wheels (simulator: 94.9)")
    args = parser.parse_args()

    program = read_program(args.file) if args.command in ("load", "size") else None
    status = 0

    # If the robot stops answering (e.g. the simulator crashed), give up instead of hanging.
    limit = 30 + {"watch": getattr(args, "seconds", 0), "trail": getattr(args, "seconds", 0) + 30,
                  "size": 90}.get(args.command, 0)
    watchdog = threading.Timer(limit, give_up)
    watchdog.daemon = True
    watchdog.start()

    with ClientAsync() as client:

        async def prog():
            nonlocal status
            if args.command == "list":
                if await wait_for_robot(client):
                    await client.sleep(0.5)
                for n in client.nodes:
                    print(f"{n.props['name']}  [{STATUS_NAMES.get(n.status, n.status)}]")
                if not client.nodes:
                    print("No robot found.")
                return

            if args.command == "trail":
                if not await wait_for_robot(client):
                    sys.exit("No robot found. Is Thymio Suite open, and the simulator on?")
                await run_trail(client, args)
                return

            node = await find_node(client, args.robot)

            if args.command == "size":
                with await lock(node):
                    words, error = await bytecode_words(node, program)
                if error is not None:
                    print(f"Compilation error: {error['error_msg']}")
                    status = 2
                else:
                    print(f"{args.file}: about {words} of {BYTECODE_WORDS} words "
                          f"({100 * words // BYTECODE_WORDS}%), {BYTECODE_WORDS - words} free")
                return

            if args.command in ("read", "watch"):
                await node.watch(variables=True)
                for _ in range(30):  # up to 3 s for the values to arrive
                    missing = set(args.names) - set(node.var)
                    if not missing:
                        break
                    await client.sleep(0.1)
                if missing:
                    sys.exit(f"Not found on this robot: {', '.join(sorted(missing))}. "
                             "Is the program that defines it loaded?")
                show(node, args.names)
                if args.command == "watch":
                    for _ in range(int(args.seconds / args.every)):
                        await client.sleep(args.every)
                        show(node, args.names)
                return

            with await lock(node):
                if args.command == "load":
                    error = await node.compile(program)
                    if error is not None:
                        print(f"Compilation error: {error['error_msg']}")
                        status = 2
                        return
                    error = await node.run()
                    print(f"Run error {error['error_code']}" if error else
                          f"Running {args.file} on {node.props['name']}")
                elif args.command == "stop":
                    error = await node.stop()
                    print(f"Stop error {error['error_code']}" if error else "Stopped")
                elif args.command == "set":
                    error = await node.set_variables(
                        dict(parse_assignment(a) for a in args.assignments))
                    print(f"Set error {error['error_code']}" if error else "Set")
                status = 2 if error else 0

        client.run_async_program(prog)

    return status


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:  # Ctrl+C during watch
        sys.exit(130)
    except ConnectionRefusedError:
        sys.exit("Can't reach Thymio Suite. Open it, start the simulator or plug in "
                 "the robot, then try again.")
