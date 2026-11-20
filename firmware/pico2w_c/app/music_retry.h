#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef struct {unsigned failures;uint64_t retry_at;} music_retry_t;
void music_retry_reset(music_retry_t *state);
bool music_retry_ready(const music_retry_t *state,uint64_t now);
// Bound consecutive failures by the list size; single-track requests stop on their bad file.
bool music_retry_failed(music_retry_t *state,unsigned tracks,bool single_track,uint64_t now);
