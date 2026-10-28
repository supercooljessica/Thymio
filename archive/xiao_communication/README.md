> **Archived (2026-10-27).** The team no longer connects the Thymio to an Arduino/XIAO. These scripts need `pip install pyserial==3.5 thymiodirect==0.1.2`, which were removed from the main `requirements.txt`. Paths in these guides still say `xiao_communication/`; read them as `archive/xiao_communication/`.

# XIAO and USB communication

This folder collects the XIAO firmware and the Thymio-to-XIAO communication experiments. Run the Python commands in the linked guides from the Thymio repository root unless a guide says otherwise. The shared Python dependencies are in `../requirements.txt`.

| Guide | What it runs |
|---|---|
| [Local USB dashboard](local_usb_dashboard.md) | `local_usb_dashboard.py` reads Thymio and forwards state, sensor, and LED data over USB serial to `xiao_c3_usb_serial_receiver/`. |
| [USB serial bridge](usb_serial_bridge.md) | `usb_serial_bridge.py` sends Thymio state and front sensor values to the XIAO over USB serial. |
| [Wi-Fi proximity bridge](wifi_proximity_bridge.md) | `wifi_proximity_bridge.py` loads `thymio_proximity_reader.aesl` and relays readings to `xiao_c3_wifi_proximity/` via the XIAO hotspot. |
| [Direct USB host](xiao_s3_direct_usb_host/README.md) | `xiao_s3_direct_usb_host/` connects a XIAO ESP32-S3 directly to Thymio through a powered USB hub. |

`thymio_state_button_test.aesl` is a stationary state test for the bridges. `thymio_usb_probe.py` checks Thymio's direct USB/Aseba responses. Each Arduino sketch directory contains an `.ino` file with the same name as the directory so it opens normally in Arduino IDE.
