#!/usr/bin/env python3
"""Inspect Thymio II's direct USB Aseba replies, without Thymio Suite.

Connect Thymio's micro-USB port to this computer. This tool only sends
read-only LIST_NODES, GET_NODE_DESCRIPTION, and GET_VARIABLES requests.
Use --raw to show each complete packet as hexadecimal bytes.
"""

import argparse
import struct
import sys
import time

import serial
from serial.tools import list_ports


ID_DESCRIPTION = 0x9000
ID_NAMED_VARIABLE_DESCRIPTION = 0x9001
ID_VARIABLES = 0x9005
ID_NODE_PRESENT = 0x900C
ID_GET_VARIABLES = 0xA00B
ID_GET_NODE_DESCRIPTION = 0xA010
ID_LIST_NODES = 0xA011
NAMES = {
    ID_DESCRIPTION: "DESCRIPTION",
    ID_NAMED_VARIABLE_DESCRIPTION: "NAMED_VARIABLE_DESCRIPTION",
    ID_VARIABLES: "VARIABLES",
    ID_NODE_PRESENT: "NODE_PRESENT",
}


def find_port():
    matches = [port for port in list_ports.comports()
               if port.vid == 0x0617 and port.pid == 0x000A]
    if len(matches) == 1:
        return matches[0].device
    if not matches:
        available = ", ".join(port.device for port in list_ports.comports())
        raise SystemExit("Thymio USB port not found. Connect its micro-USB cable "
                         f"to this computer. Available ports: {available or '(none)'}")
    raise SystemExit("Several Thymio USB ports found: "
                     + ", ".join(port.device for port in matches)
                     + ". Use --port to select one.")


def send(port, message_id, *words, raw=False):
    payload = struct.pack("<" + "H" * len(words), *words)
    packet = struct.pack("<HHH", len(payload), 1, message_id) + payload
    written = port.write(packet)
    port.flush()
    if written != len(packet):
        raise IOError(f"USB write was incomplete: {written}/{len(packet)} bytes")
    if raw:
        print(f"TX {message_id:04x} {packet.hex(' ')}", flush=True)


def read_exact(port, length, deadline):
    data = bytearray()
    while len(data) < length and time.monotonic() < deadline:
        data.extend(port.read(length - len(data)))
    return bytes(data)


def read_packet(port, deadline):
    header = read_exact(port, 2, deadline)
    if len(header) != 2:
        return None
    payload_length = struct.unpack("<H", header)[0]
    if payload_length > 1024:
        raise IOError(f"Unexpected payload length {payload_length}; USB stream is out of sync")
    remainder = read_exact(port, payload_length + 4, deadline)
    if len(remainder) != payload_length + 4:
        raise IOError(f"Incomplete Aseba packet: {len(remainder)}/{payload_length + 4} bytes")
    source, message_id = struct.unpack_from("<HH", remainder)
    return source, message_id, remainder[4:], header + remainder


def run(port_name, seconds, raw):
    print(f"Opening {port_name}; Thymio replies to Aseba requests (it does not send text).")
    with serial.Serial(port_name, 115200, timeout=0.1, write_timeout=1) as port:
        deadline = time.monotonic() + seconds
        last_discovery = 0.0
        last_poll = 0.0
        node_id = None
        expected_variables = None
        variables = {}
        next_offset = 0
        frames_received = 0
        while time.monotonic() < deadline:
            now = time.monotonic()
            if node_id is None and now - last_discovery >= 1.0:
                send(port, ID_LIST_NODES, 5, raw=raw)
                last_discovery = now
            if expected_variables is not None and len(variables) >= expected_variables:
                if now - last_poll >= 0.5:
                    for name, wanted in (("state", 1), ("prox.horizontal", 3)):
                        if name in variables:
                            offset, size = variables[name]
                            send(port, ID_GET_VARIABLES, node_id, offset,
                                 min(size, wanted), raw=raw)
                    last_poll = now

            packet = read_packet(port, min(deadline, time.monotonic() + 0.2))
            if packet is None:
                continue
            source, message_id, payload, wire_bytes = packet
            frames_received += 1
            if raw:
                print(f"RX {NAMES.get(message_id, hex(message_id))} "
                      f"source={source} {wire_bytes.hex(' ')}", flush=True)

            if message_id == ID_NODE_PRESENT and len(payload) >= 2:
                version = struct.unpack_from("<H", payload)[0]
                if node_id != source:
                    node_id = source
                    print(f"NODE_PRESENT: node={node_id}, protocol={version}", flush=True)
                    send(port, ID_GET_NODE_DESCRIPTION, node_id, 5, raw=raw)
            elif message_id == ID_DESCRIPTION and source == node_id and payload:
                name_length = payload[0]
                if len(payload) < 1 + name_length + 14:
                    print("Short DESCRIPTION packet", flush=True)
                    continue
                name = payload[1:1 + name_length].decode("utf-8", errors="replace")
                fields = struct.unpack_from("<7H", payload, 1 + name_length)
                expected_variables = fields[4]
                variables.clear()
                next_offset = 0
                print(f"DESCRIPTION: {name!r}, {expected_variables} variables", flush=True)
            elif (message_id == ID_NAMED_VARIABLE_DESCRIPTION and
                  source == node_id and expected_variables is not None and
                  len(variables) < expected_variables and len(payload) >= 3):
                size = struct.unpack_from("<H", payload)[0]
                name_length = payload[2]
                if len(payload) < 3 + name_length:
                    print("Short variable description packet", flush=True)
                    continue
                name = payload[3:3 + name_length].decode("utf-8", errors="replace")
                variables[name] = (next_offset, size)
                next_offset += size
                if name in ("state", "prox.horizontal"):
                    print(f"VARIABLE: {name}, offset={variables[name][0]}, size={size}",
                          flush=True)
                if len(variables) == expected_variables:
                    print(f"Variable list complete. state present: {'state' in variables}",
                          flush=True)
                    if "state" not in variables:
                        print("Thymio has no program variable named 'state' loaded.",
                              flush=True)
            elif message_id == ID_VARIABLES and source == node_id and len(payload) >= 4:
                offset = struct.unpack_from("<H", payload)[0]
                count = (len(payload) - 2) // 2
                values = struct.unpack_from("<" + "h" * count, payload, 2)
                for name in ("state", "prox.horizontal"):
                    if name in variables and variables[name][0] == offset:
                        if name == "state":
                            print(f"READ state={values[0]}", flush=True)
                        elif len(values) >= 3:
                            print(f"READ prox.horizontal[2]={values[2]}", flush=True)

        if frames_received == 0:
            print("No Aseba replies received. Check that Thymio is on and "
                  "Thymio Suite/Aseba Studio is not using this port.")
        elif node_id is None:
            print(f"Received {frames_received} packet(s), but no NODE_PRESENT reply. "
                  "Run again with --raw to inspect them.")
        elif expected_variables is None:
            print("Node appeared, but no DESCRIPTION arrived. Run again with --raw.")
        elif len(variables) < expected_variables:
            print(f"Only {len(variables)}/{expected_variables} variable descriptions arrived. "
                  "Run again with --seconds 20 --raw.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Thymio serial port; auto-detected by USB ID otherwise")
    parser.add_argument("--seconds", type=float, default=8,
                        help="How long to listen (default: 8)")
    parser.add_argument("--raw", action="store_true",
                        help="Print all request/reply bytes as hexadecimal")
    args = parser.parse_args()
    try:
        run(args.port or find_port(), args.seconds, args.raw)
    except (serial.SerialException, IOError) as error:
        print(f"USB probe error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
