#!/usr/bin/env python3
"""Talk to a Thymio (real or simulated) through Thymio Suite's device manager.

Thymio Suite must be open. Run it through the launcher in the repo folder:
"thymio" on Windows (".\\thymio" in PowerShell), "./thymio.sh" on macOS/Linux.

  thymio list
  thymio load thymio_hunter.aesl
  thymio stop
  thymio read prox.horizontal state
  thymio watch prox.horizontal state --seconds 5
  thymio set detect_threshold=800 leds.top=0,32,0

With several robots connected, pick one with --robot and part of its name,
e.g. --robot "Thymio II 0". Only one program can control a robot at a time,
so disconnect Aseba Studio from it before load, stop or set.
"""

import argparse
import sys
import xml.etree.ElementTree as ET

from tdmclient import ClientAsync
from tdmclient.clientasync import NodeLockError

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


def show(node, names):
    parts = []
    for name in names:
        if name not in node.var:
            sys.exit(f"no variable {name!r} on this robot")
        value = node.var[name]
        parts.append(f"{name}={value[0] if len(value) == 1 else value}")
    print("  ".join(parts), flush=True)


async def find_node(client, robot):
    if await client.wait_for_node(timeout=5) is None:
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
    args = parser.parse_args()

    program = read_program(args.file) if args.command == "load" else None
    status = 0

    with ClientAsync() as client:

        async def prog():
            nonlocal status
            if args.command == "list":
                if await client.wait_for_node(timeout=5) is not None:
                    await client.sleep(0.5)
                for n in client.nodes:
                    print(f"{n.props['name']}  [{STATUS_NAMES.get(n.status, n.status)}]")
                if not client.nodes:
                    print("No robot found.")
                return

            node = await find_node(client, args.robot)

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
