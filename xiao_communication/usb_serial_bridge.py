#!/usr/bin/env python3
"""Forward Thymio's state and front sensor to a XIAO over USB serial.

Each line is ``state,front_sensor``. State is -1 until an Aseba program
declaring a variable named ``state`` is loaded on the Thymio.
"""

import argparse
import itertools
import os
import sys
import time

import serial
from serial.tools import list_ports
from thymiodirect import Thymio


def usb_port(vid, pid, label):
    matches = [p.device for p in list_ports.comports()
               if p.vid == vid and p.pid == pid]
    if len(matches) != 1:
        raise SystemExit(
            f"Expected one {label} USB port, found {matches}. "
            f"Pass --{label.lower()}-port explicitly."
        )
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thymio-port", help="Thymio USB serial port")
    parser.add_argument("--xiao-port", help="XIAO USB serial port")
    parser.add_argument("--count", type=int, default=0,
                        help="Stop after this many messages; 0 runs until Control-C")
    args = parser.parse_args()

    thymio_port = args.thymio_port or usb_port(0x0617, 0x000A, "Thymio")
    xiao_port = args.xiao_port or usb_port(0x303A, 0x1001, "XIAO")
    print(f"Thymio: {thymio_port}; XIAO: {xiao_port}", flush=True)

    robot = Thymio(serial_port=thymio_port)
    exit_code = 0
    try:
        robot.connect()
        node_id = robot.first_node()
        print(f"Connected to Thymio node {node_id}", flush=True)

        with serial.Serial(xiao_port, 115200, timeout=0.5) as xiao:
            time.sleep(1.5)  # The XIAO may reset when its USB port opens.
            samples = range(args.count) if args.count else itertools.count()
            for _ in samples:
                variables = robot.variables(node_id)
                state = int(robot[node_id]["state"]) if "state" in variables else -1
                front = int(robot[node_id]["prox.horizontal"][2])
                xiao.write(f"{state},{front}\n".encode("ascii"))
                reply = xiao.readline().decode("ascii", errors="replace").strip()
                print(f"state={state} front={front} XIAO={reply or '(no ACK)'}",
                      flush=True)
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print(f"Bridge error: {error}", file=sys.stderr, flush=True)
        exit_code = 1
    finally:
        # thymiodirect 0.1.2 leaves a non-daemon reader thread running. A
        # normal Python exit hangs; process exit releases both USB ports.
        os._exit(exit_code)


if __name__ == "__main__":
    main()
