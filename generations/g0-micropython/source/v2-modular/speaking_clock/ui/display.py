"""
Display manager: handles LCD rendering, screens, backlight control.
"""

import time
import asyncio
from speaking_clock.hardware.lcd_i2c import LCD_I2C
import speaking_clock.config as config


class DisplayManager:
    """Manages LCD display with double buffering and screen management."""

    def __init__(self, lcd: LCD_I2C, locale_manager):
        self.lcd = lcd
        self.locale = locale_manager
        self._current_screen = None
        self._screen_stack = []
        self._backlight_on = True
        self._backlight_timeout = config.DISPLAY_TIMEOUT_DEFAULT
        self._last_activity = time.ticks_ms()
        self._show_seconds = config.DISPLAY_SHOW_SECONDS_DEFAULT
        self._brightness = config.DISPLAY_BRIGHTNESS_DEFAULT
        self._custom_chars_loaded = False

        # Status icons (custom characters)
        self._load_custom_chars()

    def _load_custom_chars(self):
        """Load custom characters for status icons."""
        # Speaker (sound on)
        speaker = [
            0b00001,
            0b00011,
            0b00111,
            0b11111,
            0b11111,
            0b00111,
            0b00011,
            0b00001,
        ]
        # Mute (sound off)
        mute = [
            0b00001,
            0b00011,
            0b00111,
            0b11111,
            0b11111,
            0b00111,
            0b00011,
            0b00001,
        ]
        # Bell (alarm)
        bell = [
            0b00100,
            0b01110,
            0b01110,
            0b01110,
            0b11111,
            0b00000,
            0b00100,
            0b00000,
        ]
        # Timer
        timer = [
            0b01110,
            0b10001,
            0b10101,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000,
        ]
        # Music note
        music = [
            0b00001,
            0b00011,
            0b00101,
            0b01001,
            0b01001,
            0b01011,
            0b11011,
            0b01110,
        ]
        # Moon (quiet mode)
        moon = [
            0b00111,
            0b01111,
            0b11110,
            0b11100,
            0b11100,
            0b11110,
            0b01111,
            0b00111,
        ]
        # Up arrow
        up_arrow = [
            0b00100,
            0b01110,
            0b11111,
            0b00100,
            0b00100,
            0b00100,
            0b00000,
            0b00000,
        ]
        # Down arrow
        down_arrow = [
            0b00000,
            0b00100,
            0b00100,
            0b00100,
            0b11111,
            0b01110,
            0b00100,
            0b00000,
        ]
        # Check mark
        check = [
            0b00000,
            0b00001,
            0b00011,
            0b10110,
            0b11100,
            0b01000,
            0b00000,
            0b00000,
        ]

        chars = [speaker, mute, bell, timer, music, moon, up_arrow, down_arrow, check]
        for i, charmap in enumerate(chars):
            if i < 8:
                self.lcd.create_char(i, charmap)

        self._custom_chars_loaded = True

    # Icon indices
    ICON_SPEAKER = 0
    ICON_MUTE = 1
    ICON_BELL = 2
    ICON_TIMER = 3
    ICON_MUSIC = 4
    ICON_MOON = 5
    ICON_UP = 6
    ICON_DOWN = 7
    ICON_CHECK = 8

    def set_screen(self, screen):
        """Set current screen."""
        if self._current_screen:
            self._current_screen.on_exit()
        self._current_screen = screen
        if screen:
            screen.on_enter(self)
        self.mark_dirty()

    def push_screen(self, screen):
        """Push screen onto stack (for dialogs)."""
        if self._current_screen:
            self._screen_stack.append(self._current_screen)
            self._current_screen.on_pause()
        self.set_screen(screen)

    def pop_screen(self):
        """Pop screen from stack."""
        if self._screen_stack:
            old = self._current_screen
            if old:
                old.on_exit()
            self._current_screen = self._screen_stack.pop()
            self._current_screen.on_resume()
            self.mark_dirty()
        else:
            self.set_screen(None)

    def get_current_screen(self):
        return self._current_screen

    def mark_dirty(self):
        """Mark entire display as needing refresh."""
        self.lcd.mark_dirty()
        self._last_activity = time.ticks_ms()

    def update(self):
        """Update display - call from main loop."""
        # Update current screen
        if self._current_screen:
            self._current_screen.update()

        # Handle backlight timeout
        self._check_backlight_timeout()

        # Flush buffer to hardware
        self.lcd.flush()

    def _check_backlight_timeout(self):
        """Turn off backlight after timeout."""
        if self._backlight_timeout <= 0:
            return  # Never timeout

        if self._backlight_on:
            elapsed = time.ticks_diff(time.ticks_ms(), self._last_activity)
            if elapsed >= self._backlight_timeout * 1000:
                self.set_backlight(False)

    def set_backlight(self, on: bool):
        """Control backlight."""
        if on != self._backlight_on:
            self._backlight_on = on
            self.lcd.set_backlight(on)
            if on:
                self._last_activity = time.ticks_ms()

    def activity(self):
        """Record user activity (resets backlight timer)."""
        self._last_activity = time.ticks_ms()
        if not self._backlight_on:
            self.set_backlight(True)

    def set_brightness(self, percent: int):
        """Set brightness 0-100%."""
        self._brightness = max(0, min(100, percent))
        self.lcd.set_brightness(self._brightness)

    def set_timeout(self, seconds: int):
        """Set backlight timeout (0 = never)."""
        self._backlight_timeout = max(0, seconds)

    def set_show_seconds(self, show: bool):
        self._show_seconds = show

    def draw_main_screen(self, clock, timer, alarms, music, volume: int,
                         quiet_mode: bool, language: str):
        """Draw the main clock screen."""
        # Line 0: Time + status icons (16 chars total)
        h, m, s = clock.get_time_tuple()
        time_str = f"{h:02d}:{m:02d}"
        if self._show_seconds:
            time_str += f":{s:02d}"

        # Build line 0: time (5 or 8 chars) + space + icons (up to 7 chars)
        icons = ""
        if quiet_mode:
            icons += chr(self.ICON_MOON)
        elif volume > 0:
            icons += chr(self.ICON_SPEAKER)
        else:
            icons += chr(self.ICON_MUTE)

        timer_state = timer.get_state()
        if timer_state == 1:  # RUNNING
            icons += chr(self.ICON_TIMER)
        elif timer_state == 2:  # PAUSED
            icons += chr(self.ICON_TIMER) + "."

        if music.is_playing():
            icons += chr(self.ICON_MUSIC)

        # Volume bar
        vol_bars = "#" * (volume * 4 // 31) + "." * (4 - volume * 4 // 31)
        icons += vol_bars

        # Pad to fit 16 chars
        line0 = (time_str + " " + icons)[:16]
        self.lcd.set_buffer_line(0, line0)

        # Line 1: Date + next alarm + timer
        date_str = clock.format_date(language, short=True)
        next_alarm = alarms.get_next_alarm()

        if timer_state == 1:  # Running
            timer_str = timer.format_remaining(self._show_seconds)
            timer_label = f">{timer_str}"
        elif timer_state == 2:  # Paused
            timer_str = timer.format_remaining(self._show_seconds)
            timer_label = f"II{timer_str}"
        else:
            timer_label = f"T{timer.get_duration()//60:02d}m"

        if next_alarm:
            alarm_str = f"A{next_alarm.time}"
        else:
            alarm_str = "A--:--"

        line1 = f"{date_str} {alarm_str} {timer_label}"
        line1 = (line1 + " " * 16)[:16]
        self.lcd.set_buffer_line(1, line1)

        self.mark_dirty()

    def draw_menu(self, title: str, items: list, selected: int, locale: str = "ru"):
        """Draw menu screen."""
        self.lcd.set_buffer_line(0, f">{title:<15}")

        # Show 1 item on line 1 (2-line display)
        if items and 0 <= selected < len(items):
            item = items[selected]
            prefix = "> " if item.get("enabled", True) else "  "
            text = f"{prefix}{item.get('label', str(item))}"
            self.lcd.set_buffer_line(1, text[:16])
        else:
            self.lcd.set_buffer_line(1, "")

        # Position indicator
        if items:
            pos = f"{selected+1}/{len(items)}"
            self.lcd.printf(14, 0, pos)

        self.mark_dirty()

    def draw_edit_screen(self, title: str, value: str, position: int,
                         locale: str = "ru", min_val: int = None, max_val: int = None):
        """Draw value editing screen."""
        self.lcd.set_buffer_line(0, f"{title:<16}")

        # Show value with cursor indicator
        val_str = str(value)
        cursor = "^" if position >= 0 else ""
        self.lcd.set_buffer_line(1, f"{val_str}{cursor}")

        # Min/max hints
        if min_val is not None and max_val is not None:
            hint = f"{min_val}-{max_val}"
            self.lcd.printf(16 - len(hint), 1, hint)

        self.mark_dirty()

    def draw_message(self, line1: str, line2: str = "", duration: int = 2000):
        """Show temporary message."""
        self.lcd.set_buffer_line(0, line1[:16])
        self.lcd.set_buffer_line(1, line2[:16])
        self.mark_dirty()
        # Could add auto-clear timer here

    def draw_wizard_step(self, step: int, total: int, title: str, value: str,
                         instruction: str = ""):
        """Draw first-boot wizard screen."""
        self.lcd.set_buffer_line(0, f"[{step}/{total}] {title[:12]}")
        self.lcd.set_buffer_line(1, f"{value:<16}")
        if instruction:
            # Could scroll instruction on line 1
            pass
        self.mark_dirty()

    def clear(self):
        self.lcd.clear()
        self.mark_dirty()