hiii I am yoyo

# Thymio: the Shin-chan bot

A Thymio that behaves like Shin-chan: it hunts down whoever is nearby, chases them, taunts them and runs off, and when nobody is around it gets bored and draws underpants on the floor. Plus a drawing program, a simulator setup to test it, and command-line tools. Works on **Windows** and **macOS**.

## What's in here

| File | What it is |
|---|---|
| `shinchan_bot.aesl` | **The robot program.** Search, chase, taunt, avoid, and draw underpants when bored, with the pen 4.5 cm straight behind the centre hole. |
| `shinchan_shy.aesl` | Explore open space, draw small clouds (pen 4.5 cm straight behind the centre hole), and escape front, rear, or edge hazards. A blocked front escape retries with 90° turns. |
| `shinchan_submit.aesl` | Submission version of the shy bot. It calls state 1 WANDER, calls the escape oscillation SHIVER, and draws the same cloud with the pen behind the robot after eight seconds. Front escapes turn 180° initially, then 90° on blocked retries; rear escapes do not turn. |
| `shinchan_drawings.aesl` | Drawing only: a button picks a spiral, a flower or underpants. |
| `shinchan_calibrate.aesl` | Calibration drawings for the real robot: a line, two squares, three loops. |
| `shinchan_shapes_test.aesl` | Test drawings on the real robot: underpants, cloud and star, about 12 cm each. |
| `shinchan_shapes_offset.aesl` | The same three shapes for a pen mounted outside the centre hole (4.5 cm straight behind it). |
| `shinchan_calibrate_side.aesl` | Calibration tests for the earlier side pen (15 cm left): fast lines, turn circles, slow lines. |
| `shinchan_calibrate_offset.aesl` | The outside-pen shape program drawing a line, two squares and three circles, to calibrate it. |
| `sim_victim.aesl` | A simple wandering robot for Shin-chan to chase in the simulator. |
| `playgrounds/arena.playground` | Simulator arena: empty 2 × 2 m square, four robot-sized cylinders, Shin-chan in the middle. |
| `playgrounds/arena_chase.playground` | Same arena with a second Thymio (`victim`) 45 cm ahead of Shin-chan. |
| `playgrounds/arena_floor.png` | Floor of both arenas: how far Shin-chan can see (rings around the cylinders, sensor beams at his start) and a 10 cm grid. |
| `docs/logic.md` | **How the programs work:** flowcharts and pseudo code. |
| `docs/handoff.md` | Current calibration values, pen setups, tested status, and next work for a collaborator. |
| `docs/chase_trail.svg` | Shin-chan's and the victim's trails in the chase arena, to scale, coloured by mode. |
| `docs/drawings_preview.png` | What the drawing program draws. |
| `docs/calibration.md` | **Why the real robot draws differently from the simulator**, and how to calibrate it from photos. |
| `docs/calibration_expected.svg` | What the calibration program draws on a perfect robot, to scale. |
| `docs/shapes_preview.svg` | What the shape test draws on our calibrated robot, to scale. |
| `docs/shapes_a4_placement.svg` | Where to start each shape of the shape test on a landscape A4 sheet. |
| `docs/cloud_preview.svg` | The shy bot's cloud on our robot, after calibration and before. |
| `docs/shapes_offset_preview.svg` | The outside-pen shape test: drawings, start position and the paper each shape needs. |
| `docs/calibration_side_expected.svg` | What the side-pen calibration tests draw on a calibrated robot, with the paper each needs. |
| `docs/calibration_offset_expected.svg` | What the outside-pen line, squares and circles test draws, with start points and the paper each needs. |
| `docs/arena_floor.svg` | Editable source of the arena floor. |
| `docs/instructions_prompts.rtf` | The original assignment prompts. |
| `tools/thymio.py`, `tools/trail.py` | Command-line helper (see below). |
| `thymio.cmd` / `thymio.sh` | Launchers for the helper (Windows / macOS). |
| `requirements.txt` | Python package the helper needs (`tdmclient`). |
| `calibration/` | Pen and motion calibration sketches, grouped by centered or offset pen. |
| `archive/xiao_communication/` | Archived: XIAO/Arduino connection experiments, no longer used. |

