"""
Locale manager: handles TTS folder mapping, phrases, and language switching.
"""

import speaking_clock.config as config


class LocaleManager:
    """Manages languages, TTS folder mappings, and phrase lookups."""

    def __init__(self):
        self.current_lang = config.DEFAULT_LOCALE
        self.lang_cycle = config.LOCALE_CYCLE_ORDER

        # TTS folder base numbers for each language
        # Folder structure: /tts/{lang}/hours/, /tts/{lang}/minutes/, etc.
        # DFPlayer folder numbers are assigned sequentially
        self.tts_folder_map = {
            "ru": {
                "base": 1,       # Starting folder number for RU
                "hours": 1,
                "minutes": 2,
                "days": 3,
                "months": 4,
                "years": 5,
                "weekdays": 6,
                "phrases": 7,
            },
            "de": {
                "base": 11,      # Starting folder number for DE
                "hours": 11,
                "minutes": 12,
                "days": 13,
                "months": 14,
                "years": 15,
                "weekdays": 16,
                "phrases": 17,
            },
            "ua": {
                "base": 21,      # Starting folder number for UA
                "hours": 21,
                "minutes": 22,
                "days": 23,
                "months": 24,
                "years": 25,
                "weekdays": 26,
                "phrases": 27,
            },
        }

        # Phrase track numbers within phrases folder
        self.phrase_tracks = {
            "ru": {
                "alarm": 1,
                "timer_done": 2,
                "chime_hour": 3,
                "chime_half": 4,
                "volume_on": 5,
                "volume_off": 6,
                "menu_enter": 7,
                "menu_exit": 8,
                "settings_saved": 9,
                "timer_set": 10,
                "timer_cancelled": 11,
                "work_start": 12,
                "short_break": 13,
                "long_break": 14,
            },
            "de": {
                "alarm": 1,
                "timer_done": 2,
                "chime_hour": 3,
                "chime_half": 4,
                "volume_on": 5,
                "volume_off": 6,
                "menu_enter": 7,
                "menu_exit": 8,
                "settings_saved": 9,
                "timer_set": 10,
                "timer_cancelled": 11,
                "work_start": 12,
                "short_break": 13,
                "long_break": 14,
            },
            "ua": {
                "alarm": 1,
                "timer_done": 2,
                "chime_hour": 3,
                "chime_half": 4,
                "volume_on": 5,
                "volume_off": 6,
                "menu_enter": 7,
                "menu_exit": 8,
                "settings_saved": 9,
                "timer_set": 10,
                "timer_cancelled": 11,
                "work_start": 12,
                "short_break": 13,
                "long_break": 14,
            },
        }

        # UI strings for display
        self.ui_strings = {
            "ru": {
                "main_screen": "Главный экран",
                "menu": "Меню",
                "alarms": "Будильники",
                "timers": "Таймеры",
                "sound": "Звук",
                "time_date": "Время и дата",
                "music": "Музыка",
                "display": "Дисплей",
                "system": "Система",
                "save_exit": "Сохранить и выйти",
                "enabled": "Вкл",
                "disabled": "Выкл",
                "daily": "Ежедневно",
                "weekdays": "Пн-Пт",
                "weekend": "Выходные",
                "once": "Однократно",
                "volume": "Громкость",
                "language": "Язык",
                "quiet_mode": "Тихий режим",
                "chimes": "Бой часов",
                "brightness": "Яркость",
                "timeout": "Таймаут",
                "seconds": "Секунды",
                "hour_format": "Формат времени",
                "set_time": "Установить время",
                "set_date": "Установить дату",
                "rtc_correction": "Коррекция хода",
                "timer_countdown": "Обратный отсчёт",
                "timer_pomodoro": "Помодоро",
                "timer_intervals": "Интервалы",
                "timer_stopwatch": "Секундомер",
                "preset": "Предустановка",
                "sound_preview": "Прослушка",
                "back": "Назад",
                "ok": "ОК",
                "cancel": "Отмена",
                "delete": "Удалить",
                "add": "Добавить",
                "edit": "Изменить",
                "copy": "Копировать",
                "snooze": "Отложить",
                "dismiss": "Отменить",
                "running": "Идёт",
                "paused": "Пауза",
                "finished": "Готово",
                "work": "Работа",
                "break": "Отдых",
                "cycles": "Циклов",
            },
            "de": {
                "main_screen": "Hauptbildschirm",
                "menu": "Menü",
                "alarms": "Wecker",
                "timers": "Timer",
                "sound": "Ton",
                "time_date": "Zeit & Datum",
                "music": "Musik",
                "display": "Anzeige",
                "system": "System",
                "save_exit": "Speichern & Beenden",
                "enabled": "Ein",
                "disabled": "Aus",
                "daily": "Täglich",
                "weekdays": "Mo-Fr",
                "weekend": "Wochenende",
                "once": "Einmalig",
                "volume": "Lautstärke",
                "language": "Sprache",
                "quiet_mode": "Ruhemodus",
                "chimes": "Schlaguhr",
                "brightness": "Helligkeit",
                "timeout": "Timeout",
                "seconds": "Sekunden",
                "hour_format": "Zeitformat",
                "set_time": "Zeit einstellen",
                "set_date": "Datum einstellen",
                "rtc_correction": "Gangkorrektur",
                "timer_countdown": "Countdown",
                "timer_pomodoro": "Pomodoro",
                "timer_intervals": "Intervalle",
                "timer_stopwatch": "Stoppuhr",
                "preset": "Voreinstellung",
                "sound_preview": "Vorschau",
                "back": "Zurück",
                "ok": "OK",
                "cancel": "Abbrechen",
                "delete": "Löschen",
                "add": "Hinzufügen",
                "edit": "Bearbeiten",
                "copy": "Kopieren",
                "snooze": "Schlummern",
                "dismiss": "Abbrechen",
                "running": "Läuft",
                "paused": "Pause",
                "finished": "Fertig",
                "work": "Arbeit",
                "break": "Pause",
                "cycles": "Zyklen",
            },
            "ua": {
                "main_screen": "Головний екран",
                "menu": "Меню",
                "alarms": "Будільники",
                "timers": "Таймери",
                "sound": "Звук",
                "time_date": "Час і дата",
                "music": "Музика",
                "display": "Дисплей",
                "system": "Система",
                "save_exit": "Зберегти і вийти",
                "enabled": "Увімк",
                "disabled": "Вимк",
                "daily": "Щодня",
                "weekdays": "Пн-Пт",
                "weekend": "Вихідні",
                "once": "Разово",
                "volume": "Гучність",
                "language": "Мова",
                "quiet_mode": "Тихий режим",
                "chimes": "Бой годин",
                "brightness": "Яскравість",
                "timeout": "Таймаут",
                "seconds": "Секунди",
                "hour_format": "Формат часу",
                "set_time": "Встановити час",
                "set_date": "Встановити дату",
                "rtc_correction": "Корекція ходу",
                "timer_countdown": "Зворотний відлік",
                "timer_pomodoro": "Помодоро",
                "timer_intervals": "Інтервали",
                "timer_stopwatch": "Секундомір",
                "preset": "Предустановка",
                "sound_preview": "Прослуховування",
                "back": "Назад",
                "ok": "ОК",
                "cancel": "Скасувати",
                "delete": "Видалити",
                "add": "Додати",
                "edit": "Змінити",
                "copy": "Копіювати",
                "snooze": "Відкласти",
                "dismiss": "Скасувати",
                "running": "Йде",
                "paused": "Пауза",
                "finished": "Готово",
                "work": "Робота",
                "break": "Відпочинок",
                "cycles": "Цикли",
            },
        }

    def get_tts_base(self, lang: str = None) :
        """Get base folder number for TTS in language."""
        lang = lang or self.current_lang
        return self.tts_folder_map.get(lang, self.tts_folder_map["ru"])["base"]

    def get_tts_folder(self, category: str, lang: str = None) :
        """Get DFPlayer folder number for TTS category."""
        lang = lang or self.current_lang
        return self.tts_folder_map.get(lang, self.tts_folder_map["ru"]).get(category, 1)

    def get_phrase_folder(self, lang: str = None) :
        """Get phrases folder number."""
        return self.get_tts_folder("phrases", lang)

    def get_phrase_track(self, phrase_key: str, lang: str = None) :
        """Get track number for phrase."""
        lang = lang or self.current_lang
        return self.phrase_tracks.get(lang, self.phrase_tracks["ru"]).get(phrase_key)

    def get_ui_string(self, key: str, lang: str = None) :
        """Get UI string for current language."""
        lang = lang or self.current_lang
        return self.ui_strings.get(lang, self.ui_strings["ru"]).get(key, key)

    def set_language(self, lang: str) :
        """Set current language."""
        if lang in self.lang_cycle:
            self.current_lang = lang
            return True
        return False

    def cycle_language(self) :
        """Cycle to next language."""
        idx = self.lang_cycle.index(self.current_lang)
        self.current_lang = self.lang_cycle[(idx + 1) % len(self.lang_cycle)]
        return self.current_lang

    def get_current_language(self):
        return self.current_lang

    def get_language_name(self, lang=None):
        """Get native language name."""
        names = {"ru": "Русский", "de": "Deutsch", "ua": "Українська"}
        lang = lang or self.current_lang
        return names.get(lang, lang)

    def format_time_phrase(self, hour, minute, lang=None):
        """Get folder/track pairs for speaking time."""
        lang = lang or self.current_lang
        tts = self.tts_folder_map.get(lang, self.tts_folder_map["ru"])
        return (
            (tts["hours"], hour),
            (tts["minutes"], minute),
        )

    def format_date_phrase(self, year, month, day, weekday, lang=None):
        """Get folder/track pairs for speaking date."""
        lang = lang or self.current_lang
        tts = self.tts_folder_map.get(lang, self.tts_folder_map["ru"])
        # Year offset from 2020
        year_track = year - 2020
        return [
            (tts["weekdays"], weekday),
            (tts["days"], day),
            (tts["months"], month),
            (tts["years"], max(0, year_track)),
        ]

    def get_phrase_sequence(self, phrase_key, lang=None):
        """
        Get list of (folder, track) tuples for a phrase.
        Supports multi-track phrases (e.g., "14:30" = hour + minute).
        Returns empty list if phrase not found.
        """
        lang = lang or self.current_lang
        track = self.get_phrase_track(phrase_key, lang)
        if track is None:
            return []
        folder = self.get_phrase_folder(lang)
        return [(folder, track)]

    def get_chime_sequence(self, hour, lang=None):
        """
        Get chime sequence for hourly chime.
        Returns list of (folder, track) tuples.
        Hour 0 = 12 strikes (midnight/noon).
        """
        lang = lang or self.current_lang
        # Chimes folder is 18 (legacy), new structure uses /chimes/
        # Use folder 18 for DFPlayer compatibility (legacy folder at root)
        chimes_folder = 18
        strikes = 12 if hour == 0 else hour if hour <= 12 else hour - 12
        if strikes == 0:
            strikes = 12
        # melody.mp3 is track 0 (or 1 in DFPlayer), strikes are 1-12
        # DFPlayer track numbers: 1 = melody, 2-13 = strike_1...strike_12
        # Legacy: 000.mp3 = melody, 001-012 = strikes
        sequence = [(chimes_folder, 1)]  # melody (track 1 = 001.mp3 in legacy)
        for i in range(strikes):
            sequence.append((chimes_folder, i + 2))  # strikes (2-13)
        return sequence

    def get_beep_sequence(self, count, lang=None):
        """
        Get beep sequence.
        Returns list of (folder, track) tuples.
        """
        lang = lang or self.current_lang
        # Beeps folder is 19 (legacy)
        beeps_folder = 19
        if count == 1:
            return [(beeps_folder, 1)]  # beep_01.mp3
        elif count == 2:
            return [(beeps_folder, 2)]  # beep_02.mp3
        else:
            # Multiple beeps - repeat beep_01
            return [(beeps_folder, 1)] * count