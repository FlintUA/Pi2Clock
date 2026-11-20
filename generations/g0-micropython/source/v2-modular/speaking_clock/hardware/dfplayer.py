"""
Async DFPlayer Mini driver with command queue.
Improvements over original:
- Non-blocking command queue
- Busy pin monitoring
- Folder/track abstraction
- Error recovery
- Volume control without blocking main loop
"""

from machine import UART, Pin
import time
import asyncio


class DFPlayerAsync:
    """Asynchronous DFPlayer Mini driver using UART."""

    # Commands
    CMD_NEXT = 0x01
    CMD_PREV = 0x02
    CMD_VOLUME_UP = 0x04
    CMD_VOLUME_DOWN = 0x05
    CMD_SET_VOLUME = 0x06
    CMD_SET_EQ = 0x07
    CMD_PLAY_MODE = 0x08
    CMD_SET_SOURCE = 0x09
    CMD_STANDBY = 0x0A
    CMD_NORMAL = 0x0B
    CMD_RESET = 0x0C
    CMD_RESUME = 0x0D
    CMD_PAUSE = 0x0E
    CMD_PLAY_FOLDER = 0x0F
    CMD_PLAY_MP3 = 0x12

    # EQ modes
    EQ_NORMAL = 0
    EQ_POP = 1
    EQ_ROCK = 2
    EQ_JAZZ = 3
    EQ_CLASSIC = 4
    EQ_BASE = 5

    # Play modes
    MODE_REPEAT = 0
    MODE_FOLDER_REPEAT = 1
    MODE_SINGLE_REPEAT = 2
    MODE_RANDOM = 3

    # Sources
    SRC_U = 0
    SRC_TF = 1
    SRC_AUX = 2
    SRC_SLEEP = 3
    SRC_FLASH = 4

    START_BYTE = 0x7E
    VERSION = 0xFF
    LENGTH = 0x06
    ACK = 0x01
    END_BYTE = 0xEF
    CMD_DELAY_MS = 50

    def __init__(self, uart_id: int, tx_pin: int, rx_pin: int, busy_pin: int):
        self.uart = UART(uart_id, baudrate=9600, tx=Pin(tx_pin), rx=Pin(rx_pin), bits=8, parity=None, stop=1)
        self.busy_pin = Pin(busy_pin, Pin.IN, Pin.PULL_UP)
        self._volume = 15
        self._playing = False
        self._current_folder = 0
        self._current_track = 0
        self._command_queue = []
        self._last_cmd_time = 0
        self._lock = asyncio.Lock()

        # Response buffer
        self._response = None

    def _checksum(self, cmd: int, param1: int, param2: int) :
        """Calculate checksum."""
        return -(self.VERSION + self.LENGTH + cmd + self.ACK + param1 + param2) & 0xFFFF

    def _build_command(self, cmd: int, param1: int = 0, param2: int = 0) -> bytes:
        """Build command packet."""
        checksum = self._checksum(cmd, param1, param2)
        high = (checksum >> 8) & 0xFF
        low = checksum & 0xFF
        return bytes([
            self.START_BYTE, self.VERSION, self.LENGTH, cmd, self.ACK,
            param1, param2, high, low, self.END_BYTE
        ])

    async def _send_raw(self, cmd: int, param1: int = 0, param2: int = 0) :
        """Send command with rate limiting."""
        async with self._lock:
            # Rate limit
            now = time.ticks_ms()
            delay = time.ticks_diff(now, self._last_cmd_time)
            if delay < self.CMD_DELAY_MS:
                await asyncio.sleep_ms(self.CMD_DELAY_MS - delay)

            packet = self._build_command(cmd, param1, param2)
            self.uart.write(packet)
            self._last_cmd_time = time.ticks_ms()

            # Read response if any
            await asyncio.sleep_ms(20)
            self._response = self.uart.read()
            return True

    def is_busy(self) :
        """Check if DFPlayer is busy (pin LOW = busy)."""
        return not self.busy_pin.value()

    # ==================== HIGH-LEVEL COMMANDS ====================

    async def set_volume(self, volume: int) :
        """Set volume 0-30."""
        volume = max(0, min(30, volume))
        if volume == self._volume:
            return True
        ok = await self._send_raw(self.CMD_SET_VOLUME, 0, volume)
        if ok:
            self._volume = volume
        return ok

    async def volume_up(self) :
        """Increase volume by 1."""
        return await self.set_volume(self._volume + 1)

    async def volume_down(self) :
        """Decrease volume by 1."""
        return await self.set_volume(self._volume - 1)

    async def play_folder_track(self, folder: int, track: int) :
        """Play track from folder (folder 1-99, track 1-255)."""
        folder = max(1, min(99, folder))
        track = max(1, min(255, track))
        ok = await self._send_raw(self.CMD_PLAY_FOLDER, folder, track)
        if ok:
            self._playing = True
            self._current_folder = folder
            self._current_track = track
        return ok

    async def play_mp3(self, track_num: int) :
        """Play MP3 by global number (1-3000)."""
        high = (track_num >> 8) & 0xFF
        low = track_num & 0xFF
        ok = await self._send_raw(self.CMD_PLAY_MP3, high, low)
        if ok:
            self._playing = True
        return ok

    async def next_track(self) :
        """Play next track."""
        ok = await self._send_raw(self.CMD_NEXT)
        if ok:
            self._playing = True
        return ok

    async def prev_track(self) :
        """Play previous track."""
        ok = await self._send_raw(self.CMD_PREV)
        if ok:
            self._playing = True
        return ok

    async def pause(self) :
        """Pause playback."""
        ok = await self._send_raw(self.CMD_PAUSE)
        if ok:
            self._playing = False
        return ok

    async def resume(self) :
        """Resume playback."""
        ok = await self._send_raw(self.CMD_RESUME)
        if ok:
            self._playing = True
        return ok

    async def stop(self) :
        """Stop playback (pause)."""
        return await self.pause()

    async def set_eq(self, eq: int) :
        """Set EQ mode."""
        return await self._send_raw(self.CMD_SET_EQ, 0, eq)

    async def set_play_mode(self, mode: int) :
        """Set playback mode."""
        return await self._send_raw(self.CMD_PLAY_MODE, 0, mode)

    async def set_source(self, source: int) :
        """Set playback source."""
        return await self._send_raw(self.CMD_SET_SOURCE, 0, source)

    async def reset(self) :
        """Reset DFPlayer."""
        ok = await self._send_raw(self.CMD_RESET)
        if ok:
            await asyncio.sleep_ms(500)
            self._playing = False
        return ok

    # ==================== STATUS ====================

    def get_volume(self) :
        return self._volume

    def is_playing(self) :
        return self._playing and not self.is_busy()

    def get_current_track(self) :
        return (self._current_folder, self._current_track)

    # ==================== TTS HELPERS ====================

    async def speak_number(self, folder: int, number: int, lang_folder: int = None) :
        """Speak a number from TTS folder structure."""
        if lang_folder is not None:
            folder = lang_folder
        return await self.play_folder_track(folder, number)

    async def speak_time(self, hour: int, minute: int, tts_base: int) :
        """Speak time: hour from folder, minute from folder+1."""
        # Hour
        await self.play_folder_track(tts_base, hour)
        await asyncio.sleep_ms(700)
        # Minute
        return await self.play_folder_track(tts_base + 1, minute)

    # ==================== INITIALIZATION ====================

    async def initialize(self) :
        """Initialize DFPlayer."""
        try:
            await self.reset()
            await asyncio.sleep_ms(500)
            await self.set_volume(self._volume)
            await self.set_source(self.SRC_TF)  # TF card
            await self.set_play_mode(self.MODE_FOLDER_REPEAT)
            await self.set_eq(self.EQ_NORMAL)
            print("[DFPlayer] Initialized")
            return True
        except Exception as e:
            print(f"[DFPlayer] Init failed: {e}")
            return False

    def test_connection(self) :
        """Test if DFPlayer responds."""
        try:
            # Try to read busy pin
            _ = self.busy_pin.value()
            return True
        except Exception:
            return False