## Software you need

1. **[Thymio Suite](https://www.thymio.org/download-thymio-suite/)** (Windows, macOS, Linux). It includes Aseba Studio, the simulator, and the Thymio Device Manager that connects everything to the robot. The download page asks you to sign up; "Skip and download" also works.
2. **Python 3**, only for the command-line helper.
   - **Windows:** install from [python.org](https://www.python.org/downloads/) and tick **"Add python.exe to PATH"** in the installer.
   - **macOS:** usually already there. Check with `python3 --version`.

## Run the simulator

1. Open **Thymio Suite**, choose **Aseba Studio**, then click **"launch a simulator"**.
2. A file picker asks for an arena. Pick `playgrounds/arena.playground` (one robot) or `playgrounds/arena_chase.playground` (Shin-chan and a victim) from this folder.
   - **macOS:** press **Cmd+Shift+G** in the picker and paste the folder's path.
   - **Windows:** paste the folder's path into the picker's address bar.
   - Starting the simulator with an arena file from the command line doesn't work (you get an empty grey world). Always use the picker.
3. **Allow network access** when asked, or Thymio Suite won't see the simulated robots.
   - **macOS:** "Allow AsebaPlayground to find devices on local networks?" → **Allow**. To fix it later: System Settings → Privacy & Security → Local Network.
   - **Windows:** Windows Firewall prompt → **Allow**. To fix it later: Windows Security → Firewall & network protection → Allow an app through firewall.
4. Load the programs with the helper below, or in Thymio Suite select the robot (`shinchan` or `victim`), click **Program with Aseba Studio**, open the `.aesl` file, then **Load** and **Run**.

In the simulator you can drag robots and cylinders with the left mouse button and turn them with the right. If the helper suddenly says "No robot found" while the simulator is still open, close the simulator and open it again; it sometimes stops announcing its robots.

For a **real robot**, plug in the Thymio with USB (or the wireless dongle). It appears in the same list.

## Command-line helper

Open a terminal in this folder. The first run sets up a Python environment in `.venv` automatically.

| | Windows (Command Prompt) | Windows (PowerShell) | macOS |
|---|---|---|---|
| Show robots | `thymio list` | `.\thymio list` | `./thymio.sh list` |

All commands, written the Windows way (use `./thymio.sh` on macOS):

| Command | What it does |
|---|---|
| `thymio list` | Show connected robots, real and simulated |
| `thymio load shinchan_bot.aesl` | Compile and start a program |
| `thymio stop` | Stop the program |
| `thymio read prox.horizontal state` | Print variables once |
| `thymio watch prox.horizontal state --seconds 5` | Print variables live (Ctrl+C to stop early) |
| `thymio set detect=800` | Change a variable while it runs |
| `thymio set leds.top=0,32,0` | Set an array (comma-separated) |
| `thymio size shinchan_bot.aesl` | How much of the robot's program memory (1534 words) a program uses |
| `thymio trail playgrounds\arena_chase.playground shinchan=shinchan_bot.aesl victim=sim_victim.aesl --seconds 180 --out docs\chase_trail.svg` | Run programs in a freshly opened simulator and draw the robots' trails as an SVG, to scale |

With several robots, add `--robot` and part of the name, e.g. `thymio --robot victim load sim_victim.aesl`.

**Rules:**
- Thymio Suite must be open; the helper connects to robots through it.
- Only one program can control a robot at a time. Disconnect Aseba Studio before using `load`, `stop`, `set`, `size` or `trail`.
- `trail` needs the simulator opened fresh, so the robots are where the `.playground` file puts them. It rebuilds the path from the wheel speeds the robots report; bumps and rounding add up, so the part after `--solid` seconds (default 100) is drawn faded. Options: `--seconds`, `--out`, `--set ROBOT.VAR=VALUE` (applied right after start), `--k` and `--w` (speed scale and wheel spacing; the defaults fit the simulator).

## The Shin-chan bot (`shinchan_bot.aesl`)

Flowchart and pseudo code: [`docs/logic.md`](docs/logic.md). The top LED shows the mode:

| State | Colour | What it does |
|---|---|---|
| 1 SEARCH | blue | Snake forward in deep S-waves (steering flips every 1.6 s), with a small random lean so the path wanders. Something behind makes it turn around |
| 2 PURSUE | green | Chase whatever is in front: slower as the gap closes, faster the longer the chase lasts (up to 400), so a robot driving away still gets caught. Half the chases (at random) weave left and right |
| 3 BORED | cyan | 17 s of searching with nothing found: draw underpants (12 × 9 cm). Stops the moment something shows up |
| 6 RECOVER | yellow | Lost it: spin toward the side it was last seen for 2.5 s, then back to SEARCH |
| 5 TAUNT | magenta | Caught it (close enough, or touching it while chasing): stop 1 s, spin around, run away 2 s, then SEARCH. Bumps are ignored during the stop and spin |
| 4 AVOID | red | Touching something (not while chasing it): back off and turn away (boxed in: spin on the spot), at least 1.5 s and until everything is clear |

The state number is also the LED colour: 4 = red, 2 = green, 1 = blue, added together.

The program uses about 394 of the robot's 1534 words of program memory (`thymio size` checks this) and has no comments, to stay small.

Settings at the top of the file; `thymio set` changes them while it runs. The first five are raw IR readings (higher = closer), not millimetres; calibrate them with the real robots.

| Setting | Default | Meaning |
|---|---|---|
| `detect` | 700 | Start chasing (the sensors see about 13 cm) |
| `lost` | 500 | Target lost |
| `close` | 2500 | Close enough to taunt (about 7 cm) |
| `hard` | 4000 | Touching (about 2 cm) |
| `clear` | 1500 | Everything below this ends AVOID |
| `bored` | 172 | Ticks (0.1 s) of searching before drawing underpants |
| `kc`, `kb`, `kw` | 900, -20, -953 | Pen steering for the pen 4.5 cm straight behind the centre hole, as in `shinchan_shapes_offset.aesl` below |

The pen sits behind the robot, so while drawing the program steers the pen tip every 50 ms and the robot's body swings round as needed (same method and numbers as the outside-pen shape test). These were measured on our real robot on paper; the drawing takes about 15 s and needs about 27 × 28 cm.

## The shy bot (`shinchan_shy.aesl`)

The shy bot explores open space for eight seconds, then draws the six-arc cloud (the cloud of the shape test, about 12 cm) with the pen 4.5 cm straight behind the centre hole, steering the pen tip every 50 ms like `shinchan_shapes_offset.aesl`. It uses the current heading as the cloud's starting direction. When the cloud finishes, a new eight-second exploration session begins. At a moderate front reading it slows down and steers around the clearer side for up to three seconds. A rapid rise in the reading, a very close object, a failed maneuver, or a sustained dark ground reading triggers the backward wiggle, 180° turn, and forward shot. A moderate rear reading makes it move forward a little faster; a rapidly rising or very close rear reading starts a forward wiggle and shot without a turn. Drawing waits while an obstacle is near. Interrupted clouds are abandoned and started fresh after another exploration session.

The main states are explore (green, or yellow while maneuvering), draw (cyan), and avoid (red). Orange marks a brief blocked phase. If the front path is still blocked and the rear is clear, the robot starts another backward wiggle, turns 90° toward the less occupied side, and tries the forward shot again. This can repeat without a retry limit. If the rear is also blocked, it waits for room to retreat. The center button pauses (blue) or resumes.

Settings near the top include `front_threshold`, `front_hard`, `rear_threshold`, `rear_hard`, `fast_rise`, `maneuver_fast_rise`, `maneuver_timeout_ticks`, `white_min`, `edge_samples`, the pen steering `pen_speed`, `pen_side`, `pen_turn` (same as `kc`, `kb`, `kw` in the robot program; the cloud is the 6-arc cloud of the shape test), and the wiggle, turn, and shot timings. `fast_rise` is a rise in raw IR readings over roughly three sensor updates; it is an apparent closing-rate cue, not a measurement of an object's speed in millimetres per second. Two consecutive rising readings are required, and the threshold is higher while maneuvering because turning also changes the readings. The normal ground debounce is ten readings, as in the edge test; the faster escape motions use a two-reading edge stop. Try it first with the pen raised and enough room around the robot, then adjust the thresholds and timing on the actual surface.

`shinchan_submit.aesl` uses the same pen-behind cloud and three escape variations, naming the wiggle SHIVER. Its front and rear checks share `obstacle_threshold = 1500`, `hard_threshold = 3000`, and `clear_threshold = 900`. Its shiver alternates motor targets of 600 and 0 and relies on the robot to limit the 600 target. `turn_180_ms` and `turn_90_ms` remain separate settings for calibration.

## The drawing program (`shinchan_drawings.aesl`)

Draws with a pen in the centre hole. The pen line is the path of the robot's centre: driving draws, spinning in place leaves only a dot.

| Button | Draws | Size | Time | Start with the pen at |
|---|---|---|---|---|
| Forward | Spiral, 5 coils | about 21 × 17 cm | 20 s | the centre of the spiral |
| Left | Flower, 5 petals | about 13 × 13 cm | 42 s | the centre of the flower |
| Right | Underpants | 12 × 9 cm | 16 s | the top-left corner, robot facing right |
| Centre | Stop | | | |

Drawing starts 1 s after you let go of the button. In the simulator (no buttons), start a shape from the computer with `thymio set n=12 s=0 timer.period=1000,0` (`n=200` spiral, `n=20` flower, `n=12` underpants). The simulator doesn't draw lines; `thymio trail` can show the path.

**Calibrate on paper** with two settings:

| Setting | Default | Meaning | How to fix it |
|---|---|---|---|
| `t90` | 1620 | ms for a 90° spin | Draw the flower. If the last petal lands past the first, lower `t90`; if it falls short, raise it. |
| `cm` | 214 | ms to drive 1 cm | Draw the underpants and measure the waistband. New `cm` = `cm` × 120 ÷ measured mm. |

For the newer turn, circle, edge, shy-motion, and offset-pen cloud tests, see [`calibration/`](calibration/README.md). The centered-pen turn and shape test assumes the pen is on the wheel axis; the offset-pen cloud has its own motion calculation.

## Calibrating the real robot (`shinchan_calibrate.aesl`)

The real robot doesn't move like the simulator. All drawings are timed, so the real robot's shapes come out distorted until it is calibrated. [`docs/calibration.md`](docs/calibration.md) explains why and has the full instructions.

| Button | Test | Draws |
|---|---|---|
| Forward | T1 line | 33 cm straight line with three stop dots |
| Left | T2 squares | Two 12 cm squares, right turns then left turns |
| Right | T3 loops | A line with three loops of 4.8, 9.5 and 19 cm |
| Centre | Stop | |

Pen in the centre hole. The test starts 2 s after you let go of the button. Photograph each drawing from straight above with a ruler next to it, and send the photos to Claude Code to get new `t90`/`cm` values for every program.

## Shape test (`shinchan_shapes_test.aesl`)

Draws the three Shin-chan shapes at about the size of a calibration square (12 cm), using only the moves the calibration measured. Preview, to scale: [`docs/shapes_preview.svg`](docs/shapes_preview.svg).

| Button | Draws | Size | Time | Start with the pen at |
|---|---|---|---|---|
| Forward | Underpants | 11.9 × 8.6 cm | 19 s | the top-left corner of the waistband, robot facing right |
| Left | Cloud (the shy bot's six-bump cloud) | 12.1 × 10.0 cm | 40 s | the right side of the cloud, robot facing right. It first turns 45° left on the spot |
| Right | Star | 11.7 × 11.2 cm | 23 s | the left end of the star's top bar, robot facing right |
| Centre | Stop | | | |

The light is purple, cyan or yellow while drawing and goes off when the shape is done. The drawing starts 2 s after you let go of the button. `cm` and `t90` sit at the top of the file, as in the other programs.

**On A4:** lay the sheet in **landscape** (long side left to right) and tape it down. Put the pen tip at the start point below, with the robot facing the right edge. Each shape then sits in the middle of the sheet and the wheels stay on the paper. Picture: [`docs/shapes_a4_placement.svg`](docs/shapes_a4_placement.svg).

| Shape | Pen start: from the left edge | from the top edge |
|---|---|---|
| Underpants | 9.0 cm | 6.2 cm |
| Cloud | 19.6 cm | 9.5 cm |
| Star | 9.0 cm | 9.2 cm |

To start from the computer instead of the buttons: `thymio set i=0 e=33 timer.period=2000,0` (underpants), `i=33 e=69` (cloud), `i=69 e=96` (star), each with `timer.period=2000,0`.

## Shape test with the outside pen (`shinchan_shapes_offset.aesl`)

The same three shapes, for a pen fixed outside the centre hole: **4.5 cm straight behind it**, in a printed sleeve (since 2026-10-28; before that the pen sat 15 cm to the left, then 4–5 cm behind and 5 cm to the right, where every corner made the robot swing round one wheel). Spinning on the spot would swing that pen along an arc. Instead, every 50 ms the program works out the robot's heading and picks wheel speeds that move the **pen tip** along the shape; the robot's body swings around as needed. Preview with the start position and the paper each shape needs: [`docs/shapes_offset_preview.svg`](docs/shapes_offset_preview.svg).

| Button | Shape | Paper | Pen start: from the left edge, from the bottom edge | Time |
|---|---|---|---|---|
| Forward | Underpants (start: top-left corner of the waistband) | 27 × 28 cm | 9 cm, 14 cm | 15 s |
| Left | Cloud (start: its right side) | 28 × 29 cm | 18 cm, 13 cm | 16 s |
| Right | Star (start: left end of the top bar) | 32 × 26 cm | 9 cm, 12 cm | 22 s |
| Centre | Stop | | | |

- Same lights as the shape test. All shapes start with the robot **facing up** (away from you) and the pen tip on the shape's start point. The paper sizes include the robot's body swinging around the drawing.
- While a shape is drawing, Forward, Left and Right do nothing (a stray touch used to restart the drawing); Centre still stops it.
- `kc`, `kb` and `kw` at the top come from the pen position and the calibration: `kc` = 10 × pen speed 90; `kb` = 10 × 90 × sideways offset ÷ forward offset; `kw` = 10 × 90 × 95.3 mm ÷ (2 × forward offset). Offsets are in mm from the centre hole, left and forward positive: now +1 and −45. 95.3 mm = speed ÷ turn rate for turns on the spot, from the spin test with the printed pen sleeve. With the pen straight behind the centre, `kb` is almost 0 and every corner starts as a turn on the spot. The heading update `(r - l) * 86 / 49` is the turn per step per unit of wheel difference. If the pen moves, only `kb` and `kw` change. The tables use 0.321 mm per wheel unit per second; if the pen speed changes, the table changes too.

## Calibrating with the side pen (`shinchan_calibrate_side.aesl`)

For the earlier side pen, 15 cm to the left; kept for reference. Tests for the robot with the side pen and its extra weight, with no pen in the centre hole. A turn on the spot swings the side pen along a 15.7 cm-radius arc around the centre hole, so these tests use turns as circles to measure. Preview with the paper each test needs: [`docs/calibration_side_expected.svg`](docs/calibration_side_expected.svg).

| Button | Test | Draws | Paper | Measures |
|---|---|---|---|---|
| Forward | T1 fast lines | Forward 3, 6, 12 cm at 150 and 12 cm at 300 with stop dots, a half circle (180° turn), then the same backwards on a parallel line about 30 cm away | 49 × 93 cm | Speed forward and backward, start lag, the pen's sideways distance |
| Left | T2 turn circles | Four 90° right turns (two fast, two slow) with a dot after each: a 31 cm circle. Then 40 cm straight and four 90° left turns | 49 × 89 cm | Right and left turn times at speeds 150 and 60, the pen's exact distance from the centre hole |
| Right | T3 slow lines | Like T1 at speed 60: 4, 7, 15 cm forward, 180° turn, the same backwards | 49 × 79 cm | Speed at slow wheel speeds, which the side-pen drawings use a lot |
| Centre | Stop | | | |

Robot facing up, side pen on the start point. Start the pen 10 cm from the left edge of each test's area, 9 cm from its bottom (T1 and T3) or 20 cm (T2). On a 100 × 173 cm sheet: T1 and T3 one above the other on the left half, T2 on the right half. Photograph each test from straight above with a ruler next to it.

## Calibrating the outside-pen shapes (`shinchan_calibrate_offset.aesl`)

The outside-pen shape program with the figures of the first calibration instead of the shapes: a line, two squares and three circles. The steering, `kc`, `kb`, `kw` and the heading update are the same as in `shinchan_shapes_offset.aesl`, so the figures go wrong in the same way the shapes do, but on simple figures it is easy to see how. Preview with start points and paper: [`docs/calibration_offset_expected.svg`](docs/calibration_offset_expected.svg).

| Button | Test | The pen draws | Paper | Pen start: from the left edge, from the bottom edge | Time |
|---|---|---|---|---|---|
| Forward | T1 line | One line to the right: 3, 6 and 12 cm, with an ink dot between the parts | 32 × 21 cm | 9 cm, 7 cm | 10 s |
| Left | T2 squares | Two 12 cm squares touching at the start: up-right with right turns, then down-left with left turns | 41 × 46 cm | 20 cm, 20 cm | 36 s |
| Right | T3 circles | A line to the right with three circles sitting on it, 3, 6 and 9 cm across, each drawn counter-clockwise | 41 × 30 cm | 11 cm, 14 cm | 29 s |
| Centre | Stop | | | | |

Robot facing up (towards the top edge of the paper, square to it), pen tip on the start point, battery full. While a test is drawing, Forward, Left and Right do nothing; Centre still stops it. The light is green, blue or purple while drawing. The paper sizes include the robot's body swinging around the drawing. To start from the computer: `./thymio.sh set j=0 e=21 n=0 p=0 th=0 hq=0 la=0 ra=0 timer.period=2000,0` (T1), with `j=21 e=42` (T2) or `j=42 e=63` (T3). How the photos are used: [`docs/calibration.md`](docs/calibration.md#side-pen-shapes-line-squares-and-circles-2026-10-28-shinchan_calibrate_offsetaesl).

## Continuing with an AI collaborator

Start with [`docs/handoff.md`](docs/handoff.md), then inspect the specific `.aesl` file before editing it. The calibration values in the source files are authoritative; older prose may describe an earlier experiment. The helper can be run on a connected robot or simulator. Example requests:

- "Load the bot on the simulator and tell me what it's doing."
- "The two robots are 5 cm apart now. Read the sensors and set the thresholds."
- "Record a 3-minute chase and update the trail picture."

Record what the physical robot actually drew or sensed, including the paper surface, pen position, motor settings, and measured error. Keep measured results separate from model predictions.
