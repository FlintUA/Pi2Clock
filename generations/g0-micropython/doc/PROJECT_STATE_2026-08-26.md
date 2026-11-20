# Speaking Timer-Clock - Project State (2026-08-26)

## Overview
Migration from legacy v1 (monolithic `speaking_timer_clock.py`) to modular v2 (async, hardware abstraction, priority speech queue, JSON config, multi-language) on Raspberry Pi Pico (RP2040).

## Hardware
- **MCU**: Raspberry Pi Pico (RP2040)
- **RTC**: DS1302 (CLK=GP2, DAT=GP5, RST=GP4)
- **LCD**: I2C 1602 via PCF8574 (SDA=GP0, SCL=GP1)
- **DFPlayer Mini**: UART0 (TX=GP16, RX=GP17, BUSY=GP18)
- **Encoders**: 2x Rotary (ENC1: DT=GP14, CLK=GP15, SW=GP20; ENC2: DT=GP11, CLK=GP10, SW=GP19)
- **Buttons**: 5x (GP28, GP21, GP22, GP26, GP27)

## Completed Work

### 1. SD Card Migration ✅
**Script**: `migrate_sdcard_pc.py`
- Legacy folders 01-21 preserved at root (DFPlayer only sees root folders)
- New structure created: `/sd/tts/`, `/sd/music/`, `/sd/chimes/`, `/sd/beeps/`
- Folder mapping verified:
  - 01→tts/ru/hours, 02→tts/ru/minutes, 03→tts/ru/days, 04→tts/ru/months, 05→tts/ru/years, 06→tts/ru/weekdays
  - 07→tts/ru/phrases (renumbered), 08→music (renamed), 09→tts/ru/numbers_0_30
  - 11→tts/de/hours, 12→tts/de/minutes, 13→tts/de/days, 14→tts/de/months, 15→tts/de/years, 16→tts/de/weekdays
  - 17→tts/de/phrases (renumbered), 18→chimes (renamed), 19→beeps (renamed)

### 2. Missing Phrase Tracks Created ✅
**Scripts**: `create_missing_phrases.py` (legacy folders), `create_missing_phrases_v2.py` (v2 structure)

**RU phrases (folder 07 & tts/ru/phrases)**:
- 001=alarm, 002=timer_done, 003=chime_hour, 004=chime_half, 005=volume_on, 006=volume_off
- 007=menu_enter (copied from 005), 008=menu_exit (copied from 006), 009=settings_saved (copied from 010)
- 010=timer_set, 011=timer_cancelled, 012=work_start, 013=short_break, 014=long_break (copied from 013)

**DE phrases (folder 17 & tts/de/phrases)**:
- Same structure, fallbacks from existing tracks

### 3. Code Fixes Applied ✅

| File | Issue | Fix |
|------|-------|-----|
| `main.py` | Encoder press/release not forwarding to ButtonManager | Added `on_enc_left_press/release` → `buttons.on_enc_left_press/release()` |
| `main.py` | Constant "ноль часов" spam | Added `time_valid` check rejecting h=0,m=0,s=0; `_last_hour_chime`/`_last_half_chime` flags |
| `main.py` | Typo `speech.speech.speak_phrase` | Fixed to `speech.speak_phrase` |
| `clock.py` | RTC returns 0:0:0 treated as valid time | `now()` rejects 0:0:0, falls back to soft_time |
| `display.py` | Display "каша" (garbage) | Simplified `draw_main_screen` to single `set_buffer_line` calls |
| `rotary_encoder.py` | RuntimeError: schedule queue full | Added try/except around `micropython.schedule` |
| `music.py` | `random.shuffle` not available | Manual Fisher-Yates implementation |
| `alarms.py` | `@dataclass` not supported | Converted to regular class with `__init__` and `to_dict()` |
| `lcd_i2c.py` | `LCD_FUNCTION_RESET` missing, `str.ljust` not available | Used 0x03 constant, added `_pad_text()` method |
| `patch_micropython.py` | typing, dataclasses, enum, asyncio missing | Stripper converting to plain classes |

### 4. Architecture v2 Components ✅

**Hardware Abstraction** (`speaking_clock/hardware/`):
- `dfplayer.py` - Async DFPlayer with command queue, busy pin monitoring
- `lcd_i2c.py` - Buffered LCD rendering, custom chars, backlight PWM
- `rotary_encoder.py` - Interrupt-driven quadrature, acceleration, debounced button
- `buttons.py` - 5 buttons + 2 encoders, short/long press detection
- `rtc_ds1302.py` - DS1302 driver with calibration

