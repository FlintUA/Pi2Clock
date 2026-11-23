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

**Review:** the later wiring plan (2026-11-23) keeps **two encoders** (TIMER and VOLUME), as in G1. Two encoders keep direct volume control during music, which the concept itself lists as important. Decide on the prototype: one encoder (simpler panel) or two (G1 habits, direct volume).

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

| Event | Proposed WS2812 behaviour |
| --- | --- |
| Touch confirmation | Short soft flash (can be disabled) |
| Silent mode on | Short blue confirmation |
| Timer finished | Orange pulsing until acknowledged |
| Alarm ringing | Red pulsing in silent mode |
| Bluetooth connected | Short green signal |
| Normal operation | Off or barely visible |

Colours are preliminary and later configurable.

- **Silent mode** turns off spoken and sound notifications but not the events; OLED and WS2812 still show them.
- **Night mode** dims OLED and WS2812 (or turns them off on a schedule) independently of silent mode.
- An alarm or finished timer shows a **priority notification** that can be acknowledged without finding its function in the menu, without accidentally acknowledging another event.

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

1. Daily use with one encoder, especially volume during music (or two encoders, see above).
2. Readability of the 256×64 screen from a distance; layout of three timers.
3. Whether five touch keys are enough; long touches and false triggers.
4. Menu behaviour with simultaneous notifications.
5. OLED brightness by day, idle and at night; WS2812 brightness in silent mode.
6. One driver and UI for a later 5.5" SSD1322.

## Decisions

| Decision | Status (2026-11-13 concept) |
| --- | --- |
| One central encoder instead of two | Chosen for testing — **superseded by the two-encoder wiring plan, to be decided on the prototype** |
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
