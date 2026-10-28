# Thymio collaboration handoff

Updated 2026-10-28. Read the source file before changing a behavior: the values below describe the current checkout and the observations reported so far. A saved parameter is not proof that the physical robot draws that path accurately.

## Which program to continue

| Goal | Source of truth | Current behavior |
|---|---|---|
| Hunter Shin-chan | [`../shinchan_bot.aesl`](../shinchan_bot.aesl) | Search, pursue, taunt, avoid, and draw underpants when bored, with the pen 45 mm straight behind the centre hole (pen-tip steering). |
| Shy Shin-chan | [`../shinchan_shy.aesl`](../shinchan_shy.aesl) | Explore open space for 8 seconds, draw a small cloud with the pen behind the robot (pen-tip steering), maneuver around slow front obstacles, and use 180°/0°/90° escape variations for first front, rear, and blocked front hazards. |
| Submission version | [`../shinchan_submit.aesl`](../shinchan_submit.aesl) | WANDER and SHIVER names; draws the pen-behind cloud and underpants in turn (`drawing_steps`, `next_drawing`); 180° turn for the first front escape, no turn for a rear escape, and repeating 90° turns after a blocked front escape. |
| Centered-pen drawing tests | [`../calibration/centered_pen/`](../calibration/centered_pen/) | Turn and shape calibration, cloud semicircles, circle sweep, shy motion, and edge escape. |
| Offset-pen cloud | [`../calibration/offset_pen/cloud_offset_test.aesl`](../calibration/offset_pen/cloud_offset_test.aesl) | Standalone six-lobe cloud that commands the pen tip along the intended arcs. It does not explore or avoid obstacles. |
| XIAO communication | [`../archive/xiao_communication/README.md`](../archive/xiao_communication/README.md) | Archived: separate USB, local dashboard, Wi-Fi, and direct USB host experiments. These are not part of the drawing controller. |

The detailed behavior flow is in [`logic.md`](logic.md). The calibration file index and setup instructions are in [`../calibration/README.md`](../calibration/README.md).

## Calibration and motion values in the current files

| Item | Current value or observation | Where to edit or verify |
|---|---|---|
| 90-degree spin at `-150, 150` and `150, -150` | The user's working estimate is about **1670 ms in both directions**. | `t90_ccw` / `t90_cw` in the centered-pen tests and shy bot; `t90_ms` in the offset cloud. |
| Star overrotation correction | `star_turn_trim_ms = 100` subtracts time from the nominal 144-degree turn. | `calibration/centered_pen/turn_and_shape_calibration.aesl` |
| Straight travel estimate | `cm = 167` ms per cm at `150, 150` in the older centered-pen tests. | Turn/shape calibration and circle sweeps; test on the actual surface. |
| Circle experiment | Outer motor target 150; inner 10 in the turn/shape trial. The user observed that 150/50 stopped short while 150/10 came nearer the start. The sweep tries inner targets -20, -10, 0, 10, 20, 30, 40. | `circle_inner_speed`, `circle_outer_speed`, `circle_time_percent`; `calibration/*/circle_speed_sweep.aesl` |
| Edge detection | A low `prox.ground.delta` reading is at or below `white_min = 500`. Ten consecutive low samples on either sensor confirm an edge in normal motion. | `edge_escape_test.aesl` and `shinchan_shy.aesl`; the shy bot also uses two low samples to stop a fast escape. |
| Escape | 25 wiggle intervals × 50 ms at nominal 300 with 300 swerve, then a 1000 ms forward shot. The first front escape turns 180° for 1200 ms, rear escape skips the turn, and blocked front retries turn 90° for 600 ms. | `shinchan_shy.aesl` and `shinchan_submit.aesl`. The full-speed turn timings are starting estimates. |

The shy bot's front and rear proximity thresholds are raw IR values, not millimetres: moderate at 1500, hard at 3000, clear below 900. A fast approach is inferred from a rise in readings across roughly three sensor updates, with two consecutive rises needed. This is a cue for whether to maneuver or escape, not a measured relative speed. The maneuver timeout is 30 ticks of timer 0 (3 seconds). Review the current source before tuning thresholds.

In the circle tests, `circle_speed_gap` means `outer_speed - inner_speed`. The programmed quarter-circle duration is approximately `t90_ccw * 300 / circle_speed_gap`, multiplied by `circle_time_percent / 100` in the sweep. If a circle stops short at a chosen pair of motor speeds, `circle_time_percent` is the direct duration adjustment; changing the inner speed changes the physical radius and turn rate as well.

## Offset pen geometry and status

**Current setup (2026-10-28):** the pen sits in a printed sleeve (`cad/`) **45 mm straight behind the centre hole, 1 mm left**, sliding freely and touching the paper by its own weight. `shinchan_bot.aesl`, `shinchan_shy.aesl` and `shinchan_submit.aesl` draw with it by steering the pen tip every 50 ms, with the method and numbers of `shinchan_shapes_offset.aesl`: `kc`/`pen_speed` 900, `kb`/`pen_side` -20, `kw`/`pen_turn` -953, heading update `(r - l) * 86 / 49`, tables built for 0.321 mm per wheel unit per second and W 95.3 mm. These were measured on the real robot with a spin test and photographed drawings; see [`calibration.md`](calibration.md) for the whole history. Lines and steady circles come out within a few millimetres; corners can be off by up to about 15° because the body keeps swinging for about 11 cm after each corner. The robot also has two pen-test programs: `shinchan_shapes_offset.aesl` (underpants, cloud, star) and `shinchan_calibrate_offset.aesl` (line, squares, circles).

