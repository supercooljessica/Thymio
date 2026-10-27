# Thymio state to XIAO over the computer

The Mac reads Thymio II over USB and forwards `state,front_sensor` lines to the
XIAO ESP32C3 over its USB serial port. The XIAO replies `ACK,state,front_sensor`.
Both connections have been tested on this Mac with the ports detected
automatically. Thymio Suite is not required for this route.

## Run

1. Connect and turn on both devices. Close Aseba Studio before starting the
   bridge: it otherwise holds Thymio's serial port.
2. From the Thymio repository root, run:

   ```sh
   .venv/bin/python -u xiao_communication/usb_serial_bridge.py
   ```

   Stop with Control-C. Use `--count 5` for a short test.
3. Look for lines such as `state=2 front=1500 XIAO=ACK,2,1500`.

`state=-1` means the robot has no Aseba program with a variable named `state`
loaded. The front sensor value is still sent. For a safe first state test,
load and run `xiao_communication/thymio_state_button_test.aesl` in Aseba Studio. The forward button sets
state 2 and a green top light; the backward button sets state 1 and blue.
Quit Studio, then run the bridge and press those buttons to check the readings.

`shinchan_bot.aesl` in the repository root also declares
`state` (1=SEARCH, 2=PURSUE, 3=BORED, 4=AVOID, 5=TAUNT, 6=RECOVER).
Load and run that program in Aseba Studio only when the robot has a safe area to
move, then close Studio so the bridge can use the USB port. If the program stops
or the robot resets when Studio closes, use Thymio's permanent-program feature
or a Thymio Device Manager based bridge instead.

The XIAO receiver source is `xiao_communication/xiao_c3_usb_serial_receiver/xiao_c3_usb_serial_receiver.ino`. It stores
the latest values in `thymioState` and `frontSensor`; `connected` becomes false
when updates stop for one second. The previously staged Wi-Fi web sketch remains
in `xiao_communication/xiao_c3_wifi_proximity/` and can be uploaded again to restore that behavior.
