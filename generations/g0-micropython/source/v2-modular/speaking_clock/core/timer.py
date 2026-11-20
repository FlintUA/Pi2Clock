"""
Timer core: countdown timer and Pomodoro timer.
"""

import time
import asyncio
import speaking_clock.config as config


class TimerState:
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3


class TimerConfig:
    duration: int = config.TIMER_DEFAULT_SECONDS  # seconds
    sound: str = config.ALARM_DEFAULT_SOUND
    repeat: bool = False


class CountdownTimer:
    """Simple countdown timer with callbacks."""

    def __init__(self, speech_queue, dfplayer):
        self.speech = speech_queue
        self.dfplayer = dfplayer
        self.config = TimerConfig()
        self._state = TimerState.STOPPED
        self._remaining = 0
        self._total = 0
        self._start_time = 0
        self._paused_time = 0
        self._last_update = 0
        self._on_finish_callback = None
        self._on_tick_callback = None

    def set_duration(self, seconds):
        """Set timer duration in seconds."""
        self.config.duration = max(1, min(config.TIMER_MAX_SECONDS, seconds))
        if self._state == TimerState.STOPPED:
            self._remaining = self.config.duration
            self._total = self.config.duration

    def get_duration(self):
        return self.config.duration

    def get_remaining(self):
        if self._state == TimerState.RUNNING:
            elapsed = time.ticks_diff(time.ticks_ms(), self._start_time) // 1000
            return max(0, self._total - elapsed)
        elif self._state == TimerState.PAUSED:
            return self._remaining
        elif self._state == TimerState.FINISHED:
            return 0
        else:
            return self.config.duration

    def get_progress(self) -> float:
        """Return progress 0.0-1.0."""
        if self._total == 0:
            return 0.0
        return 1.0 - (self.get_remaining() / self._total)

    def get_state(self):
        return self._state

    def start(self):
        """Start or resume timer."""
        if self._state == TimerState.STOPPED:
            self._total = self.config.duration
            self._remaining = self._total
            self._start_time = time.ticks_ms()
        elif self._state == TimerState.PAUSED:
            # Resume from paused time
            self._start_time = time.ticks_add(time.ticks_ms(), -self._paused_time)
        elif self._state == TimerState.FINISHED:
            # Restart
            self._total = self.config.duration
            self._remaining = self._total
            self._start_time = time.ticks_ms()
        else:
            return  # Already running

        self._state = TimerState.RUNNING
        self._last_update = time.ticks_ms()

    def pause(self):
        """Pause timer."""
        if self._state == TimerState.RUNNING:
            self._paused_time = time.ticks_diff(time.ticks_ms(), self._start_time)
            self._remaining = self.get_remaining()
            self._state = TimerState.PAUSED

    def stop(self):
        """Stop and reset timer."""
        self._state = TimerState.STOPPED
        self._remaining = 0
        self._total = 0
        self._start_time = 0
        self._paused_time = 0

    def reset(self):
        """Reset to initial state."""
        self.stop()
        self._remaining = self.config.duration
        self._total = self.config.duration

    def add_seconds(self, seconds: int):
        """Add/subtract seconds (while running or stopped)."""
        if self._state == TimerState.RUNNING:
            self._total += seconds
            self._total = max(1, min(config.TIMER_MAX_SECONDS, self._total))
        else:
            self.config.duration = max(1, min(config.TIMER_MAX_SECONDS, self.config.duration + seconds))
            if self._state == TimerState.STOPPED:
                self._remaining = self.config.duration
                self._total = self.config.duration

    def set_on_finish(self, callback):
        """Set callback when timer finishes."""
        self._on_finish_callback = callback

    def set_on_tick(self, callback):
        """Set callback on each second tick (receives remaining seconds)."""
        self._on_tick_callback = callback

    def update(self):
        """Call from main loop to check for completion."""
        if self._state != TimerState.RUNNING:
            return

        remaining = self.get_remaining()

        # Tick callback (once per second)
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_update) >= 1000:
            self._last_update = now
            if self._on_tick_callback:
                self._on_tick_callback(remaining)

        # Check finish
        if remaining <= 0:
            self._finish()

    def _finish(self):
        """Timer finished."""
        self._state = TimerState.FINISHED
        self._remaining = 0

        # Queue critical speech
        async def finish_sequence():
            await self.speech.speak_phrase("timer_done")
            await self.dfplayer.play_folder_track(7, 13)  # timer done sound
            return True

        self.speech.enqueue_critical(finish_sequence, "timer_finished")

        # Call finish callback
        if self._on_finish_callback:
            asyncio.create_task(self._on_finish_callback())

        # Auto-repeat
        if self.config.repeat:
            self.start()

    def format_remaining(self, show_seconds: bool = True) :
        """Format remaining time as MM:SS or HH:MM:SS."""
        rem = self.get_remaining()
        h = rem // 3600
        m = (rem % 3600) // 60
        s = rem % 60

        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}" if show_seconds else f"{h:02d}:{m:02d}"
        return f"{m:02d}:{s:02d}"


