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

## Side-pen shapes: line, squares and circles (2026-10-28, `shinchan_calibrate_offset.aesl`)

The side-pen shapes still come out shifted. The tests above measured the robot's motion; this one checks the shape program itself. It is `shinchan_shapes_offset.aesl` with a different drawing table: the pen tip draws the figures of the first calibration, a line, two squares and three circles. Same steering every 50 ms, same `kc`, `kb`, `kw` and heading update. Preview: [`calibration_offset_expected.svg`](calibration_offset_expected.svg).

| Button | Test | The pen draws | Paper | Pen start: from left, from bottom |
|---|---|---|---|---|
| Forward | T1 line | To the right: 3, 6, 12 cm, ink dot between the parts | 25 × 27 cm | 2 cm, 2 cm |
| Left | T2 squares | 12 cm square up-right (right turns), then 12 cm square down-left (left turns), touching at the start | 60 × 60 cm | 25 cm, 23 cm |
| Right | T3 circles | Line to the right with circles 3, 6 and 9 cm across sitting on it, counter-clockwise | 55 × 52 cm | 15 cm, 25 cm |

The circles are the same sizes as the curves in the underpants and the cloud (1.4 to 4.8 cm radius).

**Run it:** full battery. Robot facing the top edge of the paper, square to it, pen tip on the start point. Run each test twice on fresh paper. Photograph from straight above with a ruler, as for the first calibration, and write the test name on the sheet.

**What a wrong number looks like.** Simulated with this program on a robot that differs from the one it assumes:

| The real robot | T1 line | T2 squares: end misses the start by | T3 circles: worst gap |
|---|---|---|---|
| as assumed | straight, 3 / 6 / 12 cm | 2.5 mm | 0.9 mm |
| turns 5 % faster | first part bends 5° down, last 4° up | 30 mm | 15 mm (middle circle) |
| turns 5 % slower | first part bends 8° up, last 4° down | 26 mm | 18 mm |
| drives 5 % faster | 5 % longer, drifts up 2–4° | 32 mm | 12 mm (big circle) |
| one wheel 3 % faster | 3–7 mm off | 21–38 mm, sides tilted up to 8° | 12–14 mm |
| pen 5 mm off from where the program thinks | 6–7 mm off | 9–12 mm | 9–10 mm |
| motors lag 0.1 s | no change | no change | no change |

Each error leaves a different pattern across the three figures, so they are fitted together: simulate the program on a robot model, adjust speed, turn rate, each wheel and the pen position until the simulated figures match the photos, then recompute `kc`, `kb`, `kw` and the heading update for `shinchan_shapes_offset.aesl` (and this program).

### Results (2026-10-28)

