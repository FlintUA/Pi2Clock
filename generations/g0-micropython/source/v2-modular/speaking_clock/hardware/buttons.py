"""
Button manager with debouncing, short/long press detection.
Handles 5 buttons + 2 encoder switches.
"""

from machine import Pin
import time
import asyncio


class Button:
    """Single button with debouncing and press detection."""

    def __init__(self, pin: int, pull_up: bool = True, active_low: bool = True,
                 debounce_ms: int = 50, long_press_ms: int = 1000):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self.active_low = active_low
        self.debounce_ms = debounce_ms
        self.long_press_ms = long_press_ms

        self._last_state = self._read_raw()
        self._stable_state = self._last_state
        self._last_change = time.ticks_ms()
        self._press_time = 0
        self._pressed = False

        # Callbacks
        self.on_press = None      # Called on press (after debounce)
        self.on_release = None    # Called on release
        self.on_short = None      # Called on short press (release < long_press_ms)
        self.on_long = None       # Called on long press (hold > long_press_ms)
        self.on_click = None      # Alias for on_short

    def _read_raw(self) -> bool:
        """Read raw pin state (True = active/pressed)."""
        val = self.pin.value()
        return not val if self.active_low else val

    def update(self):
        """Call periodically to process button state."""
        now = time.ticks_ms()
        raw = self._read_raw()

        # Debounce
        if raw != self._last_state:
            self._last_state = raw
            self._last_change = now
            return

        if raw != self._stable_state:
            if time.ticks_diff(now, self._last_change) >= self.debounce_ms:
                self._stable_state = raw
                if raw:  # Pressed
                    self._pressed = True
                    self._press_time = now
                    if self.on_press:
                        self.on_press()
                else:  # Released
                    if self._pressed:
                        duration = time.ticks_diff(now, self._press_time)
                        self._pressed = False
                        if self.on_release:
                            self.on_release()
                        if duration >= self.long_press_ms:
                            if self.on_long:
                                self.on_long()
                        else:
                            if self.on_short:
                                self.on_short()
                            if self.on_click:
                                self.on_click()

    def is_pressed(self) -> bool:
        """Return current stable pressed state."""
        return self._stable_state

    def was_pressed(self) -> bool:
        """Return True if button was pressed since last check (consumes event)."""
        # Not implemented - use callbacks instead
        return False


class ButtonManager:
    """Manages all buttons (5 main + 2 encoder switches)."""

    def __init__(self, config):
        self.config = config
        self.buttons = {}

        # Main buttons (Btn1-5)
        self.buttons["btn1"] = Button(config.BTN1_PIN, long_press_ms=1500)  # Music
        self.buttons["btn2"] = Button(config.BTN2_PIN, long_press_ms=1000)  # Speak time / Language
        self.buttons["btn3"] = Button(config.BTN3_PIN, long_press_ms=1000)  # Menu / Chime
        self.buttons["btn4"] = Button(config.BTN4_PIN, long_press_ms=1000)  # Timer preset 1
        self.buttons["btn5"] = Button(config.BTN5_PIN, long_press_ms=1000)  # Timer preset 2

        # Encoder buttons (handled by RotaryEncoder, but we track long press here)
        self._enc_left_press_time = 0
        self._enc_right_press_time = 0
        self._enc_left_pressed = False
        self._enc_right_pressed = False

        # App reference for callbacks
        self._app = None

    def set_app(self, app):
        """Set app reference for callbacks."""
        self._app = app
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Setup button callbacks to app methods."""
        if not self._app:
            return

        # Btn1: Music play/pause (short), Shuffle (long)
        self.buttons["btn1"].on_short = self._app.on_btn1_short
        self.buttons["btn1"].on_long = self._app.on_btn1_long

        # Btn2: Speak time (short), Cycle language (long)
        self.buttons["btn2"].on_short = self._app.on_btn2_short
        self.buttons["btn2"].on_long = self._app.on_btn2_long

        # Btn3: Menu enter (long), Chime demo (short)
        self.buttons["btn3"].on_short = self._app.on_btn3_short
        self.buttons["btn3"].on_long = self._app.on_btn3_long

        # Btn4: Timer preset 1 cycle (short), Reset timer (long)
        self.buttons["btn4"].on_short = self._app.on_btn4_short
        self.buttons["btn4"].on_long = self._app.on_btn4_long

        # Btn5: Timer preset 2 cycle (short), Start Pomodoro (long)
        self.buttons["btn5"].on_short = self._app.on_btn5_short
        self.buttons["btn5"].on_long = self._app.on_btn5_long

    def register_encoder_left(self, press_cb=None, release_cb=None,
                              short_cb=None, long_cb=None, long_ms=1000):
        """Register encoder left button callbacks."""
        self._enc_left_short_cb = short_cb
        self._enc_left_long_cb = long_cb
        self._enc_left_long_ms = long_ms

    def register_encoder_right(self, press_cb=None, release_cb=None,
                               short_cb=None, long_cb=None, long_ms=1000):
        """Register encoder right button callbacks."""
        self._enc_right_short_cb = short_cb
        self._enc_right_long_cb = long_cb
        self._enc_right_long_ms = long_ms

    def on_enc_left_press(self):
        """Called from RotaryEncoder on press."""
        self._enc_left_pressed = True
        self._enc_left_press_time = time.ticks_ms()

    def on_enc_left_release(self):
        """Called from RotaryEncoder on release."""
        if self._enc_left_pressed:
            self._enc_left_pressed = False
            duration = time.ticks_diff(time.ticks_ms(), self._enc_left_press_time)
            if duration >= getattr(self, '_enc_left_long_ms', 1000):
                if self._enc_left_long_cb:
                    self._enc_left_long_cb()
            else:
                if self._enc_left_short_cb:
                    self._enc_left_short_cb()

    def on_enc_right_press(self):
        """Called from RotaryEncoder on press."""
        self._enc_right_pressed = True
        self._enc_right_press_time = time.ticks_ms()

    def on_enc_right_release(self):
        """Called from RotaryEncoder on release."""
        if self._enc_right_pressed:
            self._enc_right_pressed = False
            duration = time.ticks_diff(time.ticks_ms(), self._enc_right_press_time)
            if duration >= getattr(self, '_enc_right_long_ms', 1000):
                if self._enc_right_long_cb:
                    self._enc_right_long_cb()
            else:
                if self._enc_right_short_cb:
                    self._enc_right_short_cb()

    def update(self):
        """Update all buttons. Call from main loop."""
        for btn in self.buttons.values():
            btn.update()

    async def update_async(self, interval_ms: int = 20):
        """Async version for use with asyncio."""
        while True:
            self.update()
            await asyncio.sleep_ms(interval_ms)

    def get_button(self, name: str) -> Button:
        """Get button by name."""
        return self.buttons.get(name)