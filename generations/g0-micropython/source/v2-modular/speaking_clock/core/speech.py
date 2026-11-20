"""
Speech queue with priorities for TTS playback.
Manages DFPlayer commands with priority levels.
"""

import asyncio
import speaking_clock.config as config


class SpeechPriority:
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class SpeechItem:
    def __init__(self, priority, coro, description, interruptible=True):
        self.priority = priority
        self.coro = coro
        self.description = description
        self.interruptible = interruptible


class SpeechQueue:
    """
    Priority queue for speech playback.
    Critical items interrupt current playback.
    Other items queue up.
    """

    def __init__(self, dfplayer, locale_manager):
        self.dfplayer = dfplayer
        self.locale = locale_manager
        self._queues = {
            SpeechPriority.CRITICAL: [],
            SpeechPriority.HIGH: [],
            SpeechPriority.NORMAL: [],
            SpeechPriority.LOW: [],
        }
        self._max_sizes = {
            SpeechPriority.CRITICAL: config.SPEECH_QUEUE_MAX_CRITICAL,
            SpeechPriority.HIGH: config.SPEECH_QUEUE_MAX_HIGH,
            SpeechPriority.NORMAL: config.SPEECH_QUEUE_MAX_NORMAL,
            SpeechPriority.LOW: config.SPEECH_QUEUE_MAX_LOW,
        }
        self._current_task = None
        self._current_priority = None
        self._processing = False
        self._volume_before_interrupt = None
        self._muted_for_quiet = False

    def set_quiet_mode(self, enabled):
        """Enable/disable quiet mode (suppresses non-critical)."""
        self._muted_for_quiet = enabled

    def is_quiet_mode(self):
        return self._muted_for_quiet

    def enqueue(self, priority, coro, description="", interruptible=True):
        """Add speech item to queue. Returns True if queued."""
        if priority != SpeechPriority.CRITICAL and self._muted_for_quiet:
            return False

        queue = self._queues[priority]
        if len(queue) >= self._max_sizes[priority]:
            return False

        queue.append(SpeechItem(priority, coro, description, interruptible))
        return True

    def enqueue_critical(self, coro, description=""):
        return self.enqueue(SpeechPriority.CRITICAL, coro, description, interruptible=False)

    def enqueue_high(self, coro, description=""):
        return self.enqueue(SpeechPriority.HIGH, coro, description)

    def enqueue_normal(self, coro, description=""):
        return self.enqueue(SpeechPriority.NORMAL, coro, description)

    def enqueue_low(self, coro, description=""):
        return self.enqueue(SpeechPriority.LOW, coro, description)

    def clear_queue(self, priority=None):
        """Clear specific queue or all queues."""
        if priority:
            self._queues[priority].clear()
        else:
            for q in self._queues.values():
                q.clear()

    def stop_current(self):
        """Stop currently playing speech (for critical interrupt)."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
        try:
            asyncio.create_task(self.dfplayer.stop())
        except Exception:
            pass

    async def process(self):
        """Process queues - call periodically from main loop."""
        if self._processing:
            return

        if self._queues[SpeechPriority.CRITICAL]:
            if self._current_priority != SpeechPriority.CRITICAL:
                self.stop_current()

        for priority in (SpeechPriority.CRITICAL, SpeechPriority.HIGH, SpeechPriority.NORMAL, SpeechPriority.LOW):
            if self._queues[priority]:
                item = self._queues[priority].pop(0)
                await self._play_item(item, priority)
                return

    async def _play_item(self, item, priority):
        """Play a single speech item."""
        self._processing = True
        self._current_priority = priority

        try:
            if priority == SpeechPriority.CRITICAL:
                self._volume_before_interrupt = self.dfplayer.get_volume()
                await self.dfplayer.set_volume(max(15, self._volume_before_interrupt))

            success = await item.coro()

            if priority == SpeechPriority.CRITICAL and self._volume_before_interrupt is not None:
                await self.dfplayer.set_volume(self._volume_before_interrupt)
                self._volume_before_interrupt = None

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Speech] Error playing {item.description}: {e}")
        finally:
            self._processing = False
            self._current_priority = None

    async def speak_time(self, hour, minute, lang=None):
        """Speak time in current or specified language."""
        lang = lang or self.locale.current_lang
        tts_base = self.locale.get_tts_base(lang)
        return await self.dfplayer.speak_time(hour, minute, tts_base)

    async def speak_date(self, lang=None):
        """Speak full date."""
        return True

    async def speak_phrase(self, phrase_key, lang=None, **kwargs):
        """Speak a predefined phrase using new locale API."""
        lang = lang or self.locale.current_lang
        sequence = self.locale.get_phrase_sequence(phrase_key, lang)
        for folder, track in sequence:
            success = await self.dfplayer.play_folder_track(folder, track)
            if not success:
                return False
        return True

    async def play_chime(self, hour, lang=None):
        """Play hourly chime sequence."""
        lang = lang or self.locale.current_lang
        sequence = self.locale.get_chime_sequence(hour, lang)
        for folder, track in sequence:
            success = await self.dfplayer.play_folder_track(folder, track)
            if not success:
                return False
        return True

    async def play_beep(self, count=1, lang=None):
        """Play beep sequence."""
        lang = lang or self.locale.current_lang
        sequence = self.locale.get_beep_sequence(count, lang)
        for folder, track in sequence:
            success = await self.dfplayer.play_folder_track(folder, track)
            if not success:
                return False
        return True

    def get_queue_status(self):
        """Get queue status for debugging."""
        return {p.name if hasattr(p, 'name') else str(p): len(q) for p, q in self._queues.items()}