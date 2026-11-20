#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SD Card Migration Script: Legacy v1 -> Modular v2 Structure

Run ON THE PICO (MicroPython) or ON PC (Python 3.8+).
Copies/renames files from /sd/sound/_sdcard/XX/ to new structure:
  /sd/tts/ru/, /sd/tts/de/, /sd/tts/ua/
  /sd/music/
  /sd/chimes/

LEGACY -> V2 MAPPING:
  Folder 01 -> tts/ru/hours/       (tracks 000-023)
  Folder 02 -> tts/ru/minutes/     (tracks 000-059)
  Folder 03 -> tts/ru/days/        (tracks 001-031)
  Folder 04 -> tts/ru/months/      (tracks 001-012)
  Folder 05 -> tts/ru/years/       (tracks 003=2023...)
  Folder 06 -> tts/ru/weekdays/    (tracks 001-007)
  Folder 07 -> tts/ru/phrases/     (RENUMBERED to v2 track numbers)
  Folder 08 -> music/              (tracks 001-045 -> track001.mp3...)
  Folder 11 -> tts/de/hours/       (tracks 000-023)
  Folder 12 -> tts/ru/minutes/     (tracks 000-059)
  Folder 13 -> tts/de/days/        (tracks 001-031)
  Folder 14 -> tts/de/months/      (tracks 000-011, 000=Januar)
  Folder 15 -> tts/de/years/       (tracks 003=2023...)
  Folder 16 -> tts/de/weekdays/    (tracks 001-007)
  Folder 17 -> tts/de/phrases/     (RENUMBERED to v2 track numbers)
  Folder 18 -> chimes/             (000=melody, 001-012=strikes)

V2 PHRASE TRACK NUMBERS (what locale/manager.py expects):
  alarm=1, timer_done=2, volume_on=5, volume_off=6,
  menu_enter=7, timer_set=10, timer_cancelled=11

LEGACY PHRASE TRACK NUMBERS (folder 07/17):
  timer_set=7, volume_on=8, volume_off=9, timer_cancelled=14, minuten=15
