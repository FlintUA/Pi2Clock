"""
Speaking Timer-Clock - Main Entry Point
Modular architecture for Raspberry Pi Pico (RP2040)
"""

import asyncio
import time
import gc
from machine import Pin, I2C, UART

# Hardware drivers
from speaking_clock.hardware.rtc_ds1302 import RTC_DS1302
from speaking_clock.hardware.lcd_i2c import LCD_I2C
from speaking_clock.hardware.dfplayer import DFPlayerAsync
from speaking_clock.hardware.rotary_encoder import RotaryEncoder
from speaking_clock.hardware.buttons import ButtonManager

# Core logic
from speaking_clock.core.clock import Clock
from speaking_clock.core.speech import SpeechQueue, SpeechPriority
from speaking_clock.core.alarms import AlarmManager
from speaking_clock.core.timer import CountdownTimer, PomodoroTimer, TimerState
from speaking_clock.core.music import MusicPlayer

# Locale & UI
from speaking_clock.locale.manager import LocaleManager
from speaking_clock.ui.display import DisplayManager

# Configuration & Storage
import speaking_clock.config as config
from speaking_clock.storage import storage


class SpeakingClockApp:
    """Main application class tying all components together."""

    def __init__(self):
        # Hardware
        self.rtc = None
        self.lcd = None
        self.dfplayer = None
        self.enc_left = None
        self.enc_right = None
        self.buttons = None

        # Core
        self.clock = None
        self.speech = None
        self.alarms = None
        self.timer = None
        self.pomodoro = None
        self.music = None

        # Locale & UI
        self.locale = None
        self.display = None

        # State
        self.volume = config.VOLUME_DEFAULT
        self.quiet_mode = config.QUIET_MODE_ENABLED_DEFAULT
        self.running = True
        self._last_gc = 0
        self._prev_volume = config.VOLUME_DEFAULT
        self._last_hour_chime = False
        self._last_half_chime = False

    async def initialize_hardware(self):
        """Initialize all hardware components."""
        print("[App] Initializing hardware...")

        # I2C for LCD
        i2c = I2C(0, sda=Pin(config.I2C_SDA_PIN), scl=Pin(config.I2C_SCL_PIN), freq=config.I2C_FREQ)
        self.lcd = LCD_I2C(i2c, config.LCD_I2C_ADDR, config.LCD_ROWS, config.LCD_COLS)
        print("[App] LCD initialized")

        # DFPlayer
        self.dfplayer = DFPlayerAsync(
            config.UART_ID,
            config.UART_TX_PIN,
            config.UART_RX_PIN,
            config.DFPLAYER_BUSY_PIN
        )
        await self.dfplayer.initialize()
        await self.dfplayer.set_volume(self.volume)
        print("[App] DFPlayer initialized")

        # RTC
        self.rtc = RTC_DS1302(config.RTC_CLK_PIN, config.RTC_DAT_PIN, config.RTC_RST_PIN)
        self.rtc.start()
        if not self.rtc.test_connection():
            print("[App] WARNING: RTC not responding!")
        print("[App] RTC initialized")

        # Encoders
        self.enc_left = RotaryEncoder(
            config.ENC1_DT_PIN, config.ENC1_CLK_PIN, config.ENC1_SW_PIN,
            config.ENCODER_ACCEL_THRESHOLD, config.ENCODER_ACCEL_MULTIPLIER
        )
        self.enc_right = RotaryEncoder(
            config.ENC2_DT_PIN, config.ENC2_CLK_PIN, config.ENC2_SW_PIN,
            config.ENCODER_ACCEL_THRESHOLD, config.ENCODER_ACCEL_MULTIPLIER
        )
        print("[App] Encoders initialized")

        # Buttons
        self.buttons = ButtonManager(config)
        self.buttons.set_app(self)
        print("[App] Buttons initialized")

    def initialize_core(self):
        """Initialize core logic components."""
        print("[App] Initializing core components...")

        # Clock
        self.clock = Clock(self.rtc)
        # Load RTC correction from storage
        correction = storage.get("rtc_correction_ppm", config.RTC_CORRECTION_PPM_DEFAULT)
        self.clock.set_correction_ppm(correction)

        # Locale
        self.locale = LocaleManager()
        saved_lang = storage.get("language", config.DEFAULT_LOCALE)
        self.locale.set_language(saved_lang)

        # Speech queue
        self.speech = SpeechQueue(self.dfplayer, self.locale)

        # Alarms
        self.alarms = AlarmManager(storage, self.speech, self.clock)
        self.alarms.load()
        self.alarms.set_dfplayer(self.dfplayer)

        # Timers
        self.timer = CountdownTimer(self.speech, self.dfplayer)
        saved_timer = storage.get("timer.last_value", config.TIMER_DEFAULT_SECONDS)
        self.timer.set_duration(saved_timer)

        self.pomodoro = PomodoroTimer(self.speech, self.dfplayer)
        # Load pomodoro settings
        self.pomodoro.config.work = storage.get("pomodoro.work", config.POMODORO_WORK_DEFAULT)
        self.pomodoro.config.short_break = storage.get("pomodoro.short_break", config.POMODORO_SHORT_BREAK_DEFAULT)
        self.pomodoro.config.long_break = storage.get("pomodoro.long_break", config.POMODORO_LONG_BREAK_DEFAULT)
        self.pomodoro.config.cycles = storage.get("pomodoro.cycles", config.POMODORO_CYCLES_DEFAULT)

        # Music
        self.music = MusicPlayer(self.dfplayer, self.speech)

        # Quiet mode
        self.quiet_mode = storage.get("quiet_mode.enabled", config.QUIET_MODE_ENABLED_DEFAULT)
        quiet_start = storage.get("quiet_mode.start", config.QUIET_START_DEFAULT)
        quiet_end = storage.get("quiet_mode.end", config.QUIET_END_DEFAULT)
        self.speech.set_quiet_mode(self.quiet_mode)

        print("[App] Core components initialized")

    def initialize_ui(self):
        """Initialize UI components."""
        print("[App] Initializing UI...")

        self.display = DisplayManager(self.lcd, self.locale)
        self.display.set_backlight(True)
        self.display.set_brightness(storage.get("display.brightness", config.DISPLAY_BRIGHTNESS_DEFAULT))
        self.display.set_timeout(storage.get("display.timeout", config.DISPLAY_TIMEOUT_DEFAULT))
        self.display.set_show_seconds(storage.get("display.show_seconds", config.DISPLAY_SHOW_SECONDS_DEFAULT))

        # Load custom characters
        # (done in DisplayManager.__init__)

        print("[App] UI initialized")

    def setup_encoder_callbacks(self):
        """Setup encoder rotation and button callbacks."""
        # Left encoder: Volume
        self.enc_left.on_cw(lambda: self.on_enc_left_cw())
        self.enc_left.on_ccw(lambda: self.on_enc_left_ccw())
        self.enc_left.on_press(lambda: self.on_enc_left_press())
        self.enc_left.on_release(lambda: self.on_enc_left_release())

        # Right encoder: Timer/Navigation
        self.enc_right.on_cw(lambda: self.on_enc_right_cw())
        self.enc_right.on_ccw(lambda: self.on_enc_right_ccw())
        self.enc_right.on_press(lambda: self.on_enc_right_press())
        self.enc_right.on_release(lambda: self.on_enc_right_release())

        # Register encoder buttons with ButtonManager for long-press detection
        self.buttons.register_encoder_left(
            short_cb=self.on_enc_left_short,
            long_cb=self.on_enc_left_long,
            long_ms=1000
        )
        self.buttons.register_encoder_right(
            short_cb=self.on_enc_right_short,
            long_cb=self.on_enc_right_long,
            long_ms=1000
        )

    # ==================== ENCODER CALLBACKS ====================

    def on_enc_left_cw(self):
        """Left encoder clockwise - volume up."""
        if self.volume < config.VOLUME_MAX:
            self.volume += config.VOLUME_STEP
            asyncio.create_task(self.dfplayer.set_volume(self.volume))
            storage.set("volume", self.volume)
            self.display.activity()
            self._update_main_screen()

    def on_enc_left_ccw(self):
        """Left encoder counter-clockwise - volume down."""
        if self.volume > config.VOLUME_MIN:
            self.volume -= config.VOLUME_STEP
            asyncio.create_task(self.dfplayer.set_volume(self.volume))
            storage.set("volume", self.volume)
            self.display.activity()
            self._update_main_screen()

    def on_enc_left_press(self):
        """Left encoder press - forward to ButtonManager for short/long detection."""
        self.buttons.on_enc_left_press()

    def on_enc_left_release(self):
        """Left encoder release - forward to ButtonManager."""
        self.buttons.on_enc_left_release()

    def on_enc_left_short(self):
        """Left encoder short press - toggle mute."""
        if self.volume > 0:
            self._prev_volume = self.volume
            self.volume = 0
        else:
            self.volume = self._prev_volume
        asyncio.create_task(self.dfplayer.set_volume(self.volume))
        storage.set("volume", self.volume)
        # Use new locale API for phrase sequence
        phrase_key = "volume_on" if self.volume > 0 else "volume_off"
        self.speech.enqueue_low(
            lambda: self.speech.speak_phrase(phrase_key),
            "volume_toggle"
        )
        self._update_main_screen()

    def on_enc_left_long(self):
        """Left encoder long press - enter settings menu."""
        print("[App] Long press left encoder - Settings menu")
        # TODO: Push settings screen
        self.display.activity()

    def on_enc_right_cw(self):
        """Right encoder clockwise - increase timer/navigate."""
        if self.timer.get_state() == TimerState.STOPPED:
            self.timer.add_seconds(60)  # Add 1 minute
            storage.set("timer.last_value", self.timer.get_duration())
        self.display.activity()
        self._update_main_screen()

    def on_enc_right_ccw(self):
        """Right encoder counter-clockwise - decrease timer/navigate."""
        if self.timer.get_state() == TimerState.STOPPED:
            self.timer.add_seconds(-60)  # Subtract 1 minute
            storage.set("timer.last_value", self.timer.get_duration())
        self.display.activity()
        self._update_main_screen()

    def on_enc_right_press(self):
        """Right encoder press - forward to ButtonManager."""
        self.buttons.on_enc_right_press()

    def on_enc_right_release(self):
        """Right encoder release - forward to ButtonManager."""
        self.buttons.on_enc_right_release()

    def on_enc_right_short(self):
        """Right encoder short press - start/stop timer."""
        state = self.timer.get_state()
        if state == TimerState.STOPPED:
            self.timer.start()
            self.speech.enqueue_normal(
                lambda: self.speech.speak_phrase("timer_set"),
                "timer_started"
            )
        elif state == TimerState.RUNNING:
            self.timer.pause()
            self.speech.enqueue_normal(
                lambda: self.speech.speak_phrase("timer_cancelled"),
                "timer_paused"
            )
        elif state == TimerState.PAUSED:
            self.timer.start()
        elif state == TimerState.FINISHED:
            self.timer.reset()
        self._update_main_screen()

    def on_enc_right_long(self):
        """Right encoder long press - reset timer."""
        self.timer.reset()
        storage.set("timer.last_value", self.timer.get_duration())
        self._update_main_screen()

    # ==================== BUTTON CALLBACKS ====================

    def on_btn1_short(self):
        """Btn1 short: Play/pause music."""
        if self.music.is_playing():
            self.music.pause()
        else:
            if not self.music.is_scanned():
                asyncio.create_task(self.music.initialize(config.MUSIC_ROOT))
            self.music.play()
        self.display.activity()

    def on_btn1_long(self):
        """Btn1 long: Shuffle playlist."""
        self.music.shuffle()
        self.speech.enqueue_low(
            lambda: self.speech.speak_phrase("menu_enter"),
            "shuffle"
        )
        self.display.activity()

    def on_btn2_short(self):
        """Btn2 short: Speak current time."""
        h, m, _ = self.clock.get_time_tuple()
        self.speech.enqueue_normal(
            lambda: self.speech.speak_time(h, m),
            "speak_time"
        )
        self.display.activity()

    def on_btn2_long(self):
        """Btn2 long: Cycle language."""
        new_lang = self.locale.cycle_language()
        storage.set("language", new_lang)
        self.speech.enqueue_normal(
            lambda: self.speech.speak_phrase("menu_enter"),
            f"language_{new_lang}"
        )
        self._update_main_screen()

    def on_btn3_short(self):
        """Btn3 short: Chime demo (plays hourly chime for current hour)."""
        h, _, _ = self.clock.get_time_tuple()
        # Use new locale API for chime sequence
        self.speech.enqueue_high(
            lambda: self.speech.play_chime(h),
            "chime_demo"
        )
        self.display.activity()

    def on_btn3_long(self):
        """Btn3 long: Enter main menu."""
        print("[App] Main menu - TODO")
        self.display.activity()

    def on_btn4_short(self):
        """Btn4 short: Cycle timer preset 1 (5/10/15 min)."""
        presets = config.TIMER_PRESETS_1
        current = self.timer.get_duration()
        try:
            idx = presets.index(current)
            next_idx = (idx + 1) % len(presets)
        except ValueError:
            next_idx = 0
        self.timer.set_duration(presets[next_idx])
        storage.set("timer.last_value", self.timer.get_duration())
        self.speech.enqueue_normal(
            lambda: self.speech.speak_phrase("timer_set"),
            f"preset_{presets[next_idx]//60}min"
        )
        self._update_main_screen()
        self.display.activity()

    def on_btn4_long(self):
        """Btn4 long: Reset timer."""
        self.timer.reset()
        storage.set("timer.last_value", self.timer.get_duration())
        self._update_main_screen()
        self.display.activity()

    def on_btn5_short(self):
        """Btn5 short: Cycle timer preset 2 (30/45/60 min)."""
        presets = config.TIMER_PRESETS_2
        current = self.timer.get_duration()
        try:
            idx = presets.index(current)
            next_idx = (idx + 1) % len(presets)
        except ValueError:
            next_idx = 0
        self.timer.set_duration(presets[next_idx])
        storage.set("timer.last_value", self.timer.get_duration())
        self.speech.enqueue_normal(
            lambda: self.speech.speak_phrase("timer_set"),
            f"preset_{presets[next_idx]//60}min"
        )
        self._update_main_screen()
        self.display.activity()

    def on_btn5_long(self):
        """Btn5 long: Start Pomodoro."""
        self.pomodoro.start()
        self._update_main_screen()
        self.display.activity()

    # ==================== MAIN LOOP ====================

    def _update_main_screen(self):
        """Update main screen display."""
        self.display.draw_main_screen(
            clock=self.clock,
            timer=self.timer,
            alarms=self.alarms,
            music=self.music,
            volume=self.volume,
            quiet_mode=self.quiet_mode,
            language=self.locale.get_current_language()
        )

    def _check_quiet_mode(self):
        """Check and update quiet mode based on time."""
        if self.quiet_mode:
            quiet_start = storage.get("quiet_mode.start", config.QUIET_START_DEFAULT)
            quiet_end = storage.get("quiet_mode.end", config.QUIET_END_DEFAULT)
            is_quiet = self.clock.is_quiet_time(quiet_start, quiet_end)
            if is_quiet != self.speech.is_quiet_mode():
                self.speech.set_quiet_mode(is_quiet)
                if is_quiet:
                    self.volume = 0
                    asyncio.create_task(self.dfplayer.set_volume(0))
        else:
            if self.speech.is_quiet_mode():
                self.speech.set_quiet_mode(False)

    async def _process_speech(self):
        """Process speech queue."""
        await self.speech.process()

    def _periodic_tasks(self):
        """Run periodic tasks (every loop iteration)."""
        now = time.ticks_ms()

        # Update clock (handles RTC sync)
        self.clock.tick()

        # Check if we have valid time (not default/fallback)
        h, m, s = self.clock.get_time_tuple()
        time_valid = not (h == 0 and m == 0 and s == 0)  # Reject 0:0:0

        # Hourly/half-hourly chimes (only if time is valid)
        if time_valid:
            if self.clock.is_hour_boundary() and not self._last_hour_chime:
                self.speech.enqueue_high(
                    lambda: self.speech.play_chime(h),
                    f"chime_hour_{h}"
                )
                self._last_hour_chime = True
            elif m != 0:
                self._last_hour_chime = False

            if self.clock.is_half_hour_boundary() and not self._last_half_chime:
                self.speech.enqueue_high(
                    lambda: self.speech.play_chime(30),
                    "chime_half"
                )
                self._last_half_chime = True
            elif m != 30:
                self._last_half_chime = False

        # Check alarms (only if time is valid)
        if time_valid:
            self.alarms.check_alarms()

        # Update timers
        self.timer.update()
        self.pomodoro.update()

        # Check quiet mode
        self._check_quiet_mode()

        # Garbage collection every 30 seconds
        if time.ticks_diff(now, self._last_gc) >= 30_000:
            gc.collect()
            self._last_gc = now

    async def run(self):
        """Main event loop."""
        print("[App] Starting main loop...")

        # Initial screen draw
        self._update_main_screen()

        # Initialize music in background
        asyncio.create_task(self.music.initialize(config.MUSIC_ROOT))

        # Main loop
        while self.running:
            loop_start = time.ticks_ms()

            # Update buttons
            self.buttons.update()

            # Run periodic tasks
            self._periodic_tasks()

            # Process speech queue
            await self._process_speech()

            # Update display
            self.display.update()

            # Maintain loop timing
            elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
            target_interval = config.MAIN_LOOP_INTERVAL_MS
            if elapsed < target_interval:
                await asyncio.sleep_ms(target_interval - elapsed)
            else:
                # Loop overrun - yield anyway
                await asyncio.sleep_ms(1)

        print("[App] Main loop ended")

    async def shutdown(self):
        """Graceful shutdown."""
        print("[App] Shutting down...")
        self.running = False
        await self.dfplayer.stop()
        storage.save_now()
        self.display.set_backlight(False)
        print("[App] Shutdown complete")


async def main():
    """Async main entry point."""
    app = SpeakingClockApp()

    try:
        await app.initialize_hardware()
        app.initialize_core()
        app.initialize_ui()
        app.setup_encoder_callbacks()

        # Check first boot
        if storage.is_first_boot():
            print("[App] First boot detected - running wizard")
            # TODO: First boot wizard
            storage.mark_first_boot_done()

        await app.run()

    except KeyboardInterrupt:
        print("[App] Interrupted")
    except Exception as e:
        print(f"[App] Fatal error: {e}")
        import sys
        sys.print_exception(e)
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())