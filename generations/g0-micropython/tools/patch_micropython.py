#!/usr/bin/env python3
"""
Patch script to make code compatible with minimal MicroPython firmware.
Run on PC, then copy patched files to Pico via Thonny.
OR run directly in Thonny REPL on Pico.
"""

import os
import re

# ============================================================
# REPLACEMENTS FOR EACH FILE
# ============================================================

PATCHES = {
    "speaking_clock/core/speech.py": {
        "imports": [
            (r"from typing import Optional, Callable, Awaitable\n", ""),
            (r"from dataclasses import dataclass\n", ""),
            (r"from enum import IntEnum\n", ""),
        ],
        "classes": [
            # SpeechPriority IntEnum -> regular class
            (r"class SpeechPriority\(IntEnum\):\n    CRITICAL = 0.*?\n    LOW = 3",
             """class SpeechPriority:
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3"""),
            # SpeechItem dataclass -> regular class
            (r"@dataclass\nclass SpeechItem:\n    priority: SpeechPriority\n    coro: Callable\[\[\], Awaitable\[bool\]\]\n    description: str\n    interruptible: bool = True",
             """class SpeechItem:
    def __init__(self, priority, coro, description, interruptible=True):
        self.priority = priority
        self.coro = coro
        self.description = description
        self.interruptible = interruptible"""),
        ],
        "type_hints": [
            (r"def __init__\(self, dfplayer, locale_manager\):", "def __init__(self, dfplayer, locale_manager):"),
            (r"def set_quiet_mode\(self, enabled: bool\):", "def set_quiet_mode(self, enabled):"),
            (r"def is_quiet_mode\(self\) -> bool:", "def is_quiet_mode(self):"),
            (r"def enqueue\(self, priority: SpeechPriority, coro: Callable\[\[\], Awaitable\[bool\]\], description: str = \"\", interruptible: bool = True\) -> bool:", "def enqueue(self, priority, coro, description=\"\", interruptible=True):"),
            (r"def enqueue_critical\(self, coro: Callable\[\[\], Awaitable\[bool\]\], description: str = \"\"\) -> bool:", "def enqueue_critical(self, coro, description=\"\"):"),
            (r"def enqueue_high\(self, coro: Callable\[\[\], Awaitable\[bool\]\], description: str = \"\"\) -> bool:", "def enqueue_high(self, coro, description=\"\"):"),
            (r"def enqueue_normal\(self, coro: Callable\[\[\], Awaitable\[bool\]\], description: str = \"\"\) -> bool:", "def enqueue_normal(self, coro, description=\"\"):"),
            (r"def enqueue_low\(self, coro: Callable\[\[\], Awaitable\[bool\]\], description: str = \"\"\) -> bool:", "def enqueue_low(self, coro, description=\"\"):"),
            (r"def clear_queue\(self, priority: SpeechPriority = None\):", "def clear_queue(self, priority=None):"),
            (r"async def process\(self\):", "async def process(self):"),
            (r"async def _play_item\(self, item: SpeechItem, priority: SpeechPriority\):", "async def _play_item(self, item, priority):"),
            (r"async def speak_time\(self, hour: int, minute: int, lang: str = None\) -> bool:", "async def speak_time(self, hour, minute, lang=None):"),
            (r"async def speak_date\(self, lang: str = None\) -> bool:", "async def speak_date(self, lang=None):"),
            (r"async def speak_phrase\(self, phrase_key: str, lang: str = None, \*\*kwargs\) -> bool:", "async def speak_phrase(self, phrase_key, lang=None, **kwargs):"),
            (r"async def play_chime\(self, hour: int, lang: str = None\) -> bool:", "async def play_chime(self, hour, lang=None):"),
            (r"async def play_beep\(self, count: int = 1, lang: str = None\) -> bool:", "async def play_beep(self, count=1, lang=None):"),
            (r"def get_queue_status\(self\) -> dict:", "def get_queue_status(self):"),
        ]
    },

    "speaking_clock/core/music.py": {
        "imports": [
            (r"from typing import List, Optional, Tuple\n", ""),
            (r"from dataclasses import dataclass\n", ""),
        ],
        "classes": [
            (r"@dataclass\nclass Track:\n    path: str\n    folder: str\n    name: str\n    size: int = 0",
             """class Track:
    def __init__(self, path, folder, name, size=0):
        self.path = path
        self.folder = folder
        self.name = name
        self.size = size"""),
        ],
        "type_hints": [
            (r"def __init__\(self, dfplayer, speech\):", "def __init__(self, dfplayer, speech):"),
            (r"async def initialize\(self, music_root: str = \"/sd/music\"\):", "async def initialize(self, music_root=\"/sd/music\"):"),
            (r"async def _scan_music\(self, root: str\):", "async def _scan_music(self, root):"),
            (r"def _shuffle\(self\):", "def _shuffle(self):"),
            (r"def play\(self\) -> bool:", "def play(self):"),
            (r"def pause\(self\):", "def pause(self):"),
            (r"def stop\(self\):", "def stop(self):"),
            (r"def next_track\(self\):", "def next_track(self):"),
            (r"def prev_track\(self\):", "def prev_track(self):"),
            (r"def shuffle\(self\):", "def shuffle(self):"),
            (r"def set_mode\(self, mode: str\):", "def set_mode(self, mode):"),
            (r"def get_current_track\(self\) -> Optional\[Track\]:", "def get_current_track(self):"),
            (r"def get_playlist_info\(self\) -> dict:", "def get_playlist_info(self):"),
            (r"def is_playing\(self\) -> bool:", "def is_playing(self):"),
            (r"def is_scanned\(self\) -> bool:", "def is_scanned(self):"),
        ]
    },

    "speaking_clock/core/alarms.py": {
        "imports": [
            (r"from dataclasses import dataclass, asdict\n", ""),
            (r"from typing import List, Optional\n", ""),
        ],
        "classes": [
            (r"@dataclass\nclass Alarm:\n    id: int\n    enabled: bool\n    time: str  # \"HH:MM\"\n    days: int  # bitmask\n    sound: str\n    label: str",
             """class Alarm:
    def __init__(self, id, enabled, time, days, sound, label):
        self.id = id
        self.enabled = enabled
        self.time = time
        self.days = days
        self.sound = sound
        self.label = label
    def to_dict(self):
        return {"id": self.id, "enabled": self.enabled, "time": self.time,
                "days": self.days, "sound": self.sound, "label": self.label}
    @staticmethod
    def from_dict(d):
        return Alarm(d["id"], d["enabled"], d["time"], d["days"], d["sound"], d["label"])"""),
        ],
        "type_hints": [
            (r"def __init__\(self, storage, speech, clock\):", "def __init__(self, storage, speech, clock):"),
            (r"def load\(self\):", "def load(self):"),
            (r"def save\(self\):", "def save(self):"),
            (r"def add\(self, alarm: Alarm\):", "def add(self, alarm):"),
            (r"def remove\(self, alarm_id: int\):", "def remove(self, alarm_id):"),
            (r"def get\(self, alarm_id: int\) -> Optional\[Alarm\]:", "def get(self, alarm_id):"),
            (r"def get_all\(self\) -> List\[Alarm\]:", "def get_all(self):"),
            (r"def set_dfplayer\(self, dfplayer\):", "def set_dfplayer(self, dfplayer):"),
            (r"def check_alarms\(self\):", "def check_alarms(self):"),
            (r"def _check_alarm\(self, alarm: Alarm\):", "def _check_alarm(self, alarm):"),
        ]
    },

    "speaking_clock/core/timer.py": {
        "imports": [
            (r"from dataclasses import dataclass\n", ""),
            (r"from typing import Optional\n", ""),
            (r"from enum import IntEnum\n", ""),
        ],
        "classes": [
            # TimerState IntEnum
            (r"class TimerState\(IntEnum\):\n    STOPPED = 0\n    RUNNING = 1\n    PAUSED = 2\n    FINISHED = 3",
             """class TimerState:
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3"""),
            # TimerConfig dataclass
            (r"@dataclass\nclass TimerConfig:\n    work: int = 1500\n    short_break: int = 300\n    long_break: int = 900\n    cycles: int = 4",
             """class TimerConfig:
    def __init__(self, work=1500, short_break=300, long_break=900, cycles=4):
        self.work = work
        self.short_break = short_break
        self.long_break = long_break
        self.cycles = cycles"""),
            # PomodoroState dataclass
            (r"@dataclass\nclass PomodoroState:\n    phase: str\n    cycle: int\n    remaining: int\n    total: int",
             """class PomodoroState:
    def __init__(self, phase, cycle, remaining, total):
        self.phase = phase
        self.cycle = cycle
        self.remaining = remaining
        self.total = total"""),
        ],
        "type_hints": [
            (r"def __init__\(self, speech, dfplayer\):", "def __init__(self, speech, dfplayer):"),
            (r"def set_duration\(self, seconds: int\):", "def set_duration(self, seconds):"),
            (r"def add_seconds\(self, delta: int\):", "def add_seconds(self, delta):"),
            (r"def get_duration\(self\) -> int:", "def get_duration(self):"),
            (r"def get_state\(self\) -> TimerState:", "def get_state(self):"),
            (r"def start\(self\):", "def start(self):"),
            (r"def pause\(self\):", "def pause(self):"),
            (r"def reset\(self\):", "def reset(self):"),
            (r"def update\(self\):", "def update(self):"),
            (r"def get_remaining\(self\) -> int:", "def get_remaining(self):"),
            (r"async def _finish\(self\):", "async def _finish(self):"),
        ]
    },
}

