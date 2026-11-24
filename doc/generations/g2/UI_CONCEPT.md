# G2 user interface concept

> **Status (2026-11-23): preliminary concept for testing on the prototype.** Translated and condensed from the user's early document `PicoClock_V4_UI_Control_Concept.md` of 2026-11-13 ([original](sources/references/early_V4_concepts/PicoClock_V4_UI_Control_Concept.md)), written when the next device was still called "V4". Where it differs from the newer [HARDWARE.md](HARDWARE.md), the newer document wins; differences are marked **Review**.

Purpose: an autonomous talking desk clock for kitchen, bedroom, hallway and desk.

## Controls

The 2026-11-13 concept proposed **one central encoder with push button** for navigation and value changes, plus five TTP223 touch sensors for quick actions (chosen because they are silent):

- Rotate outside an editor — choose a function or menu item.
- Short press — enter the item or confirm a value.
- Rotate inside an editor — change the selected value.
- Short press again — confirm and save (simple values) or go to the next field (multi-field editors).
- Long press — back to the home screen, leaving any editor safely.

**Decision (2026-11-23):** G2 uses **two encoders** (TIMER and VOLUME), as in G1. A one-encoder variant is planned only after the two-encoder G2 release; the UI state machine and input layer must keep it possible.

| Element | Count | Purpose |
| --- | ---: | --- |
| Encoder with push button | 1 or 2 | Navigation, adjustment, confirmation (+ volume) |
| TTP223 | 5 | Silent quick-access keys |
| WS2812 | 4 | Touch confirmation, silent notifications, status |
| OLED SSD1322 3.12" 256×64 | 1 | Main graphic feedback (two modules ordered; a 5.5" SSD1322 later possible with the same driver) |

## Screen hierarchy

```text
HOME
  |
  +-- rotate --> SELECT_FUNCTION
  |               +-- Volume   --> EDIT_VOLUME
  |               +-- Timers   --> TIMERS_OVERVIEW --> TIMER_DETAIL / EDIT
  |               +-- Alarms   --> ALARMS_OVERVIEW --> ALARM_EDITOR
  |               +-- Music    --> MUSIC_PLAYER
  |               +-- Weather  --> WEATHER_VIEW
  |               +-- Bluetooth --> BT_MENU
  |               +-- Settings --> SETTINGS_MENU
  |
  +-- TTP223 --> quick actions / direct jump to a function
  |
  +-- timer finished / alarm --> PRIORITY_NOTIFICATION
```

The current context is always visible on the OLED, every nested page has a clear way back, and key events are reachable without deep menus.

**Home screen priorities:** large time; date and weekday; small Wi-Fi and Bluetooth status; next alarm; the active timer or the number of running timers; weather when a current forecast exists. Not everything fits 256×64 permanently; details are one step away. The OLED runs dimmed when idle and brightens while being operated; night mode and silent mode are independent.

**Volume:** applied immediately while rotating; a press only ends the mode; bar and number on the OLED; separate levels for the built-in speaker and Bluetooth (as in G1); predictable exit by long press or timeout (about 5 s, to be tested). Quick volume access during playback should stay available through a touch key.

## Three independent timers

**TIMERS_OVERVIEW** shows all running timers at once when two or three run; the one with the least remaining time is large, the others compact; a finished but unacknowledged timer has top priority.

```text
TIMERS        3 ACTIVE
T1
04:32      T2  12:45
           T3  28:16
```

