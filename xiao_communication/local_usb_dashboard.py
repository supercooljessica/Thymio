#!/usr/bin/env python3
"""Show Thymio on a local web page and forward its state to a USB-connected XIAO."""

import argparse
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import serial
from serial.tools import list_ports
from thymiodirect import Thymio


PAGE = r"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thymio live state</title>
<style>
  body { font: 16px system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; color: #17212b; }
  h1 { margin-bottom: .3rem; } .muted { color: #5c6873; }
  .card { border: 1px solid #d5dde4; border-radius: 12px; padding: 1rem; margin: 1rem 0; }
  .value { font-size: 2rem; font-weight: 700; } .row { display: flex; gap: 1rem; align-items: center; }
  .swatch { width: 2rem; height: 2rem; border: 1px solid #aab4bc; border-radius: 50%; }
  .bars { display: flex; gap: 7px; align-items: end; height: 110px; }
  .bar { flex: 1; background: #3384ca; min-height: 2px; border-radius: 4px 4px 0 0; }
  .numbers { display: flex; gap: 7px; text-align: center; font-size: .8rem; }
  .numbers span { flex: 1; }
</style>
<h1>Thymio live state</h1>
<p class="muted" id="status">Connecting…</p>
<div class="card"><div>Program state</div><div class="value" id="program-state">—</div>
<div class="muted" id="state-note"></div></div>
<div class="card"><div>Top LED</div><div class="row"><div class="swatch" id="led-swatch"></div>
<strong id="led-values">—</strong></div></div>
<div class="card"><div>Horizontal proximity sensors (raw values)</div>
<div class="bars" id="bars"></div><div class="numbers" id="numbers"></div></div>
<div class="card">Wheel speeds: <strong id="motors">—</strong></div>
<div class="card">XIAO USB link: <strong id="xiao">—</strong></div>
<script>
const bars = document.getElementById('bars');
const numbers = document.getElementById('numbers');
for (let i = 0; i < 7; i++) {
  bars.appendChild(document.createElement('div')).className = 'bar';
  numbers.appendChild(document.createElement('span')).textContent = '0';
}
async function refresh() {
  try {
    const response = await fetch('/api/state', {cache: 'no-store'});
    if (!response.ok) throw Error('HTTP ' + response.status);
    const data = await response.json();
    document.getElementById('status').textContent = 'Reading Thymio over USB · updated ' + new Date(data.updated * 1000).toLocaleTimeString();
    document.getElementById('program-state').textContent = data.state === null ? 'Unavailable' : data.state;
    document.getElementById('state-note').textContent = data.state === null
      ? 'Load and run a Thymio program that declares a variable named state to show it here.' : '';
    const led = data.led_top;
    document.getElementById('led-values').textContent = led.join(', ') + ' (R, G, B)';
    document.getElementById('led-swatch').style.backgroundColor = 'rgb(' + led.map(v => Math.round(v * 255 / 32)).join(',') + ')';
    data.proximity.forEach((v, i) => {
      bars.children[i].style.height = Math.min(100, Math.max(2, v / 4000 * 100)) + '%';
      numbers.children[i].textContent = v;
    });
    document.getElementById('motors').textContent = data.motors.join(' / ') + ' (left / right)';
    document.getElementById('xiao').textContent = data.xiao;
  } catch (error) {
    document.getElementById('status').textContent = 'Unable to read Thymio: ' + error.message;
  }
}
refresh(); setInterval(refresh, 250);
</script></html>"""


def find_usb_port(vid, pid, label, option):
    matches = [p.device for p in list_ports.comports() if p.vid == vid and p.pid == pid]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {label} USB port, found {matches}. Use {option} to select one.")
    return matches[0]


def make_handler(latest, lock):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                body = PAGE.encode("utf-8")
                content_type = "text/html; charset=utf-8"
            elif self.path == "/api/state":
                with lock:
                    data = latest.copy()
                body = json.dumps(data).encode("utf-8")
                content_type = "application/json; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thymio-port", help="Thymio USB port; normally found automatically")
    parser.add_argument("--xiao-port", help="XIAO USB port; normally found automatically")
    parser.add_argument("--dashboard-only", action="store_true", help="Show the page without forwarding to XIAO")
    parser.add_argument("--port", type=int, default=8765, help="Local web port (default: 8765)")
    args = parser.parse_args()

    try:
        thymio_port = args.thymio_port or find_usb_port(0x0617, 0x000A, "Thymio", "--thymio-port")
        xiao_port = None if args.dashboard_only else (
            args.xiao_port or find_usb_port(0x303A, 0x1001, "XIAO", "--xiao-port"))
        robot = Thymio(serial_port=thymio_port)
        robot.connect()
        node_id = robot.first_node()
        if node_id is None:
            raise RuntimeError("No Thymio was found on the USB port")
        available = set(robot.variables(node_id))
        print(f"Connected to Thymio on {thymio_port} (node {node_id})", flush=True)
        if "state" not in available:
            print("No custom state variable is loaded; built-in sensors and LEDs are available.", flush=True)

        xiao = serial.Serial(xiao_port, 115200, timeout=0.5) if xiao_port else None
        if xiao:
            time.sleep(1.5)  # Opening USB can reset the XIAO.
            xiao.reset_input_buffer()
            print(f"Forwarding state, front sensor, and LED RGB to XIAO on {xiao_port}", flush=True)

        latest = {
            "updated": time.time(),
            "state": None,
            "led_top": [0, 0, 0],
            "proximity": [0] * 7,
            "motors": [0, 0],
            "xiao": "Waiting for data" if xiao else "Disabled",
        }
        lock = threading.Lock()
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(latest, lock))
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"Open http://127.0.0.1:{args.port}/ on this computer. Press Control-C to stop.", flush=True)

        while True:
            node = robot[node_id]
            state = int(node["state"]) if "state" in available else None
            proximity = list(node["prox.horizontal"])
            led_top = list(node["leds.top"])
            xiao_status = "Disabled"
            if xiao:
                sent = ",".join(str(value) for value in (
                    state if state is not None else -1, proximity[2], *led_top))
                xiao.write((sent + "\n").encode("ascii"))
                reply = xiao.readline().decode("ascii", errors="replace").strip()
                xiao_status = "ACK " + sent if reply == "ACK," + sent else (reply or "No ACK")
            sample = {
                "updated": time.time(),
                "state": state,
                "led_top": led_top,
                "proximity": proximity,
                "motors": [int(node["motor.left.speed"]), int(node["motor.right.speed"])],
                "xiao": xiao_status,
            }
            with lock:
                latest.update(sample)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        exit_code = 0
    except Exception as error:
        print(f"Web server error: {error}", file=sys.stderr, flush=True)
        exit_code = 1
    finally:
        # thymiodirect 0.1.2 leaves a non-daemon reader thread running.
        # Process exit releases the Thymio USB port and local web socket.
        os._exit(exit_code)


if __name__ == "__main__":
    main()