class PomodoroState:
    IDLE = 0
    WORK = 1
    SHORT_BREAK = 2
    LONG_BREAK = 3


class PomodoroConfig:
    work: int = config.POMODORO_WORK_DEFAULT
    short_break: int = config.POMODORO_SHORT_BREAK_DEFAULT
    long_break: int = config.POMODORO_LONG_BREAK_DEFAULT
    cycles: int = config.POMODORO_CYCLES_DEFAULT
    auto_start_break: bool = True
    auto_start_work: bool = False
    work_sound: str = "chime_work"
    break_sound: str = "chime_break"


class PomodoroTimer:
    """Pomodoro / interval timer."""

    def __init__(self, speech_queue, dfplayer):
        self.speech = speech_queue
        self.dfplayer = dfplayer
        self.config = PomodoroConfig()
        self._state = PomodoroState.IDLE
        self._cycle = 0
        self._timer = CountdownTimer(speech_queue, dfplayer)
        self._timer.set_on_finish(self._on_phase_finish)

    def get_state(self) -> PomodoroState:
        return self._state

    def get_cycle(self) :
        return self._cycle

    def get_remaining(self):
        return self._timer.get_remaining()

    def get_phase_name(self, locale: str = "ru") :
        names = {
            "ru": {PomodoroState.WORK: "Работа", PomodoroState.SHORT_BREAK: "Отдых", PomodoroState.LONG_BREAK: "Длинный отдых"},
            "de": {PomodoroState.WORK: "Arbeit", PomodoroState.SHORT_BREAK: "Pause", PomodoroState.LONG_BREAK: "Lange Pause"},
            "ua": {PomodoroState.WORK: "Робота", PomodoroState.SHORT_BREAK: "Відпочинок", PomodoroState.LONG_BREAK: "Довгий відпочинок"},
        }
        return names.get(locale, names["ru"]).get(self._state, "")

    def start(self):
        """Start Pomodoro (work phase)."""
        if self._state == PomodoroState.IDLE:
            self._cycle = 0
        self._state = PomodoroState.WORK
        self._timer.set_duration(self.config.work)
        self._timer.start()

    def pause(self):
        self._timer.pause()

    def resume(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self._state = PomodoroState.IDLE
        self._cycle = 0

    def skip_phase(self):
        """Skip to next phase."""
        self._on_phase_finish()

    async def _on_phase_finish(self):
        """Handle phase transition."""
        if self._state == PomodoroState.WORK:
            self._cycle += 1
            if self._cycle % self.config.cycles == 0:
                self._state = PomodoroState.LONG_BREAK
                self._timer.set_duration(self.config.long_break)
                await self.speech.speak_phrase("long_break")
            else:
                self._state = PomodoroState.SHORT_BREAK
                self._timer.set_duration(self.config.short_break)
                await self.speech.speak_phrase("short_break")

            if self.config.auto_start_break:
                self._timer.start()
            else:
                self._timer.stop()

        elif self._state in (PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
            self._state = PomodoroState.WORK
            self._timer.set_duration(self.config.work)
            await self.speech.speak_phrase("work_start")

            if self.config.auto_start_work:
                self._timer.start()
            else:
                self._timer.stop()

    def update(self):
        """Call from main loop."""
        self._timer.update()

    def format_remaining(self, show_seconds: bool = True) :
        return self._timer.format_remaining(show_seconds)