- Rotate in the list to choose T1/T2/T3; press to open it.
- In the editor rotation changes the duration of a **stopped** timer only; rotation never changes a running timer by accident.
- Start, pause, stop and reset are explicit commands.
- Several timers finishing together are announced one after another.
- The finished message names the timer number and its **initial** duration: «Первый таймер на 14 минут завершён» ("The first timer of 14 minutes has finished"); store `initial_duration` separately from `remaining_duration` ([VOICE.md](VOICE.md#three-timers)).

## Touch keys

The five TTP223 give one-touch access to important actions; they do not replace the encoder logic. Preliminary mapping (not approved):

| Sensor | Possible quick action |
| --- | --- |
| 1 | Timers / timer screen |
| 2 | Volume / mute |
| 3 | Alarms / acknowledge while ringing |
| 4 | Settings / mode |
| 5 | Back / cancel / home |

**Review:** [HARDWARE.md](HARDWARE.md#45-five-ttp223-touch-sensors--not-like-mechanical-buttons) keeps the G1 roles ALARM, MODE, MINUS, SETTINGS/PLUS, TIMER_MODE on GP21–GP28. The concept asks to keep the familiar meanings of the five G1 buttons as far as possible and to inventory old combinations such as ALARM hold for the music player ([G1 controls](../../CONTROLS_AND_MODES.md)). The final mapping is decided on the prototype.

Required TTP223 tests: through PLA/PETG of the chosen panel thickness (start with 1–2 mm); short and long touches without false repeats; wet fingers and interference from supply, audio and WS2812; optional light confirmation.

## Notifications, silent and night mode

- **Silent mode** turns off spoken and sound notifications but not the events; OLED and WS2812 still show them.
- **Night mode** dims OLED, WS2812 and the key backlight (or turns them off on a schedule) independently of silent mode.
- An alarm or finished timer shows a **priority notification** that can be acknowledged without finding its function in the menu, without accidentally acknowledging another event.

## Light signals and accessibility

Added on 2026-11-24. The four WS2812 are the clock's **silent notification channel**. For deaf and hard-of-hearing users they replace sound, so the signals must be simple, consistent and understandable without the manual. Colours and timings are a plan, to be tuned on the prototype; all signals are drawn by firmware (individually addressable RGB, PIO output, negligible CPU load).

### Reference practice

- **Google Nest Audio** uses four lights with few motion types and fixed meanings: all four pulsing quickly (listening), light running left to right (thinking), running back and forth (connecting to Wi-Fi), filling left to right (update), all slowly pulsing (alarm or timer ringing), one steady light (notification waiting), one to four lights as a volume scale, four orange lights (microphone off) ([Google: lights on your speaker](https://support.google.com/googlenest/answer/7073219)).
- **Alerting systems for deaf people** (Bellman Visit, Lisa, Signolux) give every source its own flash pattern and show a coloured symbol for the source on the receiver ([NDCS](https://www.ndcs.org.uk/information-and-support/parenting-and-family-life/families-magazine/technology-articles/staying-safe-with-home-alerting-systems)); for sleep they add a vibrating pad.
- **Visible fire alarms** for deaf occupants flash white at 1–2 flashes per second ([ADA National Network](https://adata.org/?p=1539)); flash rates above that range raise the risk of photosensitive seizures.
- **WCAG 2.3** forbids flashing more than three times per second and notes that saturated red flashing is the most critical ([W3C](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes.html)).
- **Light alone wakes poorly:** in a Gallaudet study strobes were the weakest waking signal ([Gallaudet TAP](https://tap.gallaudet.edu/Emergency/Nov05Conference/Presentations/JDuBois_files/textonly/slide20.html)); hence the vibration output on GP5.
- **Indicator colours** (IEC 60073 / EN 60204-1): red emergency, yellow abnormal / attention, green normal, blue action required, white neutral.

### Rules

1. **Rhythm = urgency, colour = category, number of flashes or LED position = number** (of a timer or alarm). Colour is never the only carrier of meaning (about 8 % of men confuse red and green).
2. **At most two flashes per second**; prefer smooth pulses to hard flashes; never flash saturated red quickly.
3. **The LEDs get attention, the OLED gives the details** in large text (for example `TIMER 2 FINISHED`).
4. **Important events stay visible until acknowledged**; a missed event leaves a mark until it is seen.
5. **Few patterns, each with one permanent meaning**, plus a legend card in the manual.
6. Gamma-corrected brightness for smooth pulses, a diffuser over the LEDs, software brightness limits (night, current, heat).

### Effect library

| Effect | Motion | Use |
| --- | --- | --- |
| Run right / run left | One dot with a fading tail | Searching / connecting a speaker; cancel or back |
| Back and forth | Dot bouncing between the ends | Connecting to Wi-Fi |
| Fill | 1 → 4 one after another | Loading, OTA update, volume scale (1–4 steps) |
| Countdown | 4 → 0 going out | Last seconds of a timer (visual counterpart of the warning beeps) |
| Slow breathing | All together, smooth | Attention without urgency |
| Pulse groups | N short pulses, pause, repeat | Number of the timer or alarm |
| Double flash and fade | All together, once | Command accepted / refused |
| Single steady dot | Static | Something waiting to be seen |
| Rainbow wave | Smooth gradient moving | Start-up, birthday |

### Signal dictionary

| Event | Colour | Pattern | Duration |
| --- | --- | --- | --- |
| Alarm ringing | White, full brightness, all four | Flash once per second (strobe-like) | Until Stop or Snooze |
| Alarm snoozed | Yellow, one LED | Slow breathing | Until it rings again |
| Timer N finished | Orange, all four | Groups of N pulses, pause, repeat | Until acknowledged |
| Last five seconds of a timer | Timer colour | Countdown 4 → 0 | 5 s |
| Birthday | Rainbow | Slow running wave | Until acknowledged or 30 min |
| Missed event | Yellow, one LED | Steady | Until any key is touched; the OLED lists it |
| Action required (no SD card, battery low) | Blue, one LED | Steady | Until resolved |
| Command accepted | Green | Double flash | Once |
| Command not possible | Yellow | Double flash | Once |
| Connecting Wi-Fi or speaker | White | Back and forth | While connecting |
| Hourly signal (optional) | Warm white | One soft wave | Once |
| Volume change | White | Fill 1–4 | About 2 s after the last change |
| Microphone active (later) | White | Fast pulsing (≤ 2 per second) | While recording |

**Option for three timers:** LEDs 1–3 belong to timers 1–3 (each glows dimly in its own colour while running, optionally fading as time runs out, and pulses when it finishes), LED 4 shows alarm, connection and silent-mode states. To be compared with the all-four patterns on the prototype.

### Visual alerts mode

A setting for deaf and hard-of-hearing users: maximum LED brightness; the whole OLED inverts and flashes together with the LEDs; alerts last until acknowledged without time limit; the external alert output (GP5, vibration pad or lamp) runs with alarms and finished timers.

### Beyond the clock: notifications on the phone

For a user who is away from the clock or not looking at it, the clock can send a notification over Wi-Fi to the phone or smartwatch, which then vibrates on the wrist — the "vibration mode" of a phone, carried by a device the user is already wearing. Candidates: a push service such as ntfy, a Telegram bot, or Home Assistant. Planned as a later network function; it must be optional and send nothing without the user's configuration. A vibration motor inside the clock is not planned: on a desk it mostly rattles and is barely felt.

## Event handling rules

1. Standard input events: `ROTATE(+/-)`, `PRESS`, `LONG_PRESS`, `TOUCH_i`, `TOUCH_i_LONG`.
2. A context input manager maps events to the current screen's actions.
3. The selected function and the edited field are always visibly distinct.
4. Running timers, alarms and other critical values change only inside an editor.
5. Multi-step menus never apply unconfirmed changes.
6. Finished timers and alarms appear over menus; the interrupted setting can be continued.
7. Wi-Fi, weather requests and Bluetooth never delay local timers and alarms.
8. Critical operations stay understandable without voice and with the WS2812 off.

## Prototype checks

1. Daily use of the two encoders with the touch keys; notes for the later one-encoder variant.
2. Readability of the 256×64 screen from a distance; layout of three timers.
3. Whether five touch keys are enough; long touches and false triggers.
4. Menu behaviour with simultaneous notifications.
5. OLED brightness by day, idle and at night; WS2812 brightness in silent mode.
6. One driver and UI for a later 5.5" SSD1322.

## Decisions

| Decision | Status (2026-11-13 concept) |
| --- | --- |
| One central encoder instead of two | **Superseded (2026-11-23): two encoders for G2; one-encoder variant after the G2 release** |
| Rotate = choose/change, press = enter/confirm | Main concept |
| Five TTP223 instead of five mechanical buttons | Preferred |
| Four WS2812 for silent notifications | Planned |
| Three timers shown together, nearest large | Planned |
| OLED SSD1322 3.12" 256×64 | Two modules ordered |
| MAX98357A | Module available |
| Final touch-key mapping | Open |
| Time-outs, short/long presses, back scenarios | To be tuned on the prototype |
| Enclosure shape and size | After a hardware test fit |

**Main recommendation:** implement navigation as a **UI state machine** with a separate input layer and a graphics abstraction of the display, so that the hardware variant (one or two encoders, mechanical or touch keys, 3.12" or 5.5" OLED) changes without rewriting the logic.
