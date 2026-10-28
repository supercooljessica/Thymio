# Calibrating the real robot

## Why the real robot draws differently from the simulator

Every drawing is **timed**. The program says "drive at 150 for 2 s, then spin for 1.244 s" and hopes the robot ends up where the maths says. Nothing checks where it actually went. So the shape is only right if the robot moves exactly as fast as the program assumes.

- **The timings were never measured on a real robot.** `t90 = 1244` and `cm = 167` are the textbook values for a Thymio that moves 0.4 mm/s per speed unit with 95 mm between the wheels.
- **The simulator is about 17 % slower than that** (0.332 mm/s per unit). That's why the simulator needs `t90=1482 cm=201`. A 17 % speed difference turns every 90° corner into about 75° or 108°, so a shape that looks right in one world comes out wrong in the other. Real robots also differ from each other.
- **The simulator is perfect, and a real robot isn't:**
  - Simulated wheels reach their speed instantly. Real motors take a moment to speed up and slow down, so every start, stop and change of direction loses a little distance or angle.
  - Real tyres scrub when the robot spins on the spot, so spins lose more than straight driving does.
  - The two real motors are never identical, so straight lines curve slightly and left turns differ from right turns.
  - Slow wheel speeds are the least accurate. The flower holds one wheel at 0, and the shy bot's cloud runs the inner wheel backwards at −42 to −84.
  - The pen rubs on the paper, and the wheels can slip.
- **The errors add up.** The underpants take 12 timed moves, the flower 20 and the cloud 11. A few degrees off at each turn gives a shape that doesn't close.

You can't make the simulator match the real robot exactly. What fixes it is measuring the real robot and putting those numbers into the programs.

## Results on our robot (2026-10-27, first run, with `cm=167 t90=1244`)

| Test | Measured | Meaning |
|---|---|---|
| T1 | 2.0, 4.5, 9.2 cm at speed 150 (0.5, 1, 2 s); 8.8 cm at speed 300 (1 s) | 47.8 mm/s at speed 150, so **0.318 mm/s per unit**: 20 % slower than the code assumed (0.4) and 4 % slower than the simulator (0.332). About 3.5 mm lost at each start. Speed 300 behaves the same. The line is straight, so the two motors match. |
| T2 | Right corners 69°, 68°, 68°; left corners 69°, 68°, 71° | A 90° spin needs 1244 × 90 ÷ 69 ≈ **1620 ms**, the same for both directions |
| T3 | Loops turned about 284°, 274° and 248° instead of 360° | Curves are short by the same factor as spins, so one `t90` fits spins and petals. Exception: a wheel at +50 runs relatively too fast, so the widest loop was short by more. |

### Check run (same day, with `cm=209 t90=1620`), measured from photos with a ruler

| Test | Measured | Meaning |
|---|---|---|
| T2 | Corners 90.4°, 90.6°, 90.7° (right) and 89.2°, 90.9°, 89.6° (left). The second square closes 0.6 mm from the start. Sides average 117.3 mm instead of 120. | `t90 = 1620` is right. `cm` goes up 2.3 % to **214**. |
| T3 | Loops turned 363.5° (wheels −50/150, like the cloud), 361.7° (0/150, like the flower petals) and 319.5° (+50/150) | Spins, petals and cloud arcs all match one `t90`. A wheel at +50 runs like +61, so avoid slow forward inner wheels in drawings. |
| T3 | Circle diameters: 45.1, 94.3 and 226 mm | The pivot circle's diameter is the wheel spacing: **94.3 mm**, so `half_wheelbase_mm = 47`. A wheel at −50 runs like −53, close enough. |

Final values:

| Program | Values |
|---|---|
| `shinchan_drawings.aesl`, `shinchan_bot.aesl` | `t90 = 1620`, `cm = 214` |
| `shinchan_shy.aesl`, `shinchan_submit.aesl` | `t90_ccw = t90_cw = 1620`, `half_wheelbase_mm = 47` |
| `shinchan_calibrate.aesl` | `t90r = t90l = 1620`, `cm = 214` |

The photos were measured with pixel line and circle fits against the ruler's inch ticks, accurate to about ±1° and ±1 mm.

## The test program (`shinchan_calibrate.aesl`)

Pen in the **centre hole**. The line is the path of the robot's centre.

| Button | Test | Draws | Takes |
|---|---|---|---|
| Forward | T1 line | One straight line: 3, 6 and 12 cm at speed 150, then 12 cm at speed 300, with a 2 s stop (an ink dot) between parts. Reading from the start, the parts are short, medium, long, long. | 11 s |
| Left | T2 squares | Two 12 cm squares touching at the start: the first with right turns, the second with left turns, joined by one 24 cm straight line | 24 s |
| Right | T3 loops | A straight line with three loops hanging off its left side: 4.8, 9.5 and 19 cm wide | 39 s |
| Centre | Stop | | |

The test starts 2 s after you let go of the button. The top LED is green, blue or purple while a test runs, and goes off when it's done.

This is what a perfect robot draws: [`calibration_expected.svg`](calibration_expected.svg), to scale.

## Run it

