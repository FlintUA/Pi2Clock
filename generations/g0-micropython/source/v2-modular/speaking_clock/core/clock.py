"""
Clock core: timekeeping, timezone, DST, RTC sync.
Single source of truth for current time.
"""

import time
from speaking_clock.hardware.rtc_ds1302 import RTC_DS1302


class Clock:
    """Central timekeeper. Syncs with RTC, provides formatted time, handles DST."""

    def __init__(self, rtc: RTC_DS1302):
        self.rtc = rtc
        self._timezone_offset = 0      # minutes from UTC
        self._dst_enabled = False
        self._dst_offset = 60          # DST offset in minutes
        self._last_rtc_sync = 0
        self._sync_interval_ms = 60_000  # sync with RTC every minute
        self._soft_time = None         # fallback if RTC fails
        self._rtc_failed = False

        # Weekday names for locales
        self.weekdays = {
            "ru": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
            "de": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
            "ua": ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"],
        }
        self.months = {
            "ru": ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
            "ru_short": ["", "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                         "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
            "de": ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
                   "Juli", "August", "September", "Oktober", "November", "Dezember"],
            "de_short": ["", "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
                         "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
            "ua": ["", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
                   "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"],
            "ua_short": ["", "Січ", "Лют", "Бер", "Кві", "Тра", "Чер",
                         "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"],
        }

    def now(self) -> Tuple[int, int, int, int, int, int, int]:
        """
        Get current time as tuple: (year, month, day, weekday, hour, minute, second)
        weekday: 1=Mon ... 7=Sun
        """
        # Try RTC first
        if not self._rtc_failed:
            try:
                dt = self.rtc.datetime()
                if dt and dt[0] > 2020:  # sanity check
                    # Check if time is not all zeros (uninitialized RTC)
                    if not (dt[4] == 0 and dt[5] == 0 and dt[6] == 0):
                        self._soft_time = dt
                        self._last_rtc_sync = time.ticks_ms()
                        return dt
                    else:
                        print("[Clock] RTC returns 0:0:0 - treating as uninitialized")
                        self._rtc_failed = True
            except Exception as e:
                print(f"[Clock] RTC read failed: {e}")
                self._rtc_failed = True

        # Fallback to soft time (incremented by main loop)
        if self._soft_time:
            return self._increment_soft_time()

        # Last resort: epoch
        return (2025, 1, 1, 3, 12, 0, 0)

    def _increment_soft_time(self) -> Tuple[int, int, int, int, int, int, int]:
        """Increment soft time by 1 second."""
        y, m, d, wd, h, mi, s = self._soft_time
        s += 1
        if s >= 60:
            s = 0
            mi += 1
            if mi >= 60:
                mi = 0
                h += 1
                if h >= 24:
                    h = 0
                    d += 1
                    wd = wd % 7 + 1
                    # Simple month rollover (approximate)
                    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    if d > days_in_month[m]:
                        d = 1
                        m += 1
                        if m > 12:
                            m = 1
                            y += 1
        self._soft_time = (y, m, d, wd, h, mi, s)
        return self._soft_time

    def set_time(self, dt) :
        """Set RTC and soft time."""
        try:
            self.rtc.datetime(dt)
            self._soft_time = dt
            self._rtc_failed = False
            print(f"[Clock] Time set to {dt[3]:02d}:{dt[4]:02d}:{dt[5]:02d} {dt[2]:02d}.{dt[1]:02d}.{dt[0]}")
            return True
        except Exception as e:
            print(f"[Clock] Set time failed: {e}")
            self._soft_time = dt
            self._rtc_failed = True
            return False

    def set_correction_ppm(self, ppm):
        """Set RTC calibration."""
        self.rtc.set_correction_ppm(ppm)

    def get_correction_ppm(self):
        return self.rtc.get_correction_ppm()

    def set_timezone(self, offset_minutes: int):
        """Set timezone offset from UTC in minutes."""
        self._timezone_offset = offset_minutes

    def set_dst(self, enabled: bool, offset_minutes: int = 60):
        """Enable/disable DST."""
        self._dst_enabled = enabled
        self._dst_offset = offset_minutes

    def is_quiet_time(self, quiet_start: int, quiet_end: int) :
        """Check if current time is in quiet hours."""
        _, _, _, _, hour, _, _ = self.now()
        if quiet_start <= quiet_end:
            return quiet_start <= hour < quiet_end
        else:  # crosses midnight
            return hour >= quiet_start or hour < quiet_end

    def format_time(self, show_seconds: bool = True, locale: str = "ru") :
        """Format time as HH:MM[:SS]."""
        _, _, _, _, h, m, s = self.now()
        if show_seconds:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{h:02d}:{m:02d}"

    def format_date(self, locale: str = "ru", short: bool = False) :
        """Format date as DD-MMM-YYYY or DD.MM.YYYY."""
        y, m, d, _, _, _, _ = self.now()
        months = self.months.get(f"{locale}_short" if short else locale, self.months[locale])
        return f"{d:02d}-{months[m]}-{y}"

    def format_weekday(self, locale: str = "ru", short: bool = False) :
        """Format weekday name."""
        _, _, _, wd, _, _, _ = self.now()
        weekdays = self.weekdays.get(locale, self.weekdays["ru"])
        name = weekdays[wd - 1]
        if short and len(name) > 3:
            return name[:3]
        return name

    def get_time_tuple(self) -> Tuple[int, int, int]:
        """Get (hour, minute, second)."""
        _, _, _, _, h, m, s = self.now()
        return h, m, s

    def get_date_tuple(self) -> Tuple[int, int, int]:
        """Get (year, month, day)."""
        y, m, d, _, _, _, _ = self.now()
        return y, m, d

    def tick(self):
        """Call from main loop every ~100ms to keep soft time updated."""
        if self._rtc_failed and self._soft_time:
            self._increment_soft_time()

        # Periodic RTC sync
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_rtc_sync) >= self._sync_interval_ms:
            self._last_rtc_sync = now
            try:
                dt = self.rtc.datetime()
                if dt and dt[0] > 2020:
                    self._soft_time = dt
                    self._rtc_failed = False
            except Exception:
                self._rtc_failed = True

    def seconds_until_next_minute(self) :
        """Seconds until next minute boundary."""
        _, _, _, _, _, _, s = self.now()
        return 60 - s

    def seconds_until_next_hour(self) :
        """Seconds until next hour boundary."""
        _, _, _, _, _, m, s = self.now()
        return (60 - m) * 60 - s

    def is_hour_boundary(self) :
        """True if at exact hour (minute=0, second=0)."""
        _, _, _, _, _, m, s = self.now()
        return m == 0 and s == 0

    def is_half_hour_boundary(self) :
        """True if at half hour (minute=30, second=0)."""
        _, _, _, _, _, m, s = self.now()
        return m == 30 and s == 0

    def test_rtc(self) :
        """Test RTC connection."""
        return self.rtc.test_connection()