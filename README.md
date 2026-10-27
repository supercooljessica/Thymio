hiii I am yoyo

# Thymio: the Shin-chan bot

A Thymio that behaves like Shin-chan: it hunts down whoever is nearby, chases them, taunts them and runs off, and when nobody is around it gets bored and draws underpants on the floor. Plus a drawing program, a simulator setup to test it, and command-line tools. Works on **Windows** and **macOS**.

## What's in here

| File | What it is |
|---|---|
| `shinchan_bot.aesl` | **The robot program.** Search, chase, taunt, avoid, and draw underpants when bored. |
| `shinchan_shy.aesl` | Explore open space, draw small clouds, and escape front, rear, or edge hazards. |
| `shinchan_drawings.aesl` | Drawing only: a button picks a spiral, a flower or underpants. |
| `sim_victim.aesl` | A simple wandering robot for Shin-chan to chase in the simulator. |
| `playgrounds/arena.playground` | Simulator arena: empty 2 × 2 m square, four robot-sized cylinders, Shin-chan in the middle. |
| `playgrounds/arena_chase.playground` | Same arena with a second Thymio (`victim`) 45 cm ahead of Shin-chan. |
| `playgrounds/arena_floor.png` | Floor of both arenas: how far Shin-chan can see (rings around the cylinders, sensor beams at his start) and a 10 cm grid. |
| `docs/logic.md` | **How the programs work:** flowcharts and pseudo code. |
| `docs/chase_trail.svg` | Shin-chan's and the victim's trails in the chase arena, to scale, coloured by mode. |
| `docs/drawings_preview.png` | What the drawing program draws. |
| `docs/arena_floor.svg` | Editable source of the arena floor. |
| `docs/instructions_prompts.rtf` | The original assignment prompts. |
| `tools/thymio.py`, `tools/trail.py` | Command-line helper (see below). |
| `thymio.cmd` / `thymio.sh` | Launchers for the helper (Windows / macOS). |
| `requirements.txt` | Python packages for the Thymio helper and serial bridge. |
| `calibration/` | Pen and motion calibration sketches, grouped by centered or offset pen. |
| `xiao_communication/` | XIAO sketches, USB communication experiments, bridges, dashboards, and setup notes. |

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
| `t90`, `cm` | 1244, 167 | Drawing timing, as in the drawing program below |

In the simulator the robot is a bit slower than these drawing defaults assume; use `thymio set t90=1482 cm=201` there.

## The shy bot (`shinchan_shy.aesl`)

The shy bot explores open space for eight seconds, then draws the six-semicircle cloud from `calibration/centered_pen/cloud_semicircle_test.aesl` at `unit_mm = 20`. It uses the current heading as the cloud's starting direction. When the cloud finishes, a new eight-second exploration session begins. At a moderate front reading it slows down and steers around the clearer side for up to three seconds. A rapid rise in the reading, a very close object, a failed maneuver, or a sustained dark ground reading triggers the backward wiggle, 180° turn, and forward shot. A moderate rear reading makes it move forward a little faster; a rapidly rising or very close rear reading starts a forward wiggle and shot without a turn. Drawing waits while an obstacle is near. Interrupted clouds are abandoned and started fresh after another exploration session.

The main states are explore (green, or yellow while maneuvering), draw (cyan), and avoid (red). Orange means a hazard blocked the planned escape; the robot waits stopped until the front, rear, and ground readings are clear for three sensor updates. The center button pauses (blue) or resumes. During an escape, a newly detected hazard stops the robot instead of launching another escape immediately.

Settings near the top include `front_threshold`, `front_hard`, `rear_threshold`, `rear_hard`, `fast_rise`, `maneuver_fast_rise`, `maneuver_timeout_ticks`, `white_min`, `edge_samples`, `unit_mm`, `t90_ccw`, `t90_cw`, and the wiggle, turn, and shot timings. `fast_rise` is a rise in raw IR readings over roughly three sensor updates; it is an apparent closing-rate cue, not a measurement of an object's speed in millimetres per second. Two consecutive rising readings are required, and the threshold is higher while maneuvering because turning also changes the readings. The normal ground debounce is ten readings, as in the edge test; the faster escape motions use a two-reading edge stop. Try it first with the pen raised and enough room around the robot, then adjust the thresholds and timing on the actual surface.

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
| `t90` | 1244 | ms for a 90° spin | Draw the flower. If the last petal lands past the first, lower `t90`; if it falls short, raise it. |
| `cm` | 167 | ms to drive 1 cm | Draw the underpants and measure the waistband. New `cm` = `cm` × 120 ÷ measured mm. |

For the newer turn, circle, edge, and shy-motion tests, see [`calibration/`](calibration/README.md). The centered-pen turn and shape test assumes the pen is on the wheel axis; the circle and motion tests are also available for an offset pen.

For XIAO and USB communication experiments, see [`xiao_communication/`](xiao_communication/README.md).

## Working with Claude Code

Claude Code can run the helper for you. Ask in plain words, for example:

- "Load the bot on the simulator and tell me what it's doing."
- "The two robots are 5 cm apart now. Read the sensors and set the thresholds."
- "Record a 3-minute chase and update the trail picture."

Describe what the real robot does, or drag in photos and screenshots; Claude Code can't watch video.
