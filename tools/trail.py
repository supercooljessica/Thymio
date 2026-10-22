"""Record robots in the simulator and draw their trails as an SVG, to scale.

Used by "thymio trail". Each program gets a copy with a 10 ms clock and an
"emit" after every event, so the robot itself reports each wheel change. The
path is rebuilt from those wheel speeds, starting from the robot's pose in the
.playground file, so open the simulator fresh (robots at their start) first.

Small errors add up (bumps, rounding), so the trail is drawn faded after
--solid seconds.
"""

import math
import re
import time
import xml.etree.ElementTree as ET
from contextlib import ExitStack

STATE_COLORS = {1: "#2f6fdf", 2: "#22a046", 3: "#16b5c4", 4: "#e03131", 5: "#c2259e", 6: "#d4a017"}
STATE_NAMES = {1: "SEARCH", 2: "PURSUE", 5: "TAUNT", 6: "RECOVER", 4: "AVOID", 3: "BORED (underpants)"}
OTHER_COLORS = ["#555555", "#8c564b", "#7f7f7f"]
BLOCK = re.compile(r"\s*(onevent|sub)\s")


def instrument(src):
    """Copy of an Aseba program that emits [clock, left, right, state] after every event."""
    if re.search(r"onevent\s+timer1\b", src) or "timer.period[1]" in src:
        raise SystemExit("This program uses timer 1, which the trail recorder needs for its clock.")
    has_state = re.search(r"^\s*var\s+state\b", src, re.M) is not None
    lines = src.split("\n")
    first = next((i for i, l in enumerate(lines) if BLOCK.match(l)), len(lines))
    head = ["var trc_clk", "var trc_ev[4]"] + lines[:first] + [
        "trc_clk = 0", "timer.period[1] = 10", "",
        "onevent timer1", "trc_clk += 1", "",
        "sub trc_tell", "trc_ev[0] = trc_clk",
        "trc_ev[1] = motor.left.target", "trc_ev[2] = motor.right.target",
        "trc_ev[3] = " + ("state" if has_state else "0"), "emit trc trc_ev", ""]
    body, in_event = [], False
    for line in lines[first:]:
        if BLOCK.match(line):
            if in_event:
                body.append("callsub trc_tell")
            in_event = line.strip().startswith("onevent")
        body.append(line)
    if in_event:
        body.append("callsub trc_tell")
    return "\n".join(head + body) + "\n"


def read_arena(path):
    """World size, obstacles and robot start poses from a .playground file (mm, radians)."""
    root = ET.parse(path).getroot()
    world = root.find("world")
    arena = {"w": float(world.get("w")) * 10, "h": float(world.get("h")) * 10,
             "cylinders": [], "walls": [], "robots": []}
    for c in root.findall("cylinder"):
        arena["cylinders"].append((float(c.get("x")) * 10, float(c.get("y")) * 10, float(c.get("r")) * 10))
    for w in root.findall("wall"):
        arena["walls"].append((float(w.get("x")) * 10, float(w.get("y")) * 10,
                               float(w.get("l1")) * 10, float(w.get("l2")) * 10))
    for i, r in enumerate(root.findall("robot")):
        arena["robots"].append({"name": r.get("name") or f"Thymio II {i}",
                                "x": float(r.get("x")) * 10, "y": float(r.get("y")) * 10,
                                "angle": float(r.get("angle", "0"))})
    return arena


async def record(client, jobs, seconds, sets, lock):
    """jobs: list of (node, source). Returns one event list per job."""
    events = [[] for _ in jobs]
    with ExitStack() as stack:
        for node, _ in jobs:
            stack.enter_context(await lock(node))
        for i, (node, src) in enumerate(jobs):
            await node.register_events([("trc", 4)])
            await node.watch(events=True)
            node.add_event_received_listener(
                lambda n, name, data, i=i: events[i].append(list(data)) if name == "trc" else None)
            error = await node.compile(src)
            if error is not None:
                raise SystemExit(f"Compilation error on {node.props['name']}: {error['error_msg']}")
        for node, _ in jobs:
            await node.run()
        for node, values in sets:
            await node.set_variables(values)
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            await client.sleep(0.5)
        for node, _ in jobs:
            await node.stop()
            await node.set_variables({"motor.left.target": [0], "motor.right.target": [0]})
    return events


