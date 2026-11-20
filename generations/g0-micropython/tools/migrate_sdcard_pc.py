#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SD Card Migration Script: Legacy v1 (E: drive structure) -> Modular v2 Structure

Run ON PC (Python 3.8+) with SD card in reader.
Source: E:/01, E:/02, ... E:/21  (folders directly in root)
Dest:   E:/tts/, E:/music/, E:/chimes/, E:/beeps/

REAL FOLDER MAPPING (from your E: drive):
  01 -> tts/ru/hours          (000-023)
  02 -> tts/ru/minutes        (000-059)
  03 -> tts/ru/days           (001-031)
  04 -> tts/ru/months         (001-012)
  05 -> tts/ru/years          (003=2023...)
  06 -> tts/ru/weekdays       (001-007)
  07 -> tts/ru/phrases        (RENUMBERED to v2 track numbers)
  08 -> music/                (001-045 -> track001.mp3...)
  09 -> tts/ru/numbers_0_30   (000-030)  -- extra, keep for compatibility
  10 -> tts/de/hours          (000-023)  -- NOTE: folder 10, not 11!
  11 -> SKIP (empty)
  12 -> tts/de/minutes        (000-059)
  13 -> tts/de/days           (001-031)
  14 -> tts/de/months         (000-011)
  15 -> tts/de/years          (003=2023...)
  16 -> tts/de/weekdays       (001-007)
  17 -> tts/de/phrases        (RENUMBERED to v2 track numbers)
  18 -> chimes/               (000=melody, 001-012=strikes)
  19 -> beeps/                (001=beep1, 002=beep2)
  20,21 -> SKIP (empty)
