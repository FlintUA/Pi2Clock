#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create missing phrase tracks in DFPlayer folders (07 for RU, 17 for DE)
by copying existing tracks as fallbacks.

Run ON PC with SD card in reader.
Source/Dest: E:/07/ and E:/17/ (DFPlayer folders at SD root)
"""

import os
import sys
import shutil
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

SD_DRIVE = "E:"           # Your SD card drive letter

# Set to True to actually copy files, False for dry-run
EXECUTE = False           # CHANGE TO True TO ACTUALLY CREATE FILES

# ============================================================
# FALLBACK MAPPING: target_track -> source_track
# If target_track doesn't exist, copy from source_track
# ============================================================

# RU phrases folder (07) - existing tracks: 007, 008, 009, 014
RU_FALLBACKS = {
    # v2 track -> legacy track to copy from
    1: 7,     # alarm -> timer_set (007.mp3)
    2: 7,     # timer_done -> timer_set
    3: 7,     # chime_hour -> timer_set
    4: 7,     # chime_half -> timer_set
    5: 8,     # menu_enter -> volume_on (008.mp3)
    6: 9,     # menu_exit -> volume_off (009.mp3)
    7: 7,     # settings_saved -> timer_set (already exists as 007)
    10: 7,    # timer_set -> already 007 (will be renamed to 010 by migration, but here we ensure 010 exists)
    11: 14,   # timer_cancelled -> already 014
    12: 7,    # work_start -> timer_set
    13: 7,    # short_break -> timer_set
    14: 14,   # long_break -> timer_cancelled
}

# DE phrases folder (17) - existing tracks: 007, 008, 009, 014, 015
DE_FALLBACKS = {
    1: 7,     # alarm -> timer_set
    2: 7,     # timer_done -> timer_set
    3: 7,     # chime_hour -> timer_set
    4: 7,     # chime_half -> timer_set
    5: 8,     # menu_enter -> volume_on
    6: 9,     # menu_exit -> volume_off
    7: 7,     # settings_saved -> timer_set
    10: 7,    # timer_set
    11: 14,   # timer_cancelled
    12: 7,    # work_start
    13: 7,    # short_break
    14: 15,   # long_break -> minuten (015.mp3)
    15: 15,   # minuten (already exists)
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
    print("Create Missing Phrase Tracks for DFPlayer")
    print("=" * 60)
    print(f"SD Drive: {SD_DRIVE}")
    print(f"Mode: {'EXECUTE' if EXECUTE else 'DRY-RUN'}")
    print()

    sd_root = Path(SD_DRIVE)

    if not sd_root.exists():
        print(f"[ERR] SD drive not found: {SD_DRIVE}")
        return 1

    # RU phrases: folder 07
    ru_folder = sd_root / "07"
    ru_created, ru_skipped = create_fallbacks(ru_folder, RU_FALLBACKS, "RU")

    # DE phrases: folder 17
    de_folder = sd_root / "17"
    de_created, de_skipped = create_fallbacks(de_folder, DE_FALLBACKS, "DE")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"RU (folder 07):  created={ru_created}, skipped={ru_skipped}")
    print(f"DE (folder 17):  created={de_created}, skipped={de_skipped}")
    print(f"Total:           created={ru_created + de_created}, skipped={ru_skipped + de_skipped}")

    if not EXECUTE:
        print("\n[WARN] This was a DRY-RUN.")
        print("   Edit this script: set EXECUTE = True")
        print("   Then run: python create_missing_phrases.py")

    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create missing DFPlayer phrase tracks")
    parser.add_argument("--execute", action="store_true", help="Actually create files")
    parser.add_argument("--drive", default=SD_DRIVE, help="SD card drive letter (default: E:)")
    args = parser.parse_args()

    globals()["EXECUTE"] = args.execute
    globals()["SD_DRIVE"] = args.drive

    sys.exit(main())