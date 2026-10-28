"""Bridge Thymio proximity samples from Thymio Suite to the XIAO access point."""

import argparse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from tdmclient import ClientAsync


SOURCE = Path(__file__).with_name("thymio_proximity_reader.aesl")


def aseba_source():
    node = ET.parse(SOURCE).find("./node")
    if node is None or not node.text:
        raise RuntimeError(f"No Aseba program found in {SOURCE}")
    return node.text.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://192.168.4.1/update",
                        help="XIAO update URL (default: %(default)s)")
    args = parser.parse_args()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    with ClientAsync() as client:
        async def bridge():
            with await client.lock() as node:
                error = await node.compile(aseba_source())
                if error is not None:
                    raise RuntimeError(f"Aseba compile failed: {error}")
                error = await node.run()
                if error is not None:
                    raise RuntimeError(f"Could not start Thymio program: {error}")

                latest = None

                def on_change(changed_node, variables):
                    nonlocal latest
                    if "sample" in variables:
                        latest = list(variables["sample"])

                node.add_variables_changed_listener(on_change)
                await node.watch(variables=True)
                print(f"Forwarding Thymio proximity readings to {args.url}")

                while True:
                    await client.sleep(0.1)
                    if latest is None:
                        continue
                    values, latest = latest, None
                    if len(values) != 7:
                        continue
                    payload = ",".join(str(int(value)) for value in values).encode("ascii")
                    request = urllib.request.Request(
                        args.url, data=payload,
                        headers={"Content-Type": "text/plain"}, method="POST")
                    try:
                        with opener.open(request, timeout=1) as response:
                            response.read()
                    except OSError as exc:
                        print(f"XIAO unreachable: {exc}")

        client.run_async_program(bridge)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