"""

import os
import sys
import shutil
from pathlib import Path

# ============================================================
# CONFIGURATION - ADJUST THESE FOR YOUR DRIVE
# ============================================================

SOURCE_DRIVE = "E:"           # Your SD card drive letter
DEST_DRIVE = "E:"             # Same drive (in-place restructure)

# Set to True to actually copy files, False for dry-run
EXECUTE = False               # CHANGE TO True TO ACTUALLY COPY

# Set to True to keep legacy folders (01-21) after migration
KEEP_LEGACY = True

# ============================================================
# MAPPING: legacy_folder -> (target_subdir, rename_function_name)
# ============================================================

FOLDER_MAP = {
    # Russian TTS
    "01": ("tts/ru/hours", None),
    "02": ("tts/ru/minutes", None),
    "03": ("tts/ru/days", None),
    "04": ("tts/ru/months", None),
    "05": ("tts/ru/years", None),
    "06": ("tts/ru/weekdays", None),
    "07": ("tts/ru/phrases", "rename_phrases"),
    # Music
    "08": ("music", "rename_music"),
    # Extra: RU numbers 0-30 (keep for compatibility)
    "09": ("tts/ru/numbers_0_30", None),
    # German TTS - hours in folder 11 (not 10 as in description)!
    "10": None,  # Empty - skip
    "11": ("tts/de/hours", None),
    "12": ("tts/de/minutes", None),
    "13": ("tts/de/days", None),
    "14": ("tts/de/months", None),
    "15": ("tts/de/years", None),
    "16": ("tts/de/weekdays", None),
    "17": ("tts/de/phrases", "rename_phrases"),
    # Chimes
    "18": ("chimes", "rename_chimes"),
    # Simple beeps
    "19": ("beeps", "rename_beeps"),
    "20": None,  # Empty - skip
    "21": None,  # Empty - skip
}

# Legacy phrase track -> v2 phrase track (same for RU folder 07 and DE folder 17)
# v2 expects: alarm=1, timer_done=2, volume_on=5, volume_off=6, menu_enter=7, timer_set=10, timer_cancelled=11
# Legacy has:  timer_set=7, volume_on=8, volume_off=9, timer_cancelled=14, minuten=15
PHRASE_REMAP = {
    7: 10,   # timer_set
    8: 5,    # volume_on
    9: 6,    # volume_off
    14: 11,  # timer_cancelled
    15: 12,  # minuten (DE) -> v2 uses 12 for "minutes" word
    # Missing in legacy - will create silent placeholders:
    1: None,   # alarm
    2: None,   # timer_done
}

# ============================================================
# RENAME FUNCTIONS
# ============================================================

def rename_music(old_name: str) -> str:
    """001.mp3 -> track001.mp3"""
    stem = Path(old_name).stem
    try:
        num = int(stem)
        return f"track{num:03d}.mp3"
    except ValueError:
        return old_name

def rename_chimes(old_name: str) -> str:
    """000.mp3 -> melody.mp3, 001-012 -> strike_01.mp3..."""
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

def rename_beeps(old_name: str) -> str:
    """001.mp3 -> beep_01.mp3, 002.mp3 -> beep_02.mp3"""
    stem = Path(old_name).stem
    try:
        num = int(stem)
        return f"beep_{num:02d}.mp3"
    except ValueError:
        return old_name

def rename_phrases(old_name: str) -> str:
    """Remap legacy phrase track numbers to v2 convention."""
    stem = Path(old_name).stem
    try:
        legacy_num = int(stem)
        v2_num = PHRASE_REMAP.get(legacy_num)
        if v2_num is not None:
            return f"{v2_num:03d}.mp3"
        else:
            print(f"  [WARN] Unknown phrase track {legacy_num}, keeping as {old_name}")
            return old_name
    except ValueError:
        return old_name

# ============================================================
# UTILITIES
# ============================================================

def list_files(path: Path) -> list:
    if not path.exists():
        return []
    return sorted([f.name for f in path.iterdir() if f.is_file()])

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def copy_file(src: Path, dst: Path):
    shutil.copy2(src, dst)

def create_silent_mp3(path: Path):
    """Create minimal valid silent MP3 (1 frame, ~26ms)."""
    # MPEG-1 Layer 3, 44.1kHz, mono, 128kbps frame header + minimal data
    silent_mp3 = bytes([
        0xFF, 0xFB, 0x90, 0x44,  # Frame header
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
    with open(path, "wb") as f:
        f.write(silent_mp3)

# ============================================================
# MAIN
# ============================================================

def migrate():
    print("=" * 60)
    print("SD Card Migration: Legacy (E:/) -> Modular v2")
    print("=" * 60)
    print(f"Source: {SOURCE_DRIVE}/")
    print(f"Dest:   {DEST_DRIVE}/")
    print(f"Mode:   {'EXECUTE' if EXECUTE else 'DRY-RUN'}")
    print(f"Keep legacy folders: {KEEP_LEGACY}")
    print()

    src_root = Path(SOURCE_DRIVE)
    dst_root = Path(DEST_DRIVE)

    if not src_root.exists():
        print(f"[ERR] ERROR: Source drive not found: {src_root}")
        return False

    total_copied = 0
    total_skipped = 0
    errors = []

    for legacy_folder, mapping in FOLDER_MAP.items():
        if mapping is None:
            print(f"[SKIP]  Folder {legacy_folder} -> SKIP (empty/not used)")
            continue

        target_subdir, rename_fn_name = mapping
        src_folder = src_root / legacy_folder
        dst_folder = dst_root / target_subdir

        if not src_folder.exists():
            print(f"[SKIP]  Folder {legacy_folder} not found, skipping")
            continue

        files = list_files(src_folder)
        if not files:
            print(f"[SKIP]  Folder {legacy_folder} empty, skipping")
            continue

        print(f"\n[FOLDER] {legacy_folder} -> {target_subdir} ({len(files)} files)")

        if EXECUTE:
            ensure_dir(dst_folder)

        rename_fn = globals().get(rename_fn_name) if rename_fn_name else None

        for fname in files:
            src_file = src_folder / fname
            new_name = rename_fn(fname) if rename_fn else fname
            dst_file = dst_folder / new_name

            if dst_file.exists():
                print(f"  [SKIP]  {new_name} already exists, skipping")
                total_skipped += 1
                continue

            if EXECUTE:
                try:
                    copy_file(src_file, dst_file)
                    size = src_file.stat().st_size
                    print(f"  [OK] {fname} -> {new_name} ({size:,} bytes)")
                    total_copied += 1
                except Exception as e:
                    print(f"  [ERR] {fname}: {e}")
                    errors.append(f"{src_file} -> {dst_file}: {e}")
            else:
                print(f"  [SCAN] {fname} -> {new_name}")
                total_copied += 1

    # Create missing phrase placeholders (alarm=1, timer_done=2) for RU and DE
    print("\n[NOTE] Creating missing phrase placeholders...")
    for lang in ("ru", "de"):
        phrases_dir = dst_root / f"tts/{lang}/phrases"
        if EXECUTE:
            ensure_dir(phrases_dir)
        for track_num in (1, 2):
            fname = f"{track_num:03d}.mp3"
            fpath = phrases_dir / fname
            if not fpath.exists():
                if EXECUTE:
                    create_silent_mp3(fpath)
                    print(f"  [OK] Created placeholder: {lang}/phrases/{fname}")
                else:
                    print(f"  [SCAN] Would create placeholder: {lang}/phrases/{fname}")

    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {total_copied}")
    print(f"Files skipped:   {total_skipped}")
    print(f"Errors:          {len(errors)}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")

    if not EXECUTE:
        print("\n[WARN] This was a DRY-RUN.")
        print("   Edit this script: set EXECUTE = True")
        print("   Then run: python migrate_sdcard_pc.py")

    print(f"\n[OK] New structure will be at: {dst_root}")
    print("""
