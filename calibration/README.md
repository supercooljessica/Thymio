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

For the offset pen, use `offset_pen/cloud_offset_test.aesl`. Set `pen_forward_mm` and `pen_right_mm` to the tip's displacement from the axle midpoint; the defaults are 100 mm forward and 30 mm right. Set `unit_mm` for cloud size (50 mm by default, or 20 mm for the smaller cloud used by `shinchan_shy`). Place the **pen tip** at `(2*unit_mm, unit_mm)` and point the robot toward the drawing's +x direction (right). Leave room for the robot body to travel outside the drawn outline. Press center to start after a one-second delay; press it again to stop. The script updates wheel speeds every 50 ms so the pen tip follows each semicircle without an in-place pivot at the joins. It estimates heading from the commanded wheel speeds, so wheel slip, motor lag, and pen drag can still round the joins or prevent exact closure. `t90_ms` and `half_wheelbase_mm` control the assumed wheel motion; calibrate those before judging the outline.
