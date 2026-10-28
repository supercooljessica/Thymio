# Calibration sketches

Open these `.aesl` files in Aseba Studio, or load them with `./thymio.sh load calibration/<pen_folder>/<file>.aesl` from the Thymio repository root.

| Sketch | Centered pen | Offset pen | Purpose |
|---|---|---|---|
| `turn_and_shape_calibration.aesl` | Yes | — | Adjust clockwise and counterclockwise 90° turn times, try a circle, then draw a star, heart, or cloud. Its shapes assume the pen sits on the wheel axis. |
| `cloud_semicircle_test.aesl` | Yes | — | Draw six outward semicircles through six adjustable-scale points and close the outline. |
| `cloud_offset_test.aesl` | — | Yes | Draw the same cloud by commanding the offset pen tip along the arcs. The forward and right offsets are editable at the top of the sketch. |
| `circle_speed_sweep.aesl` | Yes | Yes | Draw seven circles with right speed 150 and left speeds −20 through 40; compare closure and spacing. |
| `edge_escape_test.aesl` | Yes | Yes | Test the ground-sensor edge response: backward wiggle, 180° turn, then straight shot. |
| `shy_motion_test.aesl` | Yes | Yes | Trigger the backward wiggle, 180° turn, and straight shot with the center button. |

The three shared sketches are separate copies in `centered_pen/` and `offset_pen/`, so you can tune each setup independently. The circle sweep uses the wheel-axis radius to position each successive circle. With a rigid offset pen, the pen still traces concentric circles, but their drawn radii differ from the wheel-axis radii and in-place turns leave marks.

The centered-pen turn and shape sketch does not compensate for an offset pen. Use the dedicated offset-pen cloud sketch below for this shape; the star and heart still need their own offset-pen paths.

For the dedicated cloud test, set `unit_mm` at the top of `centered_pen/cloud_semicircle_test.aesl`. The default is 50 mm per coordinate unit. Place the centered pen at `(2,1)` in that coordinate system, facing 45° northeast, then press the center button. `half_wheelbase_mm` controls the curve radius calculation; `arc_time_percent` adjusts the duration of all six arcs if they consistently stop short or run long.

For the offset pen, use `offset_pen/cloud_offset_test.aesl`. Set `pen_forward_mm` and `pen_right_mm` to the tip's displacement from the axle midpoint. **The current file says 75 mm forward and 48 mm right**; the earlier supplied estimate was 100 mm forward and 30 mm right. Confirm the actual mount before changing these values. Set `unit_mm` for cloud size (50 mm in the offset sketch). The 20 mm cloud in `shinchan_shy.aesl` still uses centered-pen math and is not linked to this sketch. Place the **pen tip** at `(2*unit_mm, unit_mm)` and point the robot toward the drawing's +x direction (right). Leave room for the robot body to travel outside the drawn outline. Press center to start after a one-second delay; press it again to stop. The script updates wheel speeds every 50 ms so the pen tip follows each semicircle without an in-place pivot at the joins. It estimates heading from the commanded wheel speeds, so wheel slip, motor lag, and pen drag can still round the joins or prevent exact closure. `t90_ms` and `half_wheelbase_mm` control the assumed wheel motion; calibrate those before judging the outline.

The 90-degree turn estimate in the newer calibration sketches is 1670 ms in each direction at motor targets -150, 150 or 150, -150. `turn_and_shape_calibration.aesl` also has `star_turn_trim_ms = 100` and currently tries a circle with outer speed 150 and inner speed 10. The circle-speed sweeps try left speeds -20 through 40 with the right speed fixed at 150. These are working settings and experiments, not a record that every shape has been verified on the physical robot.

The shy-motion and edge-escape copies currently wiggle for 25 intervals of 50 ms, then use a 1200 ms full-speed 180-degree turn and a 1000 ms straight shot. The turn time is marked as a starting estimate in the sketches. The edge test waits for 10 consecutive low ground readings on either sensor before starting the escape, so a thin drawn line should not trigger it. The copies under `offset_pen/` test the same robot motion; only `cloud_offset_test.aesl` compensates the actual pen-tip path.
