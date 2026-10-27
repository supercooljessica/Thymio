# Thymio proximity readings on a XIAO ESP32C3

This first version uses a Mac as the USB-to-Wi-Fi bridge:

`Thymio II --USB--> Mac --XIAO's Wi-Fi hotspot--> XIAO web server --> browser`

No existing Wi-Fi network or Internet connection is needed while it runs. The XIAO creates its own local Wi-Fi network. A Thymio II USB connection cannot be wired directly to the XIAO's D6/D7 UART pins; those pins do not act as a USB host or decode Thymio's Aseba protocol.

## Set up

1. Attach the XIAO ESP32C3 antenna, then connect the XIAO to USB power. In Arduino IDE, install the `esp32` board package, select `XIAO_ESP32C3` and its port, and upload `xiao_communication/xiao_c3_wifi_proximity/xiao_c3_wifi_proximity.ino`.
2. Connect the Thymio II to the Mac with its USB cable. Install and start Thymio Suite so its Thymio Device Manager (TDM) can see the robot. This bridge uses TDM; the older standalone Aseba installation alone is insufficient. Do not leave the robot locked in Aseba Studio; close Studio or unlock it before starting the bridge.
3. Install the Python client while you still have Internet access: `python3 -m pip install tdmclient`.
4. Join the Mac to the XIAO Wi-Fi network `Thymio-XIAO` with password `thymio123`. It is normal for macOS to say this network has no Internet.
5. Check the XIAO alone: open `http://192.168.4.1/`, then run `curl -H 'Content-Type: text/plain' --data-binary '1,2,3,4,5,6,7' http://192.168.4.1/update` in a Mac terminal. The seven test numbers should appear on the page.
6. From the Thymio repository root, run `python3 xiao_communication/wifi_proximity_bridge.py`. The bridge compiles and starts `thymio_proximity_reader.aesl` on Thymio, watches its `sample` array, and sends readings to the XIAO. This replaces any currently running Aseba program, including `thymio_hunter.aesl`.
7. Move a hand near the sensors and watch the seven values change. Front sensors are indexes 0–4 from left to right; rear sensors are 5–6.

If the page says "Waiting for data", check that Thymio Suite sees the robot, Studio has released the lock, the Mac is connected to `Thymio-XIAO`, and `python3 xiao_communication/wifi_proximity_bridge.py` is still running. Stop the bridge with Control-C. The readings are raw IR values, not distances in millimetres.

For a fully self-contained Thymio-to-XIAO connection later, you would need additional hardware and software, such as a USB host interface that understands Thymio's Aseba USB protocol. The XIAO ESP32C3 alone does not provide that link.

This Mac currently has Arduino IDE and standalone Aseba installed, but I did not find Thymio Suite or `tdmclient`. The official Thymio Suite download page lists macOS support only through macOS 12, so its behavior on this Mac's macOS 15.6.1 still needs to be checked.
