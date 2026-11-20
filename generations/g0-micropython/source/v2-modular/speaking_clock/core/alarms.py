"""
Alarm manager: multiple alarms with days, sounds, labels.
"""

import time
import asyncio
import speaking_clock.config as config


class Alarm:
    def __init__(self, id, enabled, time, days, sound, label, snoozed_until=0):
        self.id = id
        self.enabled = enabled
        self.time = time
        self.days = days
        self.sound = sound
        self.label = label
        self.snoozed_until = snoozed_until

    def to_dict(self):
        return {"id": self.id, "enabled": self.enabled, "time": self.time,
                "days": self.days, "sound": self.sound, "label": self.label,
                "snoozed_until": self.snoozed_until}


class AlarmManager:
    """Manages multiple alarms with day masks and sounds."""

    def __init__(self, storage, speech_queue, clock):
        self.storage = storage
        self.speech = speech_queue
        self.clock = clock
        self.alarms: Dict[int, Alarm] = {}
        self._next_id = 1
        self._last_triggered = {}  # alarm_id -> last trigger timestamp
        self._snooze_minutes = config.ALARM_SNOOZE_MINUTES
        self._auto_dismiss_sec = config.ALARM_AUTO_DISMISS_SECONDS

    def load(self):
        """Load alarms from storage."""
        alarm_data = self.storage.get("alarms", config.DEFAULT_ALARMS)
        self.alarms = {}
        max_id = 0
        for a in alarm_data:
            alarm = Alarm(**a)
            self.alarms[alarm.id] = alarm
            max_id = max(max_id, alarm.id)
        self._next_id = max_id + 1
        print(f"[Alarms] Loaded {len(self.alarms)} alarms")

    def save(self):
        """Save alarms to storage."""
        data = [a.to_dict() for a in self.alarms.values()]
        self.storage.set("alarms", data)
        self.storage.save_now()

    def get_all(self):
        """Get all alarms sorted by ID."""
        return sorted(self.alarms.values(), key=lambda a: a.id)

    def get_enabled(self) -> List[Alarm]:
        """Get enabled alarms."""
        return [a for a in self.get_all() if a.enabled]

    def get_next_alarm(self) :
        """Get the next alarm that will trigger."""
        now = self.clock.now()
        current_minutes = now[4] * 60 + now[5]
        current_weekday = now[3]  # 1=Mon

        next_alarm = None
        next_diff = 24 * 60  # max diff

        for alarm in self.get_enabled():
            if not self._is_alarm_today(alarm, current_weekday):
                continue

            alarm_minutes = self._time_to_minutes(alarm.time)
            diff = alarm_minutes - current_minutes

            if diff < 0:
                diff += 24 * 60  # next day

            if diff < next_diff:
                next_diff = diff
                next_alarm = alarm

        return next_alarm

    def _is_alarm_today(self, alarm: Alarm, weekday: int) :
        """Check if alarm is active on given weekday (1=Mon)."""
        bit = weekday - 1
        return (alarm.days & (1 << bit)) != 0

    def _time_to_minutes(self, time_str: str) :
        """Convert 'HH:MM' to minutes since midnight."""
        try:
            h, m = map(int, time_str.split(":"))
            return h * 60 + m
        except Exception:
            return 0

    def check_alarms(self):
        """Check and trigger alarms. Call from main loop."""
        now = self.clock.now()
        hour, minute, second = now[4], now[5], now[6]
        weekday = now[3]

        # Only check on minute boundaries (second == 0)
        if second != 0:
            return

        current_minutes = hour * 60 + minute

        for alarm in self.get_enabled():
            if not self._is_alarm_today(alarm, weekday):
                continue

            alarm_minutes = self._time_to_minutes(alarm.time)

            if current_minutes == alarm_minutes:
                # Check if already triggered this minute
                last = self._last_triggered.get(alarm.id, 0)
                if time.ticks_diff(time.ticks_ms(), last) < 60_000:
                    continue

                self._trigger_alarm(alarm)
                self._last_triggered[alarm.id] = time.ticks_ms()

    def _trigger_alarm(self, alarm: Alarm):
        """Trigger alarm - queue critical speech."""
        print(f"[Alarms] Triggering alarm {alarm.id}: {alarm.label} at {alarm.time}")

        async def play_alarm():
            # Play alarm phrase + time
            # Locale is accessed via speech queue which has locale_manager
            await self.speech.speak_phrase("alarm")
            await asyncio.sleep_ms(500)
            await self.speech.speak_time(hour=int(alarm.time[:2]), minute=int(alarm.time[3:]))
            # Play alarm sound
            await self.dfplayer_play_alarm(alarm.sound)
            return True

        # We need dfplayer reference - will be set externally
        self._trigger_coro = play_alarm
        self.speech.enqueue_critical(play_alarm, f"alarm_{alarm.id}")

    def set_dfplayer(self, dfplayer):
        """Set DFPlayer reference for alarm sounds."""
        self._dfplayer = dfplayer

    async def dfplayer_play_alarm(self, sound_key: str):
        """Play alarm sound."""
        # Map sound key to folder/track
        sound_map = {
            "alarm_1": (7, 1),
            "alarm_2": (7, 2),
            "timer_done": (7, 13),
        }
        folder, track = sound_map.get(sound_key, (7, 1))
        await self._dfplayer.play_folder_track(folder, track)

    def snooze(self, alarm_id: int):
        """Snooze alarm for configured minutes."""
        if alarm_id in self.alarms:
            self.alarms[alarm_id].snoozed_until = time.ticks_add(time.ticks_ms(), self._snooze_minutes * 60_000)

    def dismiss(self, alarm_id: int):
        """Dismiss alarm (stop snooze)."""
        if alarm_id in self.alarms:
            self.alarms[alarm_id].snoozed_until = 0

    def add_alarm(self, time_str: str, days: int = config.DAYS_ALL,
                  sound: str = config.ALARM_DEFAULT_SOUND, label: str = "") -> Alarm:
        """Add new alarm."""
        alarm = Alarm(
            id=self._next_id,
            enabled=True,
            time=time_str,
            days=days,
            sound=sound,
            label=label or f"Alarm {self._next_id}",
        )
        self.alarms[self._next_id] = alarm
        self._next_id += 1
        self.save()
        return alarm

    def update_alarm(self, alarm_id: int, **kwargs) :
        """Update alarm properties."""
        if alarm_id not in self.alarms:
            return False
        alarm = self.alarms[alarm_id]
        for key, value in kwargs.items():
            if hasattr(alarm, key):
                setattr(alarm, key, value)
        self.save()
        return True

    def delete_alarm(self, alarm_id: int) :
        """Delete alarm."""
        if alarm_id in self.alarms:
            del self.alarms[alarm_id]
            self.save()
            return True
        return False

    def toggle_alarm(self, alarm_id: int) :
        """Toggle alarm enabled state."""
        if alarm_id in self.alarms:
            self.alarms[alarm_id].enabled = not self.alarms[alarm_id].enabled
            self.save()
            return self.alarms[alarm_id].enabled
        return False

    def get_alarm(self, alarm_id: int) :
        return self.alarms.get(alarm_id)

    def format_alarm(self, alarm: Alarm, locale: str = "ru") :
        """Format alarm for display."""
        days_str = self._days_to_str(alarm.days, locale)
        return f"{alarm.time} {days_str} {'ON' if alarm.enabled else 'OFF'} {alarm.label}"

    def _days_to_str(self, days: int, locale: str) :
        """Convert day bitmask to string."""
        if days == config.DAYS_ALL:
            return "Daily" if locale == "en" else "Ежедневно" if locale == "ru" else "Täglich"
        if days == config.DAYS_WEEKDAYS:
            return "Mon-Fri" if locale == "en" else "Пн-Пт" if locale == "ru" else "Mo-Fr"
        if days == config.DAYS_WEEKEND:
            return "Weekend" if locale == "en" else "Выходные" if locale == "ru" else "Wochenende"

        day_names = {
            "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "de": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
            "ua": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
        }
        names = day_names.get(locale, day_names["ru"])
        active = [names[i] for i in range(7) if days & (1 << i)]
        return ",".join(active)