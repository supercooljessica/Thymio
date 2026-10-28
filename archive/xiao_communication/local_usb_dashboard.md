# Thymio dashboard without Wi-Fi

This page runs on your computer. Thymio and the XIAO connect to the computer by USB, and the browser opens `http://127.0.0.1:8765/`. The address works only on this computer and does not use Wi-Fi. One command reads Thymio, forwards `state,front_sensor,red,green,blue` to the XIAO, and shows the readings and XIAO acknowledgement in the browser.

## Start it on this Mac

1. Keep Thymio and the XIAO connected by USB. Quit Aseba Studio and close Arduino IDE's Serial Monitor so the dashboard can use both USB ports. The XIAO already has the USB receiver sketch loaded.
2. In Terminal, run:

   ```sh
   cd /Users/jessicalee/Documents/cs-workspaces/Thymio
   .venv/bin/python -u xiao_communication/local_usb_dashboard.py
   ```

3. Open [the local dashboard](http://127.0.0.1:8765/) in a browser. Press Control-C in Terminal to stop it.

The page shows the built-in top LED, horizontal proximity sensors, wheel speeds, and the XIAO's last acknowledgement. The XIAO stores the digital top LED values in `topRed`, `topGreen`, and `topBlue`; no color sensor is needed. The page shows the program's `state` value only when the loaded Thymio program defines that variable. If it says **Unavailable**, the XIAO receives `-1` for state while still receiving the LED values. Load and run a suitable program in Aseba Studio, then quit Studio and restart the dashboard. The included `thymio_state_button_test.aesl` is a simple test program.

The dashboard uses USB serial behind the scenes because the ESP32-C3's built-in USB connection is a serial/JTAG device, not a network adapter. The web server gives you a simple local page and one command to run both connections; the XIAO still receives data without Wi-Fi.

To view Thymio without the XIAO, add `--dashboard-only` to the command.
