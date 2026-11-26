#include <assert.h>
#include <stddef.h>
#include "speech.h"
#include "dfplayer.h"

bool dfplayer_busy(void) { return false; }
bool dfplayer_command_ready(uint64_t now) { (void)now; return true; }
void dfplayer_pause(uint64_t now) { (void)now; }
void dfplayer_resume(uint64_t now) { (void)now; }
void dfplayer_set_volume(uint8_t v,uint64_t now) { (void)v; (void)now; }
void dfplayer_play_folder_track(uint8_t f,uint8_t t,uint64_t now) {
    (void)f; (void)t; (void)now;
}

int main(void) {
    ds1302_datetime_t date={.year=2026,.month=11,.day=8,.weekday=1};
    for (unsigned lang=0;lang<2;++lang) {
        audio_queue_t q={0};
        unsigned offset=lang?10:0;
        assert(speech_enqueue_date(&q,(speech_language_t)lang,&date));
        assert(q.size==4);
        assert(q.items[0].folder==6+offset && q.items[0].track==7); // Actual Sunday, not stale RTC weekday.
        assert(q.items[1].folder==3+offset && q.items[1].track==8);
        assert(q.items[2].folder==4+offset && q.items[2].track==11);
        assert(q.items[3].folder==5+offset && q.items[3].track==6);
        assert(speech_enqueue_time(&q,(speech_language_t)lang,8,33,false));
        assert(q.size==6 && q.items[4].folder==1+offset && q.items[4].track==8);
        assert(q.items[5].folder==2+offset && q.items[5].track==33);
    }
    audio_queue_t q={0};
    date.year=2030;
    assert(speech_enqueue_date(&q,SPEECH_RU,&date) && q.size==3);
    date.year=2022;
    audio_queue_init(&q);
    assert(speech_enqueue_date(&q,SPEECH_DE,&date) && q.size==3);
    date.year=2024; date.month=2; date.day=29;
    audio_queue_init(&q);
    assert(speech_enqueue_date(&q,SPEECH_DE,&date));
    date.year=2023;
    unsigned size=q.size;
    assert(!speech_enqueue_date(&q,SPEECH_RU,&date) && q.size==size);
    assert(!speech_enqueue_date(&q,SPEECH_RU,0));
    assert(!speech_enqueue_date(0,SPEECH_RU,&date));
    date.year=2026; date.month=11; date.day=8;
    audio_queue_init(&q);
    for(unsigned i=0;i<13;++i) assert(audio_queue_enqueue(&q,1,1));
    assert(!speech_enqueue_date(&q,SPEECH_RU,&date) && q.size==13);
    // Planner appends correctly through a ring wrap without partial additions.
    audio_queue_init(&q);
    q.head=15;
    assert(speech_enqueue_date(&q,SPEECH_RU,&date));
    assert(q.items[15].track==7 && q.items[0].track==8 && q.items[2].track==6);
    for (unsigned lang=0;lang<2;++lang) {
        for (unsigned voice=0;voice<2;++voice) for (unsigned sound=0;sound<3;++sound) {
            audio_queue_init(&q);q.head=15;
            assert(speech_enqueue_timer_finish_sound(&q,(speech_language_t)lang,voice!=0,(uint8_t)sound,255));
            unsigned message=voice && !lang ? 1u:0u;
            assert(q.size==message+(sound!=2));
            if(message) assert(q.items[15].folder==7 && q.items[15].track==11);
            if(sound!=2) {
                audio_track_t t=q.items[(15+message)%AUDIO_QUEUE_CAPACITY];
                assert(t.folder==(sound==1?8:7) && t.track==(sound==1?255:13));
            }
        }
        audio_queue_init(&q);
        speech_enqueue_timer_finish(&q,(speech_language_t)lang);
        assert(q.size==(lang?1:2)); // Legacy defaults unchanged.
    }
    audio_queue_init(&q);q.size=15;
    assert(!speech_enqueue_timer_finish_sound(&q,SPEECH_RU,true,1,1) && q.size==15);
    assert(!speech_enqueue_timer_finish_sound(&q,SPEECH_RU,false,3,1) && q.size==15);
    assert(!speech_enqueue_timer_finish_sound(&q,SPEECH_RU,false,1,0) && q.size==15);
    assert(!speech_enqueue_timer_finish_sound(NULL,SPEECH_RU,true,0,1));
    // Timer remaining: nearest whole minute, at least one, from existing recordings only.
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_RU,5*60+29) && q.size==1);
    assert(q.items[0].folder==2 && q.items[0].track==5);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_RU,5*60+30) && q.size==1 && q.items[0].track==6);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_RU,12) && q.size==1 && q.items[0].track==1);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_RU,2*3600+15*60) && q.size==2);
    assert(q.items[0].folder==1 && q.items[0].track==2 && q.items[1].folder==2 && q.items[1].track==15);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_RU,3*3600+10) && q.size==1 && q.items[0].folder==1 && q.items[0].track==3);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_RU,86399) && q.size==2 && q.items[0].track==23 && q.items[1].track==59);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_DE,42*60+10) && q.size==2);
    assert(q.items[0].folder==12 && q.items[0].track==42 && q.items[1].folder==17 && q.items[1].track==15);
    audio_queue_init(&q);
    assert(speech_enqueue_timer_remaining(&q,SPEECH_DE,3599) && q.items[0].track==59);
    audio_queue_init(&q);
    assert(!speech_enqueue_timer_remaining(&q,SPEECH_DE,3600) && q.size==0);
    assert(!speech_enqueue_timer_remaining(&q,SPEECH_RU,0) && q.size==0);
    assert(!speech_enqueue_timer_remaining(NULL,SPEECH_RU,60));
    q.size=16;
    assert(!speech_enqueue_timer_remaining(&q,SPEECH_RU,60) && q.size==16);
    // DE timer start uses the existing "Minuten" file 17/015.
    audio_queue_init(&q);
    speech_enqueue_timer_start(&q,SPEECH_DE,10*60);
    assert(q.size==3 && q.items[1].folder==12 && q.items[1].track==10 && q.items[2].folder==17 && q.items[2].track==15);
    return 0;
}
