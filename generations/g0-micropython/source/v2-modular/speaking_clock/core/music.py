"""
Music player: playlist management, shuffle, folder playback.
"""

import os
import random
import asyncio


class Track:
    def __init__(self, path, folder, name, size=0):
        self.path = path
        self.folder = folder
        self.name = name
        self.size = size


class MusicPlayer:
    """Manages music playback from SD card."""

    def __init__(self, dfplayer, speech_queue):
        self.dfplayer = dfplayer
        self.speech = speech_queue
        self.tracks = []
        self.folders = []
        self._current_index = 0
        self._shuffled = False
        self._playing = False
        self._paused = False
        self._mode = "shuffle"  # "shuffle", "sequential", "folder"
        self._current_folder = ""
        self._scan_done = False

    async def initialize(self, music_root="/sd/music"):
        """Scan SD card for music files."""
        self._scan_done = False
        try:
            await self._scan_music(music_root)
            self._shuffle()
            print(f"[Music] Found {len(self.tracks)} tracks in {len(self.folders)} folders")
        except Exception as e:
            print(f"[Music] Scan failed: {e}")
        self._scan_done = True

    async def _scan_music(self, root):
        """Recursively scan for MP3 files."""
        self.tracks = []
        self.folders = []

        try:
            entries = os.ilistdir(root)
        except Exception:
            return

        for entry in entries:
            name = entry[0]
            path = f"{root}/{name}"
            if entry[1] == 0x4000:  # Directory
                self.folders.append(name)
                await self._scan_music(path)
            elif name.lower().endswith(".mp3"):
                try:
                    stat = os.stat(path)
                    size = stat[6]
                except Exception:
                    size = 0
                self.tracks.append(Track(path=path, folder=root, name=name, size=size))

    def _shuffle(self):
        """Shuffle playlist using Fisher-Yates."""
        # MicroPython may not have random.shuffle, implement our own
        n = len(self.tracks)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            self.tracks[i], self.tracks[j] = self.tracks[j], self.tracks[i]
        self._current_index = 0
        self._shuffled = True

    def play(self):
        """Start/resume playback."""
        if not self.tracks:
            return False

        if self._paused:
            return asyncio.create_task(self.dfplayer.resume())

        track = self.tracks[self._current_index]
        # For DFPlayer, we need folder/track numbers
        # This is a simplified version - real implementation needs folder mapping
        self._playing = True
        self._paused = False
        return True

    def pause(self):
        """Pause playback."""
        if self._playing and not self._paused:
            self._paused = True
            asyncio.create_task(self.dfplayer.pause())

    def stop(self):
        """Stop playback."""
        self._playing = False
        self._paused = False
        asyncio.create_task(self.dfplayer.stop())

    def next_track(self):
        """Play next track."""
        if not self.tracks:
            return
        self._current_index = (self._current_index + 1) % len(self.tracks)
        self._playing = True
        self._paused = False
        # Play next
        asyncio.create_task(self.dfplayer.next_track())

    def prev_track(self):
        """Play previous track."""
        if not self.tracks:
            return
        self._current_index = (self._current_index - 1) % len(self.tracks)
        self._playing = True
        self._paused = False
        asyncio.create_task(self.dfplayer.prev_track())

    def shuffle(self):
        """Reshuffle playlist."""
        self._shuffle()

    def set_mode(self, mode):
        """Set playback mode: shuffle, sequential, folder."""
        if mode in ("shuffle", "sequential", "folder"):
            self._mode = mode
            if mode == "shuffle":
                self._shuffle()

    def get_current_track(self):
        if 0 <= self._current_index < len(self.tracks):
            return self.tracks[self._current_index]
        return None

    def get_playlist_info(self):
        return {
            "total": len(self.tracks),
            "current": self._current_index + 1 if self.tracks else 0,
            "mode": self._mode,
            "playing": self._playing,
            "paused": self._paused,
            "current_track": self.get_current_track().name if self.get_current_track() else None,
        }

    def is_playing(self):
        return self._playing and not self._paused

    def is_scanned(self):
        return self._scan_done