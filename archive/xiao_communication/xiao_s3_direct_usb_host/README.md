# Thymio to XIAO ESP32-S3, directly over USB

The XIAO acts as a USB host. The powered QGeeM hub sits between the XIAO and Thymio. No computer or Wi-Fi is needed after the sketch and Thymio program are loaded.

## Load the XIAO sketch

1. Disconnect the QGeeM hub from the XIAO and connect the XIAO to the computer for programming.
2. Open `xiao_s3_direct_usb_host.ino` in Arduino IDE and select **XIAO ESP32S3**.
3. Set **Tools → USB Mode → USB-OTG (TinyUSB)** and **Tools → USB CDC On Boot → Disabled**.
4. Upload the sketch. Then disconnect the computer cable.
5. Reconnect the XIAO to the QGeeM hub, keep the hub's wall power connected, and connect Thymio's micro-USB cable to a USB-A port on the hub. Turn Thymio on.

## Read the XIAO LED

The XIAO's user LED is active LOW and its pattern now reports the data connection:

| Pattern | Meaning |
| --- | --- |
| One short blink each second | Thymio USB has not mounted. |
| Rapid, continuous blinks | USB mounted, but the XIAO has not received a fresh valid `state` value. |
| One to six short blinks, followed by a pause | Thymio sent `state` 1 to 6. |

The sketch discovers Thymio's Aseba node, asks for its variable descriptions, and polls `state` and `prox.horizontal` every 250 ms. The latest values are stored in the sketch variables `thymioState` and `frontProximity` (`prox.horizontal[2]`). Put any XIAO behavior that depends on them in `loop()`, after the USB read. Check `millis() - lastStateAt < 1500` before acting on `thymioState`.

Thymio must be running an Aseba program that declares `var state`. For a stationary button test, load and run [`../thymio_state_button_test.aesl`](../thymio_state_button_test.aesl) on Thymio: the forward button sets state 2 and the backward button sets state 1. The full [`../../shinchan_bot.aesl`](../../shinchan_bot.aesl) program also has a `state` variable with values 1–6. If you need the program to survive switching off Thymio, use Aseba Studio's **Tools → Write program(s) → inside Thymio II** while Thymio is connected to the computer, then reconnect it to the hub.

The steady LED in the earlier mount-only sketch confirmed USB enumeration. This sketch replaces that sketch and tests whether application data actually reaches the XIAO.

## If the LED keeps blinking rapidly

Temporarily move Thymio's **micro-USB cable** from the hub to the computer, turn Thymio on, and quit Aseba Studio/Thymio Suite so they do not hold the port. From this folder run:

```sh
../../.venv/bin/python ../thymio_usb_probe.py --seconds 8
```

`NODE_PRESENT` and `DESCRIPTION` show that Thymio is answering USB requests. `VARIABLE: state` and repeated `READ state=...` lines show that the intended program is running and the value can be read. `READ prox.horizontal[2]=...` confirms sensor replies even if `state` is absent. Add `--raw` to print the exact transmitted and received Aseba bytes. Reconnect Thymio to the powered hub after this check.