**Core Logic** (`speaking_clock/core/`):
- `clock.py` - Central timekeeper, RTC sync, DST, timezone, soft_time fallback
- `speech.py` - Priority queue (CRITICAL/HIGH/NORMAL/LOW), interruptible playback
- `alarms.py` - Multiple alarms with day masks, sounds, labels, snooze
- `timer.py` - Countdown timer + Pomodoro timer
- `music.py` - Playlist management, shuffle, folder playback

**Locale** (`speaking_clock/locale/manager.py`):
- Multi-language (RU/DE/UA)
- DFPlayer folder mapping per language
- Phrase track mapping with fallbacks
- New API: `get_phrase_sequence()`, `get_chime_sequence()`, `get_beep_sequence()`

**Storage** (`speaking_clock/storage.py`):
- JSON config with atomic writes
- Auto-migration, defaults, debounced saves

**Config** (`speaking_clock/config.py`):
- All pins, defaults, constants centralized

## Current Issue
**Error**: `ValueError: need more than 3 values to unpack` at line 444 in `_periodic_tasks()`

**Root Cause**: MicroPython bytecode cache (`.pyc` files in flash) still contains old code. The fix is in source but cached bytecode executes.

**Fix Applied in Source**:
```python
# Line 444 in main.py - CHANGED FROM:
_, _, _, _, h, m, s = self.clock.get_time_tuple()
# TO:
h, m, s = self.clock.get_time_tuple()
```

**Required Action**: **Hard reset Pico** (unplug USB, wait 2s, replug) to clear bytecode cache. Soft reboot in Thonny is insufficient.

## Files to Verify on Pico After Hard Reset
All these should be current (copied 2026-08-26):
- `/main.py`
- `/speaking_clock/__init__.py`
- `/speaking_clock/config.py`
- `/speaking_clock/storage.py`
- `/speaking_clock/hardware/dfplayer.py`
- `/speaking_clock/hardware/lcd_i2c.py`
- `/speaking_clock/hardware/rotary_encoder.py`
- `/speaking_clock/hardware/buttons.py`
- `/speaking_clock/hardware/rtc_ds1302.py`
- `/speaking_clock/core/clock.py`
- `/speaking_clock/core/speech.py`
- `/speaking_clock/core/alarms.py`
- `/speaking_clock/core/timer.py`
- `/speaking_clock/core/music.py`
- `/speaking_clock/locale/manager.py`
- `/speaking_clock/ui/display.py`

## Remaining TODOs (Not Blocking)
- [ ] First boot wizard (time/date setting UI)
- [ ] Menu system (MenuSystem, ScreenManager classes)
- [ ] Time/date setting via UI
- [ ] Alarm editing via UI
- [ ] RTC calibration via UI
- [ ] Settings persistence for all new options
- [ ] Music folder scanning for legacy structure
- [ ] Display screens for all menu items

## Expected Behavior After Hard Reset
1. Boots without unpacking error
2. Enters main loop successfully
3. No "ноль часов" spam (RTC 0:0:0 rejected)
4. Left encoder button toggles mute → speaks "volume_on"/"volume_off"
5. Clean display (no garbage characters)
6. Hourly/half-hourly chimes only when valid time set
7. All phrase keys resolve via fallback system

## Migration Scripts Location
- `migrate_sdcard_pc.py` - Full SD restructure (run on PC)
- `create_missing_phrases.py` - Legacy folders 07/17 phrase tracks
- `create_missing_phrases_v2.py` - v2 structure tts/*/phrases tracks
- `patch_micropython.py` - Auto-patch for MicroPython compatibility

## Running Migration (if needed again)
```bash
# On PC with SD card in reader (E: drive):
python migrate_sdcard_pc.py --execute --source E: --dest E:
python create_missing_phrases.py --execute --drive E:
python create_missing_phrases_v2.py --execute --drive E:
```

## Testing Checklist After Hard Reset
- [ ] No traceback on boot
- [ ] Main screen shows time/date
- [ ] Left encoder: rotate = volume, press = mute toggle (speaks phrase)
- [ ] Right encoder: rotate = timer adjust, press = start/stop timer
- [ ] Btn1: short = music play/pause, long = shuffle
- [ ] Btn2: short = speak time, long = cycle language (RU→DE→UA)
- [ ] Btn3: short = chime demo, long = menu (TODO)
- [ ] Btn4: short = timer preset 1 (5/10/15), long = reset timer
- [ ] Btn5: short = timer preset 2 (30/45/60), long = start Pomodoro
- [ ] Alarms trigger at set times
- [ ] Quiet mode activates at 22:00-07:00