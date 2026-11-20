"""
Configuration storage using JSON on Flash (LittleFS) with atomic writes.
Handles config migration, defaults, and auto-save with debouncing.
"""

import json
import os
import time

import speaking_clock.config as config


class Storage:
    """Manages persistent configuration storage."""

    def __init__(self):
        self._config = {}
        self._dirty = False
        self._last_save = 0
        self._save_debounce_ms = 500
        self._config_path = config.CONFIG_FILE
        self._backup_path = config.CONFIG_FILE + ".bak"

    def load(self) -> Dict[str, Any]:
        """Load config from file, apply defaults, migrate if needed."""
        try:
            with open(self._config_path, "r") as f:
                self._config = json.load(f)
            print(f"[Storage] Loaded config v{self._config.get('version', 0)}")
        except (OSError, ValueError) as e:
            print(f"[Storage] Config load failed: {e}, using defaults")
            self._config = {}

        # Migrate / apply defaults
        self._config = self._migrate_and_default(self._config)
        self._dirty = False
        return self._config

    def _migrate_and_default(self, cfg) -> Dict[str, Any]:
        """Apply defaults and migrate from old versions."""
        # Start with all defaults
        defaults = self._get_defaults()

        # If no version or old version, start fresh with defaults
        version = cfg.get("version", 0)
        if version < config.CONFIG_VERSION:
            print(f"[Storage] Migrating config from v{version} to v{config.CONFIG_VERSION}")
            # Keep any valid user settings from old config
            cfg = self._merge_configs(defaults, cfg)
            cfg["version"] = config.CONFIG_VERSION
        else:
            # Merge loaded config over defaults (user settings win)
            cfg = self._merge_configs(defaults, cfg)

        return cfg

    def _get_defaults(self) -> Dict[str, Any]:
        """Return complete default configuration."""
        return {
            "version": config.CONFIG_VERSION,
            "volume": config.VOLUME_DEFAULT,
            "language": config.DEFAULT_LOCALE,
            "quiet_mode": {
                "enabled": config.QUIET_MODE_ENABLED_DEFAULT,
                "start": config.QUIET_START_DEFAULT,
                "end": config.QUIET_END_DEFAULT,
            },
            "alarms": config.DEFAULT_ALARMS.copy(),
            "timer": {
                "last_value": config.TIMER_DEFAULT_SECONDS,
                "sound": config.ALARM_DEFAULT_SOUND,
                "repeat": False,
            },
            "pomodoro": {
                "work": config.POMODORO_WORK_DEFAULT,
                "short_break": config.POMODORO_SHORT_BREAK_DEFAULT,
                "long_break": config.POMODORO_LONG_BREAK_DEFAULT,
                "cycles": config.POMODORO_CYCLES_DEFAULT,
                "auto_start_break": True,
                "auto_start_work": False,
            },
            "chimes": {
                "hourly": config.CHIME_HOURLY_ENABLED_DEFAULT,
                "half_hour": config.CHIME_HALF_HOUR_ENABLED_DEFAULT,
                "style": config.CHIME_STYLE_DEFAULT,
            },
            "rtc_correction_ppm": config.RTC_CORRECTION_PPM_DEFAULT,
            "display": {
                "brightness": config.DISPLAY_BRIGHTNESS_DEFAULT,
                "timeout": config.DISPLAY_TIMEOUT_DEFAULT,
                "show_seconds": config.DISPLAY_SHOW_SECONDS_DEFAULT,
            },
            "first_boot_done": False,
        }

    def _merge_configs(self, defaults: Dict, user: Dict) -> Dict:
        """Recursively merge user config over defaults."""
        result = defaults.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key (e.g., 'quiet_mode.start')."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) :
        """Set config value by dot-notation key. Returns True if changed."""
        keys = key.split(".")
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        last_key = keys[-1]
        if target.get(last_key) != value:
            target[last_key] = value
            self._dirty = True
            return True
        return False

    def save(self, force: bool = False) :
        """Save config to file atomically. Returns True if saved."""
        now = time.ticks_ms()
        if not force and not self._dirty:
            return False
        if not force and time.ticks_diff(now, self._last_save) < self._save_debounce_ms:
            return False  # debounced

        try:
            # Atomic write: write to temp, then rename
            temp_path = self._config_path + ".tmp"
            with open(temp_path, "w") as f:
                json.dump(self._config, f)

            # Backup old config
            try:
                os.rename(self._config_path, self._backup_path)
            except OSError:
                pass  # no backup existed

            # Move temp to final
            os.rename(temp_path, self._config_path)

            self._dirty = False
            self._last_save = now
            print(f"[Storage] Config saved")
            return True
        except OSError as e:
            print(f"[Storage] Save failed: {e}")
            return False

    def save_now(self) :
        """Force immediate save (bypass debounce)."""
        return self.save(force=True)

    def is_first_boot(self) :
        """Check if this is the first boot (no config file existed)."""
        return not self._config.get("first_boot_done", False)

    def mark_first_boot_done(self):
        """Mark first boot as completed."""
        self.set("first_boot_done", True)
        self.save_now()

    def reset_to_defaults(self):
        """Reset configuration to factory defaults."""
        self._config = self._get_defaults()
        self._dirty = True
        self.save_now()

    def export_for_backup(self) :
        """Export config as JSON string for backup."""
        return json.dumps(self._config)

    def import_from_backup(self, json_str: str) :
        """Import config from JSON string."""
        try:
            cfg = json.loads(json_str)
            cfg = self._migrate_and_default(cfg)
            self._config = cfg
            self._dirty = True
            return self.save_now()
        except (ValueError, KeyError) as e:
            print(f"[Storage] Import failed: {e}")
            return False


# Global instance
storage = Storage()