The rest of this section describes the earlier offset-pen cloud test:

The pen is rigidly ahead of and to the right of the wheel axle midpoint. The initial estimate supplied in conversation was **100 mm forward, 30 mm right**. The current `cloud_offset_test.aesl` has since been edited to **75 mm forward, 48 mm right**. Those file values are the ones that will run now; confirm them against the mount before interpreting a drawing. `unit_mm = 50`, `pen_speed_target = 120`, `half_wheelbase_mm = 50`, and `t90_ms = 1670` are also currently in that file.

The intended pen path visits `(2,1) → (1,2) → (-1,2) → (-3,1) → (-1,-1) → (1,-1) → (2,1)`, scaled by `unit_mm`, using outward semicircles. Put the **pen tip** at the first point and point the robot toward the drawing's +x direction. Leave enough space for the robot body beyond the outline. The center button starts after a one-second delay and stops an active drawing.

For forward offset `f` and right offset `r`, if the axle moves forward at `v` and rotates counterclockwise at `w`, the pen-tip velocity is `(v + r*w)` forward and `f*w` to the left. The offset cloud solves this for wheel commands every 50 ms and tracks heading from those commands. It changes velocity at lobe joins without an in-place pivot. This is open-loop: the script does not measure its actual heading or pen trace. Motor lag, slip, and pen drag can distort the joins and closure. Red means invalid settings or a command outside the script's permitted range; green means the sequence finished.

**Integration:** done on 2026-10-28 for the pen 45 mm straight behind the centre hole: `shinchan_shy.aesl` draws the cloud in `sub cloud_step` (timer 1 at 50 ms, table `cloud_steps`), `shinchan_submit.aesl` alternates cloud and underpants in `sub drawing_step` (table `drawing_steps`), and `shinchan_bot.aesl` draws its underpants the same way. A hazard during the cloud still interrupts it as before. `shinchan_drawings.aesl` still assumes a centered pen.

The submission version starts a drawing after eight seconds of wandering with a clear path: the six-arc cloud, then the underpants next time, and so on. Timer 1 steps the pen-tip steering every 50 ms, with a 0.3 s stop between arcs; a hazard interrupts and abandons the current cloud. A later draw restarts at the first arc. `front_history[3]`, `rear_history[3]`, and `ground_low[2]` group repeated sensor values; tuning parameters remain individually named.

In both shy programs, orange is a brief blocked phase between escape attempts. If front IR remains above 900 (`front_clear` in shy; `clear_threshold` in submit) or a ground edge is detected, and rear IR is below 1500 (`rear_threshold` in shy; `obstacle_threshold` in submit), another backward wiggle or SHIVER starts, followed by a 90° turn toward the less occupied front side and a forward shot. There is no retry limit. The first front escape from EXPLORE/WANDER or DRAW uses `turn_180_ms = 1200` at motor targets `500, -500`; blocked retries use `turn_90_ms = 600` at motor targets `±500`. Rear escapes have no turn. Both timings need physical calibration. If the rear is also occupied, the robot stays stopped until it can retreat safely.

The submit file now shares its front/rear hard and clear thresholds, and one `clear_samples` counter serves both maneuver and blocked phases. Its shiver uses a single speed setting and sends target 600 to one wheel at a time without an explicit 500 clamp. `left_space` and `right_space` also serve as temporary outputs for `math.stat` before either is used to steer. The separate shy file retains its own threshold names and explicit motor clipping.

## What has and has not been checked

- The user reported the 1670 ms turn estimate, the roughly 100 ms star trim, and the circle behavior above from physical trials. Treat the exact numbers as surface- and robot-dependent.
- The offset cloud was previously checked with XML/structural inspection and an ideal differential-drive simulation at the **earlier 100/30 estimate**. That model result does not validate the current 75/48 settings or the physical drawing.
- There is no recorded physical accuracy result for `cloud_offset_test.aesl`, and no recorded robot test of an offset-pen shy bot because that integration has not been done.
- This documentation update did not compile, load, or drive a robot.
- The XIAO guides describe separate communication tests; their success does not establish drawing accuracy.

## Good next steps

1. Run `shinchan_submit.aesl` and `shinchan_shy.aesl` on paper with the pen sleeve fitted, including a hazard during a cloud, and check that the avoid transition still works while drawing.
2. If the pen sleeve is moved, measure the pen tip from the centre hole and recompute `kb`/`pen_side` and `kw`/`pen_turn` (formulas in the README); a spin on the spot drawing an arc gives the distance directly.
3. `shinchan_drawings.aesl` (spiral, flower) still assumes a centered pen; port it only if it is needed with the pen behind.
4. Corners stay up to about 15° off with the pen 45 mm behind the axle; a pen on the wheel axis (the centre hole) would remove that if the hole becomes free.

## Aseba editing notes

Aseba `sub` routines have no arguments or return values in these sketches; they share declared global variables. `onevent prox`, `onevent timer0`, and `onevent timer1` keep motions nonblocking by advancing phases on events. `timer.period[0]` and `[1]` are timer intervals in milliseconds; setting one to zero stops that timer. Do not name a variable `step` in this project; use `step_size`, `shiver_index`, or another descriptive name. Motor targets stay within -500 to 500. Preserve each `.aesl` file's XML format, including escaped comparison signs where a file uses text inside `<node>` rather than CDATA.