# ============================================================
# GENERIC CLEANUP (applies to all .py files in speaking_clock)
# ============================================================

GENERIC_REPLACEMENTS = [
    # Remove typing imports
    (r"from typing import .*\n", ""),
    (r"import typing\n", ""),
    # Remove dataclasses imports
    (r"from dataclasses import .*\n", ""),
    # Remove enum imports (IntEnum replaced)
    (r"from enum import IntEnum\n", ""),
    # Remove type hints from function signatures
    (r":\s*Optional\[.*?\]", ""),
    (r":\s*List\[.*?\]", ""),
    (r":\s*Tuple\[.*?\]", ""),
    (r":\s*Callable\[\[.*?\],.*?\]", ""),
    (r":\s*Awaitable\[.*?\]", ""),
    (r"->\s*bool", ""),
    (r"->\s*int", ""),
    (r"->\s*str", ""),
    (r"->\s*dict", ""),
    (r"->\s*Optional\[.*?\]", ""),
    # Remove @dataclass decorators
    (r"@dataclass\n", ""),
]


def patch_file(filepath, patches):
    """Apply patches to a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  [SKIP] Not found: {filepath}")
        return False
    except Exception as e:
        print(f"  [ERR] Read {filepath}: {e}")
        return False

    original = content

    # Apply file-specific patches
    if filepath in patches:
        for pattern, replacement in patches[filepath].get("imports", []):
            content = re.sub(pattern, replacement, content)
        for pattern, replacement in patches[filepath].get("classes", []):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        for pattern, replacement in patches[filepath].get("type_hints", []):
            content = re.sub(pattern, replacement, content)

    # Apply generic patches
    for pattern, replacement in GENERIC_REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    if content != original:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  [OK] Patched: {filepath}")
            return True
        except Exception as e:
            print(f"  [ERR] Write {filepath}: {e}")
            return False
    else:
        print(f"  [SKIP] No changes: {filepath}")
        return False


def main():
    print("=" * 60)
    print("MicroPython Compatibility Patcher")
    print("=" * 60)

    # Files to patch
    target_files = [
        "speaking_clock/core/speech.py",
        "speaking_clock/core/music.py",
        "speaking_clock/core/alarms.py",
        "speaking_clock/core/timer.py",
        "speaking_clock/core/clock.py",
        "speaking_clock/hardware/dfplayer.py",
        "speaking_clock/locale/manager.py",
        "speaking_clock/storage.py",
        "speaking_clock/config.py",
        "main.py",
    ]

    patched = 0
    for f in target_files:
        if patch_file(f, PATCHES):
            patched += 1

    print(f"\nPatched {patched} files.")
    print("Copy files to Pico and test.")


if __name__ == "__main__":
    main()