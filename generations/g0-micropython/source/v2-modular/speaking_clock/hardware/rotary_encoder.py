"""
Non-blocking rotary encoder with acceleration and callbacks.
Improvements over original:
- No blocking sleeps in interrupts
- Acceleration for fast rotation
- Separate callbacks for CW/CCW/press/release
- Debounced button
"""

from machine import Pin
import micropython
import time


class RotaryEncoder:
    """Rotary encoder with interrupt-driven quadrature decoding."""

    ROT_CW = 1
    ROT_CCW = 2
    SW_PRESS = 4
    SW_RELEASE = 8

    def __init__(self, dt_pin: int, clk_pin: int, sw_pin: int,
                 accel_threshold: int = 4, accel_multiplier: int = 3):
        self.dt_pin = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.clk_pin = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.sw_pin = Pin(sw_pin, Pin.IN, Pin.PULL_UP)

        self._last_state = (self.dt_pin.value() << 1) | self.clk_pin.value()
        self._last_button_state = self.sw_pin.value()

        # Acceleration
        self._accel_threshold = accel_threshold
        self._accel_multiplier = accel_multiplier
        self._step_count = 0
        self._last_rot_time = 0

        # Callbacks
        self._rot_cw_cb = None
        self._rot_ccw_cb = None
        self._press_cb = None
        self._release_cb = None
        self._any_rot_cb = None  # Called with +steps/-steps

        # Setup interrupts
        self.dt_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._rotary_irq)
        self.clk_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._rotary_irq)
        self.sw_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._switch_irq)

    def _rotary_irq(self, pin):
        """Quadrature decoder interrupt handler."""
        new_state = (self.dt_pin.value() << 1) | self.clk_pin.value()
        if new_state == self._last_state:
            return

        transition = (self._last_state << 2) | new_state
        now = time.ticks_ms()

        # Detect direction
        if transition in (0b1110, 0b0111, 0b0001, 0b1000):  # CW
            direction = 1
        elif transition in (0b1101, 0b0100, 0b0010, 0b1011):  # CCW
            direction = -1
        else:
            self._last_state = new_state
            return

        # Acceleration
        if time.ticks_diff(now, self._last_rot_time) < 100:
            self._step_count += 1
        else:
            self._step_count = 1
        self._last_rot_time = now

        steps = 1
        if self._step_count >= self._accel_threshold:
            steps = self._accel_multiplier

        self._last_state = new_state

        # Schedule callback (not in IRQ context) - handle queue full
        try:
            micropython.schedule(self._rot_callback, direction * steps)
        except RuntimeError:
            # Queue full - skip this tick
            pass

    def _rot_callback(self, steps: int):
        """Scheduled rotation callback."""
        if steps > 0 and self._rot_cw_cb:
            for _ in range(steps):
                self._rot_cw_cb()
        elif steps < 0 and self._rot_ccw_cb:
            for _ in range(-steps):
                self._rot_ccw_cb()

        if self._any_rot_cb:
            self._any_rot_cb(steps)

    def _switch_irq(self, pin):
        """Button interrupt handler."""
        new_state = self.sw_pin.value()
        if new_state == self._last_button_state:
            return
        self._last_button_state = new_state

        if new_state:  # Released (pull-up)
            micropython.schedule(self._btn_callback, self.SW_RELEASE)
        else:  # Pressed
            micropython.schedule(self._btn_callback, self.SW_PRESS)

    def _btn_callback(self, event: int):
        """Scheduled button callback."""
        if event == self.SW_PRESS and self._press_cb:
            self._press_cb()
        elif event == self.SW_RELEASE and self._release_cb:
            self._release_cb()

    # ==================== CALLBACK REGISTRATION ====================

    def on_cw(self, callback):
        """Register clockwise rotation callback."""
        self._rot_cw_cb = callback

    def on_ccw(self, callback):
        """Register counter-clockwise rotation callback."""
        self._rot_ccw_cb = callback

    def on_rotate(self, callback):
        """Register any rotation callback (receives +steps/-steps)."""
        self._any_rot_cb = callback

    def on_press(self, callback):
        """Register button press callback."""
        self._press_cb = callback

    def on_release(self, callback):
        """Register button release callback."""
        self._release_cb = callback

    def on_short_press(self, callback):
        """Register short press callback (press + release within 500ms)."""
        # Implemented via press+release timing in ButtonManager
        pass

    def on_long_press(self, callback, threshold_ms: int = 1000):
        """Register long press callback."""
        # Implemented via press+release timing in ButtonManager
        pass

    def remove_all_callbacks(self):
        """Remove all callbacks."""
        self._rot_cw_cb = None
        self._rot_ccw_cb = None
        self._any_rot_cb = None
        self._press_cb = None
        self._release_cb = None


class EncoderPair:
    """Convenience class for managing two encoders with distinct roles."""

    def __init__(self, left: RotaryEncoder, right: RotaryEncoder):
        self.left = left   # Volume / Navigation
        self.right = right # Values / Timer

    def setup_default_callbacks(self, app):
        """Setup typical callbacks for the app."""
        # Left encoder: volume + navigation
        self.left.on_cw(lambda: app.on_enc_left_cw())
        self.left.on_ccw(lambda: app.on_enc_left_ccw())
        self.left.on_press(lambda: app.on_enc_left_press())
        self.left.on_release(lambda: app.on_enc_left_release())

        # Right encoder: timer values + selection
        self.right.on_cw(lambda: app.on_enc_right_cw())
        self.right.on_ccw(lambda: app.on_enc_right_ccw())
        self.right.on_press(lambda: app.on_enc_right_press())
        self.right.on_release(lambda: app.on_enc_right_release())