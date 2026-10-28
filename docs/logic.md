# How the programs think

Main Aseba programs and calibration sketches:

| Program | What it is |
|---|---|
| `shinchan_bot.aesl` | The Shin-chan robot: hunts, chases, taunts, avoids, and draws underpants when bored. |
| `shinchan_drawings.aesl` | Drawing only: a button picks a spiral, a flower or underpants. |
| `shinchan_shy.aesl` | Explore open space, draw a cloud, maneuver around slow obstacles, and escape hazards. |
| `calibration/offset_pen/cloud_offset_test.aesl` | Standalone cloud drawing that accounts for a pen forward and right of the wheel axle. |
| `sim_victim.aesl` | A wandering robot for Shin-chan to chase in the simulator. |

`shinchan_bot.aesl`, `shinchan_drawings.aesl`, and the cloud inside `shinchan_shy.aesl` assume a centered pen. The standalone offset-pen cloud uses a separate pen-tip motion calculation. See [the handoff](handoff.md) for current parameters and integration status.

---

## shinchan_bot.aesl

### Flowchart

```
                         START
                           |
                           v
     +-------------> SEARCH (blue)
     |               snake forward in S-waves
     |                 |          |           |
     |   something in front   something     17 s and
     |                 |       behind       nothing seen
     |                 |          |           |
     |                 |          v           v
     |                 |     RECOVER       BORED (cyan)
     |                 |     (yellow)      draw underpants
     |                 |                    |         |
     |                 |          something in front  drawing done
     |                 |                    |         |
     |                 v                    |         +--> SEARCH
     |            PURSUE (green)  <---------+
     |            steer at it, speed up the longer it runs
     |              |                   |
     |      close enough,          lost it
     |      or touching it              |
     |              |                   v
     |              |            RECOVER (yellow)
     |              |            spin toward where it went
     |              |              |                |
     |              |       found it again     2.5 s, nothing
     |              |              |                |
     |              |              +--> PURSUE      +--> SEARCH
     |              v
     |        TAUNT (magenta)
     |        stop 1 s, spin 1 s, run away 2 s
     |              |
     +--------------+

  ANY TIME (except while chasing, and during the taunt's stop and spin):
     touching something --> AVOID (red)
                            back off and turn away, at least 1.5 s
                            and until nothing is close --> SEARCH
```

The state number is also the LED colour: red = 4, green = 2, blue = 1, added together.
SEARCH 1, PURSUE 2, BORED 3, AVOID 4, TAUNT 5, RECOVER 6.

### Pseudo code

```
settings (change live with "thymio set"):
    detect = 700     reading that starts a chase          (about 13 cm)
    lost   = 500     reading below which the target is lost
    close  = 2500    reading that counts as caught          (about 7 cm)
    hard   = 4000    reading that means touching            (about 2 cm)
    clear  = 1500    AVOID ends once everything is below this
    bored  = 172     ticks of SEARCH (17.2 s) before drawing
    t90, cm          drawing timings: ms per 90 degree turn, ms per cm

start: state = SEARCH

EVERY SENSOR TICK (10 times a second):
    front   = strongest of the 5 front sensors
    rear    = strongest of the 2 back sensors
    nearest = stronger of front and rear
    bearing = where the front reading is centred, -200 (left) .. +200 (right)

    if nearest > hard:                         touching something
        if chasing:  state = TAUNT             caught it
        else if not avoiding and not in the taunt's stop/spin:
                     state = AVOID

    if the state just changed:
        age = 0
        set the top LED colour from the state number
        wavy = new random number               used by SEARCH and PURSUE
    age = age + 1
    drive = 0, turn = 0

    SEARCH:
        turn  = +160 or -160, flipping every 1.6 s,
                plus a small random lean (-15 .. +15) from wavy
        drive = 200
        if front >= detect:    state = PURSUE
        else if rear >= detect: remember which back side; state = RECOVER
        else if age >= bored:   start the underpants drawing; state = BORED

    BORED:
        (the drawing timer drives the wheels)
        if front >= detect:    state = PURSUE  (abandon the drawing)

    PURSUE:
        if front < lost:       state = RECOVER
        else:
            remember the bearing's side
            turn = bearing
            if wavy is negative (half the chases): turn += 200 or -200, flipping every 0.8 s
            drive = (close + 200 - front) / 8 + age * 4, at most 400
                    (slower as the gap closes, faster the longer the chase lasts)
            if front >= close: state = TAUNT

    RECOVER:
        spin toward the remembered side
        if front >= detect:    state = PURSUE
        else if age >= 25:     state = SEARCH

    TAUNT:
        age  0-9:   stand still
        age 10-19:  spin on the spot (about 180 degrees)
        age 20-39:  drive straight away
        age 40:     state = SEARCH

    AVOID:
        turn  = away from the side with more readings
        drive = (rear - front) / 14     backwards if the front is blocked,
                                        forwards if the back is, nothing if both
                                        (boxed in: spins on the spot)
        if nearest < clear and age >= 15: state = SEARCH

    if not BORED: set the wheels to drive + turn (left) and drive - turn (right)

DRAWING TIMER (only while BORED), one step each time it fires:
    underpants = 12 steps: a move, then a 90 degree right spin, six times
        moves: straight 120 mm, straight 40 mm, quarter arc, straight 25 mm,
               quarter arc, straight 40 mm
        straight: both wheels 150 for mm * cm / 10 ms
        arc:      left wheel stopped, right 150, for 2 * t90 ms
        spin:     left 150, right -150, for t90 ms
    after step 12, or if no longer BORED: stop the timer; if still BORED, state = SEARCH
```