1. **Paper:** use one big sheet, or A4 sheets taped together with flat seams, on the same surface you will draw on later. The robot body sticks out about 6 cm around the pen, so leave 8 cm of paper around the drawing:
   - **T1:** 50 × 20 cm. Start 8 cm from one short edge, facing along the sheet.
   - **T2:** 40 × 40 cm. Start in the middle, facing the top edge. The squares go up-right and down-left.
   - **T3:** 40 wide × 55 cm tall. Start 8 cm from the bottom and 28 cm from the left edge, facing the top. The loops go to the left.
2. **Pen:** a felt-tip marker, snug in the centre hole, with the tip just touching the paper. Pressing hard drags the robot. Use the same pen you will draw with.
3. **Robot:** charged, with no cable hanging off it (use the wireless dongle). Load the program: `./thymio.sh load shinchan_calibrate.aesl` (Windows: `thymio load shinchan_calibrate.aesl`). It stays loaded until you switch the robot off.
4. Press the test's button, let go, and don't touch the robot until the LED goes off.
5. **Run each test twice, on fresh paper.** If the two runs differ a lot, the problem is slipping, not calibration.

## Take the photos

- Hold the phone **straight above** the drawing, parallel to the paper, with the whole drawing in the frame.
- Lay a **ruler or tape measure** flat next to the drawing, with its numbers readable in the photo. That's how the photo gets its scale.
- Use even light, with no shadow across the lines.
- Write the test name on the paper (T1, T2, T3). If you changed `cm`, `t90r` or `t90l`, write the values too.

Send the photos to Claude Code. Drag them into the chat and say which test each one is.

## What each test measures

| Test | What is measured | What it gives |
|---|---|---|
| T1 | Distance between the dots | Real speed per speed unit, and the distance lost when starting and stopping. Sets `cm`. |
| T1 | Last part, at speed 300 | Whether faster driving scales the same way (the spiral drives at 400) |
| T1 | Sideways drift at the end of the line | Left/right motor mismatch |
| T2 | The three right-turn corners | `t90r`: right spins, as used by the underpants and the shy bot's cloud |
| T2 | The three left-turn corners | `t90l`: left spins, as used by the flower |
| T2 | Side lengths, and whether the second square closes | `cm` in real use, and how the errors add up |
| T3 | Loop sizes | The real distance between the wheels, and how accurate slow and backward wheel speeds are |
| T3 | How much the line bends at each loop | Whether curves turn as far as the spins suggest. This affects the flower petals and the cloud's arcs. |

The photos give new values for:

- **`shinchan_drawings.aesl` and `shinchan_bot.aesl`:** `t90` and `cm`. If left and right spins differ, these programs get separate left and right values.
- **`shinchan_shy.aesl`:** `t90_cw`, `t90_ccw`, `half_wheelbase_mm` and `arc_time_percent`.

The escape turn at speed 500 (`turn_time`) isn't covered.

To check the new values, set them in the test program while it is loaded, for example `./thymio.sh set cm=214 t90r=1620 t90l=1620`. Run the tests again: the squares should close and the line should come out straight after each loop.

## Side pen with the extra weight (2026-10-27, `shinchan_calibrate_side.aesl`)

The pen now sits in a holder outside the robot, and the robot is heavier. Measured from photos with a ruler, using line, circle and ellipse fits:

| Test | Measured | Meaning |
|---|---|---|
| T1 | Forward 25.5, 56.5, 117.9 mm in 0.64, 1.28, 2.57 s at 150; backward 22.2, 59.5, 115.9 mm | **48.0 mm/s at speed 150, the same forward and backward** (0.320 mm/s per unit), about 5 mm lost at each start |
| T1 | The 180° turn drew a 166° arc of radius 159.5 mm around the robot's centre | Turning on the spot is **8 % slower** than before the side pen. The pen tip is **152.6 mm left of the centre and 45.2 mm behind it** |
| T2 | Slow quarter turns (±60, 4.05 s): 83.5°, 83.5° right; 82.4°, 81.5° left | Same turn rate as T1: 0.00298 rad/s per unit of wheel difference (was 0.00323) |
| T2 | Fast quarter turns 66–73°, and the 40 cm straight came out 33 cm | The battery was running low (it died soon after), so fast moves were about 20 % slow. Not used |
| T3 | Slow forward line at 60: 32.9, 71.4, 142.5 mm in 2, 4, 8 s | 18.2 mm/s at speed 60 (0.304 mm/s per unit), 5 % below speed 150. Several runs overlap on this sheet, so only this line was used |

New values in `shinchan_shapes_offset.aesl`: pen 152.6 mm left / 45.2 mm back, speed 0.312 mm/s per unit, turn rate 0.00298 → `kb = -2026`, `kw = -695`, heading update `* 115 / 74`. In simulation on the measured robot, the old values would have missed the shapes by 15–31 mm, the new ones by 1–2.4 mm.

The centre-pen programs (`shinchan_drawings`, `shinchan_bot`, `shinchan_shapes_test`) still use `t90 = 1620`, `cm = 214` from before the weight. If the holder stays on, a 90° spin from rest now needs about **1760 ms** (1620 × 180 ÷ 166), while straight driving is unchanged.