def rebuild(events, start, k, wheels):
    """Path [(seconds, x, y, state)] from [clock, left, right, state] events."""
    x, y, h = start["x"], start["y"], start["angle"]
    if not events:
        return [(0.0, x, y, 0)]
    t0 = events[0][0]
    path = [(0.0, x, y, events[0][3])]
    for prev, cur in zip(events, events[1:]):
        dt = (cur[0] - prev[0]) / 100
        vl, vr = prev[1] * k, prev[2] * k
        v, w = (vl + vr) / 2, (vr - vl) / wheels
        steps = max(1, int(dt / 0.02))
        for _ in range(steps):
            s = dt / steps
            x += v * math.cos(h + w * s / 2) * s
            y += v * math.sin(h + w * s / 2) * s
            h += w * s
            path.append(((cur[0] - t0) / 100, x, y, prev[3]))
        path.append(((cur[0] - t0) / 100, x, y, cur[3]))
    return path


def write_svg(out, arena, tracks, solid, title, k, wheels):
    """tracks: list of (label, path, colour_by_state)."""
    side = 800
    scale = side / max(arena["w"], arena["h"])
    aw, ah = arena["w"] * scale, arena["h"] * scale
    m, top, lx = 64, 70, 64 + aw + 36
    width, height = lx + 300, max(top + ah + 70, 640)

    def P(px, py):
        return m + px * scale, top + (arena["h"] - py) * scale

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
         f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="Helvetica, Arial, sans-serif">',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0,2 L5,5 L0,8" fill="none" stroke="#333"/></marker></defs>',
         '<rect width="100%" height="100%" fill="#fff"/>',
         f'<text x="{m}" y="26" font-size="17" font-weight="bold">{title}</text>']
    longest = max((p[-1][0] for _, p, _ in tracks), default=0)
    o.append(f'<text x="{m}" y="46" font-size="12" fill="#555">{longest:.0f} s of simulator time, '
             f'rebuilt from the wheel speeds the robots reported.</text>')
    step = 100 if max(arena["w"], arena["h"]) <= 3000 else 500
    for g in range(0, int(arena["w"]) + 1, step):
        gx, _ = P(g, 0)
        o.append(f'<line x1="{gx:.1f}" y1="{top}" x2="{gx:.1f}" y2="{top + ah:.1f}" stroke="#f0f0f0"/>')
        if g % 500 == 0:
            o.append(f'<text x="{gx:.1f}" y="{top + ah + 15:.1f}" font-size="11" text-anchor="middle" fill="#777">{g // 10}</text>')
    for g in range(0, int(arena["h"]) + 1, step):
        _, gy = P(0, g)
        o.append(f'<line x1="{m}" y1="{gy:.1f}" x2="{m + aw:.1f}" y2="{gy:.1f}" stroke="#f0f0f0"/>')
        if g % 500 == 0:
            o.append(f'<text x="{m - 6}" y="{gy + 4:.1f}" font-size="11" text-anchor="end" fill="#777">{g // 10}</text>')
    o.append(f'<rect x="{m}" y="{top}" width="{aw:.1f}" height="{ah:.1f}" fill="none" stroke="#333" stroke-width="2"/>')
    o.append(f'<line x1="{m}" y1="{top + ah + 30:.1f}" x2="{m + aw:.1f}" y2="{top + ah + 30:.1f}" stroke="#333" '
             f'marker-start="url(#a)" marker-end="url(#a)"/><text x="{m + aw / 2:.1f}" y="{top + ah + 46:.1f}" '
             f'font-size="13" text-anchor="middle">{arena["w"] / 10:.0f} cm</text>')
    o.append(f'<line x1="{m - 36}" y1="{top}" x2="{m - 36}" y2="{top + ah:.1f}" stroke="#333" '
             f'marker-start="url(#a)" marker-end="url(#a)"/><text x="{m - 42}" y="{top + ah / 2:.1f}" font-size="13" '
             f'text-anchor="middle" transform="rotate(-90 {m - 42} {top + ah / 2:.1f})">{arena["h"] / 10:.0f} cm</text>')
    for cx, cy, r in arena["cylinders"]:
        px, py = P(cx, cy)
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * scale:.1f}" fill="#ccc" stroke="#555"/>'
                 f'<text x="{px:.1f}" y="{py + r * scale + 13:.1f}" font-size="10" text-anchor="middle" '
                 f'fill="#555">({cx / 10:.0f}, {cy / 10:.0f})</text>')
    for wx, wy, l1, l2 in arena["walls"]:
        px, py = P(wx - l1 / 2, wy + l2 / 2)
        o.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{l1 * scale:.1f}" height="{l2 * scale:.1f}" fill="#bbb"/>')
    for n, (label, path, by_state) in enumerate(tracks):
        other = OTHER_COLORS[n % len(OTHER_COLORS)]
        seg, prev_key = [], None
        for t, x, y, st in path:
            key = (STATE_COLORS.get(st, other) if by_state else other, t <= solid)
            if key != prev_key and seg:
                o.append(_polyline(seg, prev_key, P, by_state))
                seg = seg[-1:]
            seg.append((x, y))
            prev_key = key
        if len(seg) > 1:
            o.append(_polyline(seg, prev_key, P, by_state))
        if by_state:
            for (t0, *_rest0, s0), (t1, x1, y1, s1) in zip(path, path[1:]):
                if s1 == 5 and s0 != 5:
                    px, py = P(x1, y1)
                    o.append(f'<path d="M{px - 5:.1f},{py:.1f} L{px:.1f},{py - 5:.1f} L{px + 5:.1f},{py:.1f} '
                             f'L{px:.1f},{py + 5:.1f} Z" fill="#c2259e" fill-opacity="{1 if t1 <= solid else 0.35}" '
                             f'stroke="#000" stroke-width="0.6"/>')
        sx, sy = P(path[0][1], path[0][2])
        ex, ey = P(path[-1][1], path[-1][2])
        o.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="6" fill="none" stroke="#000" stroke-width="2"/>'
                 f'<text x="{sx + 8:.1f}" y="{sy - 8:.1f}" font-size="11">{label}</text>'
                 f'<rect x="{ex - 4:.1f}" y="{ey - 4:.1f}" width="8" height="8" fill="#000"/>')
    ly = top + 14
    if any(by_state for _, _, by_state in tracks):
        o.append(f'<text x="{lx}" y="{ly}" font-size="13" font-weight="bold">Mode (LED colour)</text>')
        for i, st in enumerate([1, 2, 5, 6, 4, 3]):
            yy = ly + 24 + i * 22
            o.append(f'<line x1="{lx}" y1="{yy - 4}" x2="{lx + 26}" y2="{yy - 4}" stroke="{STATE_COLORS[st]}" '
                     f'stroke-width="3"/><text x="{lx + 34}" y="{yy}" font-size="12">{STATE_NAMES[st]}</text>')
        ly += 24 + 6 * 22 + 6
    for n, (label, _, by_state) in enumerate(tracks):
        if not by_state:
            o.append(f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 26}" y2="{ly - 4}" stroke="{OTHER_COLORS[n % 3]}" '
                     f'stroke-width="2"/><text x="{lx + 34}" y="{ly}" font-size="12">{label}</text>')
            ly += 22
    items = [(f'<circle cx="{lx + 13}" cy="{{y}}" r="6" fill="none" stroke="#000" stroke-width="2"/>', "start"),
             (f'<rect x="{lx + 9}" y="{{y4}}" width="8" height="8" fill="#000"/>', "end"),
             (f'<path d="M{lx + 8},{{y}} L{lx + 13},{{y5}} L{lx + 18},{{y}} L{lx + 13},{{y1}} Z" fill="#c2259e" '
              f'stroke="#000" stroke-width="0.6"/>', "taunt starts here"),
             (f'<line x1="{lx}" y1="{{y}}" x2="{lx + 26}" y2="{{y}}" stroke="#2f6fdf" stroke-width="1.4" '
              f'stroke-opacity="0.35" stroke-dasharray="5 3"/>', f"after {solid:.0f} s: less accurate"),
             (f'<line x1="{lx}" y1="{{y}}" x2="{lx + 100 * scale:.1f}" y2="{{y}}" stroke="#000" stroke-width="2"/>', "10 cm")]
    for i, (shape, text) in enumerate(items):
        yy = ly + 10 + i * 22
        o.append(shape.format(y=yy - 4, y4=yy - 8, y5=yy - 9, y1=yy + 1) +
                 f'<text x="{lx + 34 + (8 if i == 4 else 0)}" y="{yy}" font-size="12">{text}</text>')
    notes = ["Axes in cm. Bumps and rounding add up,", f"so after {solid:.0f} s the drawn path may be",
             "off by 10-30 cm.", "", f"Robot model: {k} mm/s per speed unit,", f"{wheels} mm between the wheels."]
    for i, text in enumerate(notes):
        o.append(f'<text x="{lx}" y="{ly + 10 + len(items) * 22 + 20 + i * 16}" font-size="11" fill="#555">{text}</text>')
    o.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def _polyline(points, key, P, by_state):
    color, solid = key
    style = 'stroke-width="1.8"' if solid else 'stroke-width="1.4" stroke-opacity="0.35" stroke-dasharray="5 3"'
    if not by_state and solid:
        style = 'stroke-width="1.4"'
    pts = " ".join("%.1f,%.1f" % P(x, y) for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" {style} stroke-linejoin="round"/>'