---

## shinchan_shy.aesl

The shy program is separate from the hunter bot. `state` is 1 EXPLORE, 2 DRAW, or 3 AVOID; a maneuver remains in EXPLORE. `timer.period[0] = 100` provides the exploration clock, while timer 1 sequences cloud arcs, turns, wiggles, and escape phases without blocking sensor events.

```text
START -> EXPLORE
  front moderately close -> maneuver toward the less occupied side, up to 3 s
  rear moderately close -> move forward faster
  8 s of exploration with a clear path -> DRAW cloud

ANY ACTIVE STATE:
  sustained dark ground, very close front, or rapid front approach
    -> AVOID: backward wiggle -> 180-degree turn -> forward shot
  very close or rapidly approaching rear
    -> AVOID: forward wiggle -> forward shot
  front hazard during an escape -> BLOCKED -> backward wiggle -> 90-degree turn
    toward the less occupied side -> forward shot; repeat if blocked again
  front and rear both occupied -> wait for rear clearance before retreating

DRAW: six counterclockwise semicircles with clockwise turns between them;
      a hazard interrupts the cloud, and the next draw starts from arc 1.
CENTER: pause or resume. A paused escape stops the motors.
```

The apparent closing-rate cue compares raw proximity values across about three sensor updates. It does not estimate object speed in physical units. Two consecutive rapid rises are required. A slow front approach gets a steering attempt first; a failed attempt or hard threshold starts escape. The ground edge needs ten consecutive low readings in normal movement and two during an escape. The drawing code uses centered-pen radii and in-place turns, so it does not yet draw the intended cloud with a rigid offset pen.

`shinchan_submit.aesl` uses the same centered-pen cloud and three escape variations. WANDER replaces EXPLORE, and SHIVER replaces wiggle. Timer 1 steps through the six cloud arcs, settles, and clockwise turns while proximity events can interrupt drawing. Both programs use `turn_180_ms = 1200` and `turn_90_ms = 600` as starting estimates for turns at motor targets of magnitude 500.

## Offset-pen cloud test

`calibration/offset_pen/cloud_offset_test.aesl` keeps a running estimate of robot heading. Every 50 ms it takes the desired tangent of the next cloud semicircle, resolves that pen-tip velocity into forward and sideways components relative to the robot, and sets both wheel targets. For forward pen offset `f`, right offset `r`, axle speed `v`, and angular speed `w`, pen-tip velocity is `(v + r*w)` forward and `f*w` left. The script solves these equations for wheel commands, so it does not pivot in place at each lobe join. It has no sensor feedback for the drawn line or actual heading; motor lag, slip, and pen drag can change the result. This standalone sketch does not include the shy bot's exploration and avoidance logic.

---

## shinchan_drawings.aesl

### Flowchart

```
   button pressed --> wait 1 s --> draw that shape step by step --> stop
       forward = spiral (200 steps of 0.1 s)
       left    = flower (20 steps)
       right   = underpants (12 steps)
       centre  = stop now
```

### Pseudo code

```
settings: t90 = 1244 (ms per 90 degree spin), cm = 167 (ms per cm)

BUTTON forward / left / right / centre:
    n = 200 / 20 / 12 / 0           number of steps (0 = stop)
    s = 0, wheels off, run the step timer once after 1 s

STEP TIMER:
    if s < n:
        spiral (n = 200):  left 400, right 3 * s - 400, for 0.1 s
                           (starts as a spin on the spot, opens into wider coils)
        flower (n = 20):   5 petals, each 4 steps:
                           quarter arc (left stopped, right 150, 2 * t90)
                           spin left 90 degrees (t90)
                           quarter arc
                           spin left 162 degrees (t90 * 9 / 5)
        underpants (12):   same steps as in shinchan_bot
        s = s + 1, run the timer again after that step's time
    else:
        wheels off, timer off
```

---

## sim_victim.aesl

```
EVERY SENSOR TICK:
    turn = +32 or -32, flipping every 6.4 s     (gentle wandering curve)
    if the front reading > 1500:                something ahead
        turn 200 away from the side with more readings
    wheels: 180 + turn (left), 180 - turn (right)
```
