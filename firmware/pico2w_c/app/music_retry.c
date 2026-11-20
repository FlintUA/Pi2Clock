#include "music_retry.h"
void music_retry_reset(music_retry_t *s) {s->failures=0;s->retry_at=0;}
bool music_retry_ready(const music_retry_t *s,uint64_t now) {return now>=s->retry_at;}
bool music_retry_failed(music_retry_t *s,unsigned tracks,bool repeat_one,uint64_t now) {
    ++s->failures;
    if(!tracks || s->failures>=tracks || repeat_one) {s->retry_at=0;return false;}
    s->retry_at=now+200u;return true;
}
