#include "speech.h"
#include "clock_time.h"

bool speech_enqueue_date(audio_queue_t *queue, speech_language_t language,
                         const ds1302_datetime_t *date) {
    uint64_t wall;
    ds1302_datetime_t normalized;
    if (!queue || !clock_datetime_to_utc(date,&wall) ||
        !clock_utc_to_datetime(wall,&normalized)) return false;
    unsigned count=date->year>=2023 && date->year<=2029 ? 4u : 3u;
    if (queue->size+count>AUDIO_QUEUE_CAPACITY) return false;
    uint8_t offset=language==SPEECH_DE?10u:0u;
    audio_queue_enqueue(queue,(uint8_t)(6u+offset),normalized.weekday);
    audio_queue_enqueue(queue,(uint8_t)(3u+offset),date->day);
    audio_queue_enqueue(queue,(uint8_t)(4u+offset),date->month);
    if (count==4u) audio_queue_enqueue(queue,(uint8_t)(5u+offset),(uint8_t)(date->year%10));
    return true;
}

// Confirmed language mappings from G0 source/v3/audio.py:
// RU hours 01, minutes 02, service phrases 07
// DE hours 11, minutes 12, service phrases 17
uint8_t speech_hours_folder(speech_language_t language) {
    return language == SPEECH_DE ? 11u : 1u;
}

uint8_t speech_minutes_folder(speech_language_t language) {
    return language == SPEECH_DE ? 12u : 2u;
}

uint8_t speech_phrases_folder(speech_language_t language) {
    return language == SPEECH_DE ? 17u : 7u;
}

const char *speech_language_name(speech_language_t language) {
    return language == SPEECH_DE ? "de" : "ru";
}

bool speech_enqueue_time(audio_queue_t *queue, speech_language_t language,
                         uint8_t hour, uint8_t minute, bool exact_hour_phrase) {
    if (hour > 23u || minute > 59u) return false;
    if (queue->size + 2u > AUDIO_QUEUE_CAPACITY) return false;

    // Same conditional minute handling as enqueue_clock_time in main.py.
    // Hour track 000 at midnight follows original MicroPython mapping.
    if (!audio_queue_enqueue(queue, speech_hours_folder(language), hour)) return false;
    if (minute > 0u || exact_hour_phrase) {
        if (!audio_queue_enqueue(queue, speech_minutes_folder(language), minute)) return false;
    }
    return true;
}

void speech_enqueue_timer_start(audio_queue_t *queue, speech_language_t language,
                                uint32_t duration_seconds) {
    audio_queue_enqueue(queue, speech_phrases_folder(language), 7u);
    if (duration_seconds % 60u) return; // MicroPython skips non-whole minutes.
    uint32_t hours = duration_seconds / 3600u;
    uint32_t minutes = (duration_seconds / 60u) % 60u;
    if (language == SPEECH_RU) {
        if (hours > 0u && hours <= 23u) {
            audio_queue_enqueue(queue, speech_hours_folder(language), (uint8_t)hours);
        }
        if (minutes > 0u) {
            audio_queue_enqueue(queue, speech_minutes_folder(language), (uint8_t)minutes);
        }
    } else if (hours == 0u && minutes > 0u) {
        // German timer duration: <number> + 'Minuten' (17/017, see speech.h).
        audio_queue_enqueue(queue, speech_minutes_folder(language), (uint8_t)minutes);
        audio_queue_enqueue(queue, speech_phrases_folder(language), SPEECH_DE_MINUTEN_TRACK);
    }
}

bool speech_enqueue_timer_remaining(audio_queue_t *queue, speech_language_t language,
                                    uint32_t remaining_seconds) {
    if (!queue || !remaining_seconds) return false;
    // Nearest whole minute, never zero; there are no second or "remaining" recordings.
    uint32_t total = (remaining_seconds + 30u) / 60u;
    if (!total) total = 1u;
    if (total > 23u * 60u + 59u) total = 23u * 60u + 59u;
    if (language == SPEECH_DE) {
        // Folder 11 holds clock hours ("N Uhr"), not durations: below one hour only.
        if (remaining_seconds < 3600u && total > 59u) total = 59u;
        if (total > 59u || queue->size + 2u > AUDIO_QUEUE_CAPACITY) return false;
        audio_queue_enqueue(queue, speech_minutes_folder(language), (uint8_t)total);
        audio_queue_enqueue(queue, speech_phrases_folder(language), SPEECH_DE_MINUTEN_TRACK);
        return true;
    }
    uint32_t hours = total / 60u, minutes = total % 60u;
    unsigned needed = (hours ? 1u : 0u) + (minutes ? 1u : 0u);
    if (queue->size + needed > AUDIO_QUEUE_CAPACITY) return false;
    // RU folder 01 = "N часов", folder 02 = "N минут" with grammatical forms.
    if (hours) audio_queue_enqueue(queue, speech_hours_folder(language), (uint8_t)hours);
    if (minutes) audio_queue_enqueue(queue, speech_minutes_folder(language), (uint8_t)minutes);
    return true;
}

void speech_enqueue_timer_cancel(audio_queue_t *queue, speech_language_t language) {
    audio_queue_enqueue(queue, speech_phrases_folder(language), 14u);
}

bool speech_enqueue_timer_finish_sound(audio_queue_t *queue, speech_language_t language,
                                       bool voice, uint8_t sound, uint8_t track) {
    bool message = voice && language != SPEECH_DE;
    unsigned needed = (message ? 1u : 0u) + (sound != 2u ? 1u : 0u);
    if (!queue || sound > 2u || !track || queue->size + needed > AUDIO_QUEUE_CAPACITY) return false;
    // The DE completion phrase is absent on the current card; do not request
    // missing files or substitute Russian speech. Selected signal/music remains.
    if (message) audio_queue_enqueue(queue, speech_phrases_folder(language), 11u);
    if (sound == 2u) return true;
    return audio_queue_enqueue(queue, sound == 1u ? 8u : 7u, sound == 1u ? track : 13u);
}

void speech_enqueue_timer_finish(audio_queue_t *queue, speech_language_t language) {
    (void)speech_enqueue_timer_finish_sound(queue, language, true, 0u, 1u);
}
