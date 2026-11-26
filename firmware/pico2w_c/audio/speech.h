#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "queue.h"
#include "clock_datetime.h"

// Folder/track layout is identical to G0 source/v3/audio.py.
// Language selection is supplied by the caller from current settings.
typedef enum {
    SPEECH_RU = 0,
    SPEECH_DE = 1
} speech_language_t;

uint8_t speech_hours_folder(speech_language_t language);
uint8_t speech_minutes_folder(speech_language_t language);
uint8_t speech_phrases_folder(speech_language_t language);
const char *speech_language_name(speech_language_t language);
bool speech_enqueue_time(audio_queue_t *queue, speech_language_t language,
                         uint8_t hour, uint8_t minute, bool exact_hour_phrase);
// Year recordings cover 2023..2029; other years omit the year segment.
bool speech_enqueue_date(audio_queue_t *queue, speech_language_t language,
                         const ds1302_datetime_t *date);
void speech_enqueue_timer_start(audio_queue_t *queue, speech_language_t language,
                                uint32_t duration_seconds);
// German "Minuten" (folder 17).
#define SPEECH_DE_MINUTEN_TRACK 15u
// Time left on a running timer: nearest whole minute (at least one).
// RU: hours (01) + minutes (02). DE: number (12) + "Minuten", below one hour only
// (returns false without changing the queue when no recording fits).
bool speech_enqueue_timer_remaining(audio_queue_t *queue, speech_language_t language,
                                    uint32_t remaining_seconds);
void speech_enqueue_timer_cancel(audio_queue_t *queue, speech_language_t language);
void speech_enqueue_timer_finish(audio_queue_t *queue, speech_language_t language);

// Optional completion speech plus 0=signal 07/013, 1=music 08/NNN, 2=no extra sound.
bool speech_enqueue_timer_finish_sound(audio_queue_t *queue, speech_language_t language,
                                       bool voice, uint8_t sound, uint8_t track);
