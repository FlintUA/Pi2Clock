#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create missing phrase tracks in v2 TTS structure (tts/ru/phrases, tts/de/phrases)
by copying existing tracks as fallbacks.

Run ON PC with SD card in reader.
"""

import os
import sys
import shutil
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

SD_DRIVE = "/e"           # Your SD card mount point

# Set to True to actually copy files, False for dry-run
EXECUTE = True

# ============================================================
# FALLBACK MAPPING: target_track -> source_track
# If target_track doesn't exist, copy from source_track
# ============================================================

# v2 phrase tracks expected by locale/manager.py:
# 1=alarm, 2=timer_done, 3=chime_hour, 4=chime_half, 5=volume_on, 6=volume_off,
# 7=menu_enter, 8=menu_exit, 9=settings_saved, 10=timer_set, 11=timer_cancelled,
# 12=work_start, 13=short_break, 14=long_break

RU_FALLBACKS = {
    # Tracks that exist in tts/ru/phrases: 1,2,3,4,5,6,10,11,12,13
    # Missing: 7,8,9,14
    7: 5,     # menu_enter -> volume_on (5)
    8: 6,     # menu_exit -> volume_off (6)
    9: 10,    # settings_saved -> timer_set (10)
    14: 13,   # long_break -> short_break (13)
}

DE_FALLBACKS = {
    # Tracks that exist in tts/de/phrases: 1,2,3,4,5,6,10,11,12,13
    # Missing: 7,8,9,14
    7: 5,     # menu_enter -> volume_on (5)
    8: 6,     # menu_exit -> volume_off (6)
    9: 10,    # settings_saved -> timer_set (10)
    14: 13,   # long_break -> short_break (13)
}

# ============================================================

def create_fallbacks(phrases_folder: Path, fallbacks: dict, lang: str):
    """Create missing tracks by copying from fallbacks."""
    print(f"\n{'='*60}")
    print(f"Processing {lang.upper()} phrases folder: {phrases_folder}")
    print(f"{'='*60}")

    if not phrases_folder.exists():
        print(f"[ERR] Folder not found: {phrases_folder}")
        return 0, 0

    existing_files = {int(f.stem): f for f in phrases_folder.glob("*.mp3")}
    print(f"Existing tracks: {sorted(existing_files.keys())}")

    created = 0
    skipped = 0

    for target_track, source_track in sorted(fallbacks.items()):
        target_name = f"{target_track:03d}.mp3"
        target_path = phrases_folder / target_name

        if target_path.exists():
            print(f"  [SKIP] {target_name} already exists")
            skipped += 1
            continue

        if source_track not in existing_files:
            print(f"  [WARN] Source track {source_track:03d}.mp3 not found, skipping {target_name}")
            continue

        source_path = existing_files[source_track]

        if EXECUTE:
            try:
                shutil.copy2(source_path, target_path)
                size = target_path.stat().st_size
                print(f"  [OK] Created {target_name} <- copied from {source_track:03d}.mp3 ({size:,} bytes)")
                created += 1
                # Add to existing for chained fallbacks
                existing_files[target_track] = target_path
            except Exception as e:
                print(f"  [ERR] Failed to create {target_name}: {e}")
        else:
            print(f"  [DRY] Would create {target_name} <- copy from {source_track:03d}.mp3")
            created += 1

    return created, skipped


def main():
    print("=" * 60)
    print("Create Missing Phrase Tracks in v2 TTS Structure")
    print("=" * 60)
    print(f"SD Drive: {SD_DRIVE}")
    print(f"Mode: {'EXECUTE' if EXECUTE else 'DRY-RUN'}")
    print()

    sd_root = Path(SD_DRIVE)

    if not sd_root.exists():
        print(f"[ERR] SD drive not found: {SD_DRIVE}")
        return 1

    # RU phrases: tts/ru/phrases
    ru_folder = sd_root / "tts" / "ru" / "phrases"
    ru_created, ru_skipped = create_fallbacks(ru_folder, RU_FALLBACKS, "RU")

    # DE phrases: tts/de/phrases
    de_folder = sd_root / "tts" / "de" / "phrases"
    de_created, de_skipped = create_fallbacks(de_folder, DE_FALLBACKS, "DE")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"RU (tts/ru/phrases):  created={ru_created}, skipped={ru_skipped}")
    print(f"DE (tts/de/phrases):  created={de_created}, skipped={de_skipped}")
    print(f"Total:                created={ru_created + de_created}, skipped={ru_skipped + de_skipped}")

    if not EXECUTE:
        print("\n[WARN] This was a DRY-RUN.")
        print("   Edit this script: set EXECUTE = True")
        print("   Then run: python create_missing_phrases_v2.py")

    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create missing DFPlayer phrase tracks in v2 structure")
    parser.add_argument("--execute", action="store_true", help="Actually create files")
    parser.add_argument("--drive", default=SD_DRIVE, help="SD card drive letter (default: /e)")
    args = parser.parse_args()

    globals()["EXECUTE"] = args.execute
    globals()["SD_DRIVE"] = args.drive

    sys.exit(main())