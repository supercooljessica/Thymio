hiii I am yoyo

# Thymio

My Thymio robot project: a **hunter** program that searches for another Thymio, chases it and avoids crashes, plus tools to test it in the simulator and control the robot from the terminal. Works on **Windows** and **macOS**.

## What's in here

| File | What it is |
|---|---|
| `thymio_hunter.aesl` | The hunter program (Aseba code). Open it in Aseba Studio. |
| `playgrounds/thymio.playground` | A simulator arena with one Thymio. |
| `tools/thymio.py` | Command-line helper: load code, read sensors, change settings. |
| `thymio.cmd` / `thymio.sh` | Launchers for the helper (Windows / macOS). |
| `requirements.txt` | Python packages the helper needs (`tdmclient`). |

## Software you need

1. **[Thymio Suite](https://www.thymio.org/download-thymio-suite/)** (Windows, macOS, Linux). It includes Aseba Studio, VPL, Scratch, the simulator, and the Thymio Device Manager that connects everything to the robot. The download page asks you to sign up; "Skip and download" also works.
2. **Python 3**, only for the command-line helper.
   - **Windows:** install from [python.org](https://www.python.org/downloads/) and tick **"Add python.exe to PATH"** in the installer.
   - **macOS:** usually already there. Check with `python3 --version`.

## Run the simulator

1. Open **Thymio Suite**, choose **Aseba Studio**, then click **"launch a simulator"**.
2. A file picker opens and asks for an arena. Pick `playgrounds/thymio.playground` from this folder.
   - **macOS:** Thymio Suite comes with no arenas, so use this one. Tip: press **Cmd+Shift+G** in the picker and paste the file's path.
   - **Windows:** the picker may open Thymio Suite's own examples folder. Those arenas work too. To use ours, paste this folder's path into the picker's address bar.
   - Starting the simulator with an arena file from the command line doesn't work (you get an empty grey world). Always use the picker.
3. **Allow network access** when asked, or Thymio Suite won't see the simulated robot.
   - **macOS:** "Allow AsebaPlayground to find devices on local networks?" → **Allow**. To fix it later: System Settings → Privacy & Security → Local Network.
   - **Windows:** Windows Firewall prompt → **Allow**. To fix it later: Windows Security → Firewall & network protection → Allow an app through firewall.
4. Back in Thymio Suite, select **"Thymio II 0 on <your computer>"**, then click **Program with Aseba Studio**.
5. In Aseba Studio, open `thymio_hunter.aesl`, then click **Load** and **Run**.

For a **real robot**, plug in the Thymio with USB (or the wireless dongle). It appears in the same list.

## Control the robot from the terminal

Open a terminal in this folder. The first run sets up a Python environment in `.venv` automatically.

| | Windows (Command Prompt) | Windows (PowerShell) | macOS |
|---|---|---|---|
| Show robots | `thymio list` | `.\thymio list` | `./thymio.sh list` |

All commands (written the Windows way, swap in `./thymio.sh` on macOS):

| Command | What it does |
|---|---|
| `thymio list` | Show connected robots, real and simulated |
| `thymio load thymio_hunter.aesl` | Compile and start a program |
| `thymio stop` | Stop the program |
| `thymio read prox.horizontal state` | Print variables once |
| `thymio watch prox.horizontal state --seconds 5` | Print variables live (Ctrl+C to stop early) |
| `thymio set detect_threshold=800` | Change a variable while it runs |
| `thymio set leds.top=0,32,0` | Set an array (comma-separated) |

If several robots are connected, add `--robot` and part of the name, e.g. `thymio --robot "Thymio II 0" read state`.

**Rules:**
- Thymio Suite must be open; the helper connects to robots through it.
- Only one program can control a robot at a time. Disconnect Aseba Studio before using `load`, `stop` or `set`.

## Working with Claude Code

Claude Code can run the helper for you. Ask in plain words, for example:

- "Load the hunter on the simulator and tell me what it's doing."
- "The two robots are 5 cm apart now. Read the sensors and set the thresholds."
- "Change the search speed to 300 and run it again."

Describe what the real robot does, or drag in photos and screenshots; Claude Code can't watch video.

## The hunter program

The top LED shows what the hunter is doing:

| State | Color | Meaning |
|---|---|---|
| 0 SEARCH | blue | Spin a full circle, then search in a growing square spiral |
| 1 PURSUE | green | Chase the other robot, slowing down as the gap closes |
| 2 RECOVER | yellow | Lost it: turn toward the side it was last seen, then back to SEARCH |
| 3 TAUNT | magenta | Caught it: pause 1 s, spin around, drive away, then SEARCH again |
| 4 AVOID | red | Something too close: back away, or drive forward to escape a robot behind |

The sensor thresholds and turn timings at the top of the file are raw IR values and timer ticks, not millimetres or degrees. They need calibrating with the real robots.