Measured from photos (scale from the ruler's 1/16-inch ticks, corners from line fits, stops from the ink dots) and from wheel logs: a copy of the program that reports the commanded speed, measured speed and motor power of each wheel every 20 ms.

| Test | Measured |
|---|---|
| T1 line | Parts 26.4, 49.3, 118.0 mm (should be 30, 60, 120). The first part leans 17° away from the rest. Three runs looked the same |
| T2 squares | Sides 109–124 mm, turns +89.8 +93.3 +93.7 −84.5 −89.3 −89.7°. The long side misses the start by 17 mm; the end lands 10 mm from the start |
| T3 circles | First run: the circles miss closing by 22, 14 and 12 mm. Later runs (one at full speed, two at half speed) repeat each other but differ from the first run. At half speed the 3 cm circle comes out 46 mm, at full speed 37 mm |
| Wheel logs | The motors follow the commanded speed within 1–2 %, 60–80 ms late. Below a speed of about 40 they only reach 55–75 % of it |

What this means:

- **Changing the constants doesn't help.** Fitting speed, turn rate, wheel mismatch, pen position, lag, a speed cap, an acceleration limit or a dead zone to one figure doesn't predict the others. Constants fitted to the T3 runs (`kb = -1676`, `kw = -581`, heading `* 53 / 33`, pen 54 mm back / 152 mm left) made T2 no better: corner error rms 13.1 mm against 12.2 mm before. The programs keep the old values.
- **The pen tip doesn't stay in one place.** With everything else the same, the first T3 fits a pen 46 mm back / 158 mm left, the later runs 54 mm back / 152 mm left. The holder can't be fixed, and because the pen sits far to the side and only a little behind (about 3×), 8 mm of pen movement moves the drawing 10–20 mm.
- **Slow is worse.** Half speed spends more time at the wheel speeds below 40 that the motors can't hold, and the small circle grows.

With this pen mount, expect the side-pen shapes to be off by about 1–2 cm. Doing better needs a stiffer holder or a pen mounted behind the robot.

## Pen moved to the rear right (2026-10-28)

The pen is now fixed solidly **4.5 cm behind the centre hole and 4.2 cm to its right** (measured by hand). `shinchan_shapes_offset.aesl` and `shinchan_calibrate_offset.aesl` steer for that position: `kb = 840`, `kw = -1047`, pen speed 90 (`kc = 900`), new tables. The heading update stays `* 115 / 74`. Previews: [`calibration_offset_expected.svg`](calibration_offset_expected.svg), [`shapes_offset_preview.svg`](shapes_offset_preview.svg).

The pen is now 6.2 cm from the centre instead of 16 cm, with its sideways and backward distances about equal. In simulation the same robot errors hurt much less (worst miss over underpants, cloud and star):

| The real robot | Old side pen (15.3 left, 4.5 back, speed 60) | New rear-right pen (speed 90) |
|---|---|---|
| as assumed | 1.5–2.4 mm | 2.4–3.9 mm |
| turns 5 % slower | 11–21 mm | 7–10 mm |
| drives 5 % faster | 11–15 mm | 4–9 mm |
| left wheel 3 % faster | 9–23 mm | 6–8 mm |
| pen 5 mm off from where the program thinks | 5–10 mm | 6–11 mm |

**Why speed 90:** with the pen closer to the centre, the wheels turn more slowly for the same pen speed. At pen speed 60 they would spend 52–68 % of the time below 40, where the motors can't hold their speed. At 90 it's 30–46 %, the wheels peak at 209 and the shapes take 15–23 s. The pen position is now what matters most, so the first thing to check is whether the T1 line comes out straight with its parts 3, 6 and 12 cm long.

### The pen jams when it is pushed (2026-10-28)

First T1 with the rear-right pen: parts 24.8, 53.7 and about 83 mm instead of 30, 60 and 120, and the line bends. The wheel log of the same run says the wheels drove 26.5, 58.3 and 116.5 mm almost straight, so the robot slipped. To check, `shinchan_calibrate_side.aesl` T1 drove straight forward (pen dragged behind the robot), turned on the spot, then drove straight backward (pen pushed ahead of the robot):

| | Wheels (from their own speed readings) | Ink | Ink ÷ wheels |
|---|---|---|---|
| Forward 3, 6, 12, 12 cm | 24.1, 53.6, 114.8, 107.9 mm | 25.3, 56.7, 112.7, 105.7 mm | 98–106 % |
| Backward 3, 6, 12, 12 cm | 24.6, 54.8, 114.5, 106.6 mm | 12.3, 38.1, 75.3, 65.0 mm, curved | 50–69 % |
| 180° turn on the spot | | an arc of about 76° | |

Dragged, the pen draws exactly where the wheels go. Pushed, it digs into the paper, the wheels spin and the robot is twisted round the pen. The pen-tip steering makes this worse: following a point outside the wheels is only steady when that point leads, so the robot ends up moving with the pen ahead of it (backing up, for a pen behind). The pen must slide freely when it is pushed: upright or with its tip leaning towards the robot, touching the paper lightly. This is probably also why the side pen gave different drawings from run to run.

### 3D-printed pen sleeve (2026-10-28)

To stop the jamming, the pen now sits upright in a printed 18 × 18 × 60 mm sleeve (`cad/`). Its tip is **4.5 cm behind the centre hole and 4.7 cm to its right**, so `kb = 940` (was 840); `kw = -1047` and the tables stay the same at first. The previews are redrawn; T3 needs 48 × 35 cm of paper and the cloud 31 × 37 cm. Next: the forward/backward test again (backward ink should now match the wheels like forward does), then T1–T3.

The forward/backward test again with the sleeve (`shinchan_calibrate_side.aesl` T1 with the wheel log, photo scale 2.306 px/mm from the ruler):

| | Wheels | Ink | Ink ÷ wheels |
|---|---|---|---|
| Forward 3, 6, 12, 12 cm | 24.5, 54.6, 114.9, 107.7 mm | 23.0, 52.5, 112.3, 103.0 mm | 94–98 % |
| Backward 3, 6, 12, 12 cm | 24.3, 54.6, 112.0, 107.5 mm | 25.4, 53.9, 111.0, 104.4 mm | 97–105 % |

Pushed or dragged, the pen now draws where the wheels go, and both lines are straight (ink within 0.8 mm rms of a straight line over 28 cm, bow under 1.3 mm). The jamming is gone.

The turn on the spot drew a clean arc (radius 66.5 mm, 0.55 mm rms). The two lines' directions say the robot turned 167.8°, while the wheel readings with `W = 104.7` say 159.8°, so without the side pen dragging the robot turns more for the same wheel difference: **`W = 99.7` mm**. The programs now use `kw = -997` and heading update `(r - l) * 31 / 19`. The arc also puts the pen about 45 mm behind and 50 mm right of the centre (±2 mm; measured by hand: 47 mm right), so `kb` stays 940 until T1 says otherwise.

### T1 with the sleeve, and a joint fit (2026-10-28)

Two T1 runs with `kb = 940`, `kw = -997`, `* 31 / 19` drew the same line both times: parts 22.4 / 53.6 / 110.1 mm and 22.8 / 53.2 / 109.7 mm instead of 30 / 60 / 120, bowed about 6 mm, the first part tilted about 11°. In both runs the robot started T1 again about 0.1–0.4 s after it finished (the program received `button.forward`), and because the robot had turned about 90° while drawing, the second start went off at a right angle until the logger stopped it. That hook is not part of the test. The logger now stops the program as soon as the drawing ends.

Fitting the wheel logs of both T1 runs and the forward/backward test to their photos together (dots and ink, one rigid placement per photo) gives:

| | Before | Fitted |
|---|---|---|
| Distance per wheel unit (`K`) | 0.312 mm | 0.293 mm (± 0.001) |
| Speed ÷ turn rate (`W`) | 99.7 mm | 95.1 mm |
| Pen behind the centre hole | 45 mm | 43.8 mm |
| Pen right of the centre hole | 47 mm | 48.7 mm |

With these, every dot in the three photos sits within 1–3 mm of the path rebuilt from the wheels. The spin alone only fixes `K ÷ W`, which is why it gave 99.7 with the old `K`. The programs now use `kb = 1001`, `kw = -978`, heading `(r - l) * 53 / 33` and tables built for `K = 0.293`. In simulation on the fitted robot, T1 comes out 30.3 / 60.6 / 119.9 mm and within 0.5 mm of a straight line.

T1 with the fitted constants: parts **24.6 / 56.7 / 115.4 mm** (82 / 94 / 96 %, before 75 / 89 / 91 %), bow about 4 mm (before 6), no restart. Refitting with this run as well hardly moves the constants (`K` 0.292, `W` 95.1, pen 43.7 / 49.0 mm). Parts 2 and 3 match the wheels to 1–3 %. Part 1 is again about 5 mm shorter than the wheels say: at the start the robot pivots hard on one wheel (−193 / +5) while the other wheel sits at speeds the motor can't hold.

The first T2 with these constants stopped by itself after four sides: the robot stood still for 1.85 s with its motors at 0, after a stray button event like the T1 restarts. The forward, left and right buttons now only start a test while the robot is idle (`timer.period[0] == 0`); the log copy records `j` and `e` so the next stray event shows which button it was.

T2 with the fitted constants (battery ran out 40 s in, during the last side): ink sides 112.0 / 106.8 / 109.3 / 221.3 / 100.4 / 107.9 mm against 116–117 / 235 mm from the wheels; turns −102.7 / −87.6 / −84.9 / +79.5 / +77.4° against about ±90 from the wheels; the first square misses the start by 11 mm. During every side the body swings 74–92° (one wheel near 0, the other near ±200), and the ink says the counter-clockwise swings came out about 12° short and the clockwise ones 3–5° short. A fit with separate left and right turn constants explains T2 to 1–8 mm but only with `K` 0.271–0.289, which the T1 and forward/backward photos don't accept. Since the battery was nearly flat for the whole run, T2 is to be repeated with a full battery before any constant changes.

T2 again on a full battery drew the same thing: sides 111.1 / 108.1 / 106.8 / 221.7 / 104.4 / 106.8 / 106.9 mm, turns −97.9 / −86.6 / −83.0 / +78.9 / +79.6 / +76.7°, end 71 mm from the start, while the wheels said 116–118 mm and 89–91°. So it's not the battery but the turning: with one wheel near 0 and the other near ±200 the body turns less than the wheels say, more so counter-clockwise. Fitting the three T1 runs, the forward/backward test and this T2 with separate turn constants: `K` 0.290, 104.8 mm for left turns, 95.0 mm for right turns, pen 41.7 mm behind and 49.9 mm right (T1 within 3 mm, T2 within 10 mm, forward/backward within 6 mm). With those as the real robot, the old program reproduces the T2 error (turns −99 / −88 / −90 / +80 / +81 / +81°, end 56 mm off).

Both programs now steer with `kw = -1026` for right turns and `kp = -1132` for left turns, update the heading with `* 39 / 27` (left) or `* 43 / 27` (right), use `kb = 1077` and tables for `K = 0.290`. In simulation on the fitted robot: T2 turns within 1°, end 3 mm from the start; underpants, cloud and star within 2 mm (with the previous program 16–22 mm).

T2 with the separate left/right constants (full run, photo scale 2.868 px/mm from the ruler below the drawing): sides 137 / 142 / 135 / 278 / 134 / 135 mm, turns −102.4 / −104.2 / −95.6 / +103.8 / +95.9 / +80.5°, end 75 mm from the start. The correction overshot: the turns went from too small to too big, and the sides from 8 % short to about 15 % long, although the fitted model predicted 118 mm sides and ±1° turns for this run. Changing `kb`, `kw` and `kp` by 5–16 % moved the corners by 10–25°, and within one run the corners scatter by ±5–7°, so this pen position (behind the wheels, the body swinging about 90° on every side) is too sensitive to tune from a few photos.

Next try (V3), interpolated from the two T2 runs: right turns and side lengths moved about three times too far between the versions, left turns came out right on average, so `kb`, `kw`, the right-turn heading and `K` go 1/3 of the way from the first version to the second, and `kp` and the left-turn heading 0.8 of the way: `kb = 1026`, `kw = -994`, `kp = -1101`, heading `* 59 / 40` (left) or `* 64 / 40` (right), tables for `K = 0.292`.

V3 results (one oblique photo of all three, scale 2.26 px/mm from the ruler's inch numbers, which agree to 0.7 % along the ruler):

- T2: sides 108 / 130 / 128 / 274 / 134 / 141 / 136 mm (measured corner to corner, the sides are slightly bowed), turns −81.7 / −96.8 / −102.5 / +93.2 / +102.4 / +101.1°, end 79 mm from the start. The wheel commands in the log match the simulated program exactly.
- T3: circles 34.4 / 63.8 / 95.5 mm across instead of 30 / 60 / 90.
- T1: the logger stopped the robot 4 mm into the third part (it took the 0.95 s pause before the last part for the end; fixed: it now waits for motion after the last table entry).

Turn errors per corner (ink − ideal) over the three versions:

| Corner | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| V1 (`kb` 1001, one turn constant) | −7.9 | +3.4 | +7.0 | −11.1 | −10.4 | −13.3 |
| V2 (`kb` 1077, `kp` −1132) | −12.4 | −14.2 | −5.6 | +13.8 | +5.9 | −9.5 |
| V3 (in between) | +8.3 | −6.8 | −12.5 | +3.2 | +12.4 | +11.1 |

V3 is not in between V1 and V2 corner by corner, and no version gets below about ±13°. The same program repeats its errors closely (V1 on a low and a full battery agreed within 2–5°), so the errors are not random, but they change in ways a few constants can't follow.

## Pen straight behind the centre (2026-10-28)

The centre hole is taken, so the sleeve moved to **4.8 cm straight behind the centre hole (1 mm left)**. With no sideways offset, `kb` is almost 0 (−19), and at the start of every side the steering asks for a turn on the spot (wheels −95 / +95 for a 90° corner at speed 90) instead of a swing round one nearly stopped wheel (−208 / −5 before). Turns on the spot matched the wheels in the forward/backward test, left and right turns are now mirror images, and the fastest wheel drops from 228 to about 130. Both programs are back to one turn constant: `kb = -19`, `kw = -892` (`W` 95.1 mm), heading `(r - l) * 8 / 5`, tables for `K = 0.292`. Paper sizes and starts are in the README and the previews.

### T1–T3 with the pen behind the centre, and a spin test (2026-10-28)

With `kb = -19`, `kw = -892`, `* 8 / 5`, `K = 0.292`: T2's right-turn square came out with corners of 96–98°, and every side of the left-turn square has a sudden 15–29° bend about a third of the way along. T1's first 3 cm leave at about 35° to the rest of the line, and T3's big circle is egg-shaped with the baseline turning after each circle. The wheel logs show where: each bend is at the moment the right wheel reverses (sides 2, 5, 6, 7); the sides where the left wheel reverses (3, 4) are straight. Both wheels read the same (about 0.5 s near 0 at each reversal), so the right wheel loses grip on the paper there without the motor noticing.

Spin test (`spin_test_log.aesl` in the scratch work: 270° left on the spot, 15 cm back, 270° right, 5 cm back; the pen draws two arcs):

| | Wheels (K 0.292, W 95.1) | Ink | Ratio |
|---|---|---|---|
| Turn left on the spot | 265.1° | 289.6° | 1.092 |
| Turn right on the spot | 265.2° | 291.7° | 1.100 |
| Back | 146.8 mm | 161.2 mm | 1.098 |

Turns on the spot are the same both ways, and everything moves about 10 % further than `K = 0.292` says: `K = 0.321` (close to the 0.312 of the first calibration; the 0.29 came from the rear-right pen dragging), `W = 95.3` mm, pen 44–46 mm behind (arc radius). Programs now: `kb = -20`, `kw = -953`, heading `* 86 / 49`, tables for `K = 0.321`. Before the next T1–T3: check that the right tyre doesn't slip on its hub and clean both tyres.

### T1–T3 with `K = 0.321`, and a gentler start (2026-10-28)

| | Before (K 0.292, pen 48) | Now (K 0.321, pen 45) |
|---|---|---|
| T2 right turns | −98 / −97 / −96° | −93.2 / −95.2 / −89.3° |
| T2 left turns | +66 / +70 / +76° | +83.3 / +80.1 / +80.1° |
| T2 first square closes | no | long side 5.5 mm from the start |
| T2 end from start | about 75 mm | 33.5 mm |
| T3 circles (30 / 60 / 90) | big one egg-shaped | 25.9 / 59.9 / 87.9 mm |
| T1 parts (30 / 60 / 120) | first part off by 35° | 25.3 / 49.0 / 115.0 mm, bends of 14.5° and 8.9° at the two dots |

What is left happens where the robot starts from standing still (T1 bends exactly at its stops, T2 sides all start from rest), and it is almost always clockwise; the circles, drawn without stopping, are good. The robot is heavier now, so a jump from 0 to ±95 in one step makes the wheels slip. Both programs now limit the change of each wheel speed to 32 per 50 ms step, also when stopping, in a subroutine `mv` that also does the heading update with the limited speeds. On an ideal robot this costs nothing on T1 and T2 and 1–6 mm on the shapes (cloud 8 mm instead of 2). Programs: 476 and 502 words.

T1–T3 with the speed-change limit looked the same as without it, so slipping from a hard start isn't the cause, and the limit is taken out again (it only costs shape accuracy). Next: T1 without the stops between its parts, to see whether stopping and starting again makes the bends.

### One combined test instead of T1–T3 (2026-10-28)

A single figure now covers every move (scratch `combo_offset_log.aesl`, about 33 s, paper 50 × 33 cm, pen start 9 cm from the left and 19 cm from the bottom): right 6 cm, a stop, right 6 cm, then up 6, right 6, down 6, right 6 (two left and two right turns without stopping), a 6 cm circle counter-clockwise, right 6, a 6 cm circle clockwise, right 6.

| | Run 1 | Run 2 (speed change limited to 24 per step) |
|---|---|---|
| Line before / after the stop | −9.4° | −10.8° |
| Left, right, right, left | +90.4 / −92.2 / −81.6 / +76.7° | +91.1 / −94.6 / −86.7 / +75.7° |
| Direction after the CCW / CW circle | −6.1 / +2.2° | −3.3 / +2.0° |
| Circles | 60.2 / 56.2 mm | |
| Every straight part | within 0.4 mm of straight | |

The commanded turns are all within 1.6° of the plan. The errors repeat from run to run, the speed limit changes nothing, and neither a low-speed dead band, a different response time per motor nor a different turn rate per direction reproduces them. What the numbers do fit: with the pen 45 mm behind the wheels, the body needs about 110 mm of drawing after a 90° corner to settle within 10° of its final heading, so 6 cm parts are drawn entirely while the body is still swinging, and then the pen's direction depends directly on how far the body has actually turned. Straight runs and steady circles, where the body doesn't swing, come out right. The fix is a pen on the wheel axis, best in the centre hole, where corners become turns on the spot.