"""

import os
import sys
import shutil
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# Legacy source (on Pico SD card)
LEGACY_ROOT = "/sd/sound/_sdcard"

# New destination (on Pico SD card)
NEW_ROOT = "/sd"

# Set to True to actually copy files, False for dry-run
EXECUTE = True

# Set to True to keep legacy structure (backup), False to remove after verify
KEEP_LEGACY = True

# ============================================================
# MAPPING TABLES
# ============================================================

# Legacy folder -> (target_subdir, file_rename_function)
# file_rename_function: None = keep name, or function(old_name) -> new_name
FOLDER_MAP = {
    # Russian TTS
    "01": ("tts/ru/hours", None),
    "02": ("tts/ru/minutes", None),
    "03": ("tts/ru/days", None),
    "04": ("tts/ru/months", None),
    "05": ("tts/ru/years", None),
    "06": ("tts/ru/weekdays", None),
    "07": ("tts/ru/phrases", "rename_phrases_ru"),
    # Music
    "08": ("music", "rename_music"),
    # German TTS
    "11": ("tts/de/hours", None),
    "12": ("tts/de/minutes", None),
    "13": ("tts/de/days", None),
    "14": ("tts/de/months", None),
    "15": ("tts/de/years", None),
    "16": ("tts/de/weekdays", None),
    "17": ("tts/de/phrases", "rename_phrases_de"),
    # Chimes
    "18": ("chimes", "rename_chimes"),
}

# Legacy phrase track -> v2 phrase track
# legacy_track: v2_track
PHRASE_REMAP = {
    # Russian (folder 07) and German (folder 17) use same track numbers
    7: 10,   # timer_set
    8: 5,    # volume_on
    9: 6,    # volume_off
    14: 11,  # timer_cancelled
    15: 12,  # minuten (DE only, v2 uses 12 for "minutes" word)
    # v2 expects these but legacy doesn't have them - will create silence placeholders
    1: None,   # alarm - not in legacy, will create placeholder
    2: None,   # timer_done - not in legacy
}

# Music: legacy 001-045 -> music/track001.mp3 ...
def rename_music(old_name: str) -> str:
    """001.mp3 -> track001.mp3"""
    stem = Path(old_name).stem  # "001"
    try:
        num = int(stem)
        return f"track{num:03d}.mp3"
    except ValueError:
        return old_name

# Chimes: 000.mp3 -> melody.mp3, 001-012 -> strike_01.mp3 ... strike_12.mp3
def rename_chimes(old_name: str) -> str:
    stem = Path(old_name).stem
    try:
        num = int(stem)
        if num == 0:
            return "melody.mp3"
        elif 1 <= num <= 12:
            return f"strike_{num:02d}.mp3"
        else:
            return f"chime_{num:03d}.mp3"
    except ValueError:
        return old_name

# Phrases: remap track numbers to v2 convention
def rename_phrases_ru(old_name: str) -> str:
    return _rename_phrases(old_name, "ru")

def rename_phrases_de(old_name: str) -> str:
    return _rename_phrases(old_name, "de")

def _rename_phrases(old_name: str, lang: str) -> str:
    stem = Path(old_name).stem  # e.g., "007"
    try:
        legacy_num = int(stem)
        v2_num = PHRASE_REMAP.get(legacy_num)
        if v2_num is not None:
            return f"{v2_num:03d}.mp3"
        else:
            # Keep unknown tracks with original number but log warning
            print(f"  ⚠ {lang}: Unknown phrase track {legacy_num}, keeping as {old_name}")
            return old_name
    except ValueError:
        return old_name

# ============================================================
# UTILITIES
# ============================================================

def is_micropython() -> bool:
    return sys.implementation.name == "micropython"

def list_files_micropython(path: str) -> list:
    """List files in directory on MicroPython."""
    try:
        entries = os.ilistdir(path)
        files = []
        for entry in entries:
            name = entry[0]
            if entry[1] == 0x8000:  # file
                files.append(name)
        return sorted(files)
    except OSError:
        return []

def list_files_pc(path: Path) -> list:
    """List files in directory on PC."""
    if not path.exists():
        return []
    return sorted([f.name for f in path.iterdir() if f.is_file()])

def ensure_dir_micropython(path: str):
    """Create directory recursively on MicroPython."""
    parts = path.strip("/").split("/")
    current = ""
    for part in parts:
        current += "/" + part
        try:
            os.mkdir(current)
        except OSError as e:
            if e.args[0] != 17:  # EEXIST
                raise

def ensure_dir_pc(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def copy_file_micropython(src: str, dst: str):
    """Copy file on MicroPython (chunked to avoid memory issues)."""
    CHUNK_SIZE = 4096
    with open(src, "rb") as fsrc:
        with open(dst, "wb") as fdst:
            while True:
                chunk = fsrc.read(CHUNK_SIZE)
                if not chunk:
                    break
                fdst.write(chunk)

def copy_file_pc(src: Path, dst: Path):
    shutil.copy2(src, dst)

def file_exists_micropython(path: str) -> bool:
    try:
        os.stat(path)
        return True
    except OSError:
        return False

def file_size_micropython(path: str) -> int:
    return os.stat(path)[6]

# ============================================================
# MAIN MIGRATION LOGIC
# ============================================================

def migrate():
    print("=" * 60)
    print("SD Card Migration: Legacy v1 -> Modular v2")
    print("=" * 60)
    print(f"Source: {LEGACY_ROOT}")
    print(f"Dest:   {NEW_ROOT}")
    print(f"Mode:   {'EXECUTE' if EXECUTE else 'DRY-RUN'}")
    print(f"Keep legacy: {KEEP_LEGACY}")
    print()

    if is_micropython():
        print("Running on MicroPython (Pico)")
        list_files = list_files_micropython
        ensure_dir = ensure_dir_micropython
        copy_file = copy_file_micropython
        file_exists = file_exists_micropython
        join = lambda *p: "/".join(p)
        src_root = LEGACY_ROOT
        dst_root = NEW_ROOT
    else:
        print("Running on PC (Python)")
        list_files = lambda p: list_files_pc(Path(p))
        ensure_dir = lambda p: ensure_dir_pc(Path(p))
        copy_file = lambda s, d: copy_file_pc(Path(s), Path(d))
        file_exists = lambda p: Path(p).exists()
        join = lambda *p: str(Path(*p))
        src_root = LEGACY_ROOT
        dst_root = NEW_ROOT

    # Check source exists
    if not file_exists(src_root):
        print(f"❌ ERROR: Source not found: {src_root}")
        print("   Make sure SD card is mounted at /sd")
        return False

    total_copied = 0
    total_skipped = 0
    errors = []

    # Process each legacy folder
    for legacy_folder, (target_subdir, rename_fn_name) in FOLDER_MAP.items():
        src_folder = join(src_root, legacy_folder)
        dst_folder = join(dst_root, target_subdir)

        if not file_exists(src_folder):
            print(f"⏭  Folder {legacy_folder} not found, skipping")
            continue

        files = list_files(src_folder)
        if not files:
            print(f"⏭  Folder {legacy_folder} empty, skipping")
            continue

        print(f"\n📁 {legacy_folder} -> {target_subdir} ({len(files)} files)")

        if EXECUTE:
            ensure_dir(dst_folder)

        # Get rename function
        rename_fn = None
        if rename_fn_name:
            rename_fn = globals()[rename_fn_name]

        for fname in files:
            src_file = join(src_folder, fname)
            new_name = rename_fn(fname) if rename_fn else fname
            dst_file = join(dst_folder, new_name)

            if file_exists(dst_file):
                print(f"  ⏭  {new_name} already exists, skipping")
                total_skipped += 1
                continue

            if EXECUTE:
                try:
                    copy_file(src_file, dst_file)
                    size = file_size_micropython(src_file) if is_micropython() else Path(src_file).stat().st_size
                    print(f"  ✅ {fname} -> {new_name} ({size} bytes)")
                    total_copied += 1
                except Exception as e:
                    print(f"  ❌ {fname}: {e}")
                    errors.append(f"{src_file} -> {dst_file}: {e}")
            else:
                print(f"  🔍 {fname} -> {new_name}")
                total_copied += 1

    # Create missing phrase placeholders (alarm, timer_done)
    print("\n📝 Creating missing phrase placeholders...")
    for lang in ("ru", "de"):
        phrases_dir = join(dst_root, f"tts/{lang}/phrases")
        if EXECUTE:
            ensure_dir(phrases_dir)
        for track_num in (1, 2):  # alarm=1, timer_done=2
            fname = f"{track_num:03d}.mp3"
            fpath = join(phrases_dir, fname)
            if not file_exists(fpath):
                if EXECUTE:
                    # Create a tiny silent MP3 (1 frame, ~26ms)
                    # Minimal valid MP3: MPEG-1 Layer 3, 44.1kHz, mono, 128kbps
                    silent_mp3 = bytes([
                        0xFF, 0xFB, 0x90, 0x44,  # Frame header
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    ])
                    with open(fpath, "wb") as f:
                        f.write(silent_mp3)
                    print(f"  ✅ Created placeholder: {lang}/phrases/{fname}")
                else:
                    print(f"  🔍 Would create placeholder: {lang}/phrases/{fname}")

    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Files copied:   {total_copied}")
    print(f"Files skipped:  {total_skipped}")
    print(f"Errors:         {len(errors)}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")

    if not EXECUTE:
        print("\n⚠️  This was a DRY-RUN. Set EXECUTE = True to actually copy files.")
        print("   Edit this script and change EXECUTE = True")

    print("\n✅ Migration complete!")
    print(f"New structure at: {dst_root}")
    print("""