Expected result on E:/:
E:/
+-- tts/
|   +-- ru/
|   |   +-- hours/           (000-023.mp3)
|   |   +-- minutes/         (000-059.mp3)
|   |   +-- days/            (001-031.mp3)
|   |   +-- months/          (001-012.mp3)
|   |   +-- years/           (003=2023...)
|   |   +-- weekdays/        (001-007.mp3)
|   |   +-- phrases/         (001,002,005,006,007,010,011.mp3)
|   |   +-- numbers_0_30/    (000-030.mp3)  -- extra
|   +-- de/
|   |   +-- hours/           (000-023.mp3)
|   |   +-- minutes/         (000-059.mp3)
|   |   +-- days/            (001-031.mp3)
|   |   +-- months/          (000-011.mp3)
|   |   +-- years/           (003=2023...)
|   |   +-- weekdays/        (001-007.mp3)
|   |   +-- phrases/         (001,002,005,006,007,010,011.mp3)
|   +-- ua/                  (empty, for future)
+-- music/
|   +-- track001.mp3 ... track045.mp3
+-- chimes/
|   +-- melody.mp3
|   +-- strike_01.mp3 ... strike_12.mp3
+-- beeps/
|   +-- beep_01.mp3
|   +-- beep_02.mp3
+-- 01/ ... 21/              (legacy folders, kept if KEEP_LEGACY=True)
+-- описание папок.txt
""")
    return len(errors) == 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate SD card from legacy to v2 structure")
    parser.add_argument("--execute", action="store_true", help="Actually copy files (not dry-run)")
    parser.add_argument("--no-keep-legacy", action="store_true", help="Don't keep legacy folders (not implemented)")
    parser.add_argument("--source", default=SOURCE_DRIVE, help="Source drive letter (default: E:)")
    parser.add_argument("--dest", default=DEST_DRIVE, help="Dest drive letter (default: E:)")
    args = parser.parse_args()

    # Override globals from args
    globals()["EXECUTE"] = args.execute
    globals()["SOURCE_DRIVE"] = args.source
    globals()["DEST_DRIVE"] = args.dest
    globals()["KEEP_LEGACY"] = not args.no_keep_legacy

    success = migrate()
    sys.exit(0 if success else 1)