Expected structure:
/sd/
├── tts/
│   ├── ru/
│   │   ├── hours/      (000-023.mp3)
│   │   ├── minutes/    (000-059.mp3)
│   │   ├── days/       (001-031.mp3)
│   │   ├── months/     (001-012.mp3)
│   │   ├── years/      (003=2023...)
│   │   ├── weekdays/   (001-007.mp3)
│   │   └── phrases/    (001,002,005,006,007,010,011.mp3)
│   ├── de/
│   │   ├── hours/      (000-023.mp3)
│   │   ├── minutes/    (000-059.mp3)
│   │   ├── days/       (001-031.mp3)
│   │   ├── months/     (000-011.mp3)
│   │   ├── years/      (003=2023...)
│   │   ├── weekdays/   (001-007.mp3)
│   │   └── phrases/    (001,002,005,006,007,010,011.mp3)
│   └── ua/             (empty, for future)
├── music/
│   └── track001.mp3 ... track045.mp3
├── chimes/
│   ├── melody.mp3
│   ├── strike_01.mp3 ... strike_12.mp3
└── sound/_sdcard/      (legacy, kept for rollback)
""")
    return len(errors) == 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Allow overriding via command line
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif sys.argv[1] == "--execute":
            EXECUTE = True
        elif sys.argv[1] == "--dry-run":
            EXECUTE = False
        elif sys.argv[1] == "--no-keep-legacy":
            KEEP_LEGACY = False

    success = migrate()
    sys.exit(0 if success else 1)