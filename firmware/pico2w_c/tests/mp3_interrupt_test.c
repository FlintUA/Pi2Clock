#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "pcm_ring.h"
#include "helix_mp3.h"
static bool fail_checkpoint_alloc;
static void *checkpoint_malloc(size_t n) {return fail_checkpoint_alloc?NULL:malloc(n);}
// Exercise the production checkpoint/decoder driver with deterministic PCM,
// including resampling and a distinct notification decoder/file cursor.
#define malloc checkpoint_malloc
#define CLOCK_ENABLE_MP3 1
#include "../audio/mp3_probe.c"
#undef malloc

static uint32_t file_position,file_tag;
static bool fail_open;
static unsigned decoders;
typedef struct {uint32_t frame,tag;} fake_decoder_t;
uint64_t time_us_64(void) {static uint64_t n;return ++n;}
bool sd_fat32_stream_active(void) {return false;}
bool sd_fat32_open_read(const char *p) {
    if(fail_open)return false;
    file_position=0;file_tag=strstr(p,"M48")?48u:strstr(p,"M44")?44u:1u;return true;
}
void sd_fat32_close_read(void) {file_position=0;}
uint32_t sd_fat32_tell(void) {return file_position;}
bool sd_fat32_seek(uint32_t n) {file_position=n;return true;}
size_t sd_fat32_read(void *p,size_t n) {memset(p,(int)file_tag,n);file_position+=(uint32_t)n;return n;}
int helix_mp3_init(helix_mp3_t *d,const helix_mp3_io_t *i) {
    fake_decoder_t *f=calloc(1,sizeof(*f));assert(f);f->tag=file_tag;
    d->dec=f;d->io=i;d->rate=file_tag==48?48000u:44100u;uint8_t h[128];
    assert(i->read(i->user_data,h,sizeof(h))==sizeof(h));++decoders;return 0;
}
int helix_mp3_deinit(helix_mp3_t *d) {assert(decoders);--decoders;free(d->dec);return 0;}
uint32_t helix_mp3_get_sample_rate(helix_mp3_t *d) {return d->rate;}
uint32_t helix_mp3_get_bitrate(helix_mp3_t *d) {(void)d;return 192000;}
size_t helix_mp3_read_pcm_frames_s16(helix_mp3_t *d,int16_t *out,size_t count) {
    fake_decoder_t *f=d->dec;
    assert(file_tag==f->tag && file_position==128u+f->frame);
    uint32_t total=f->tag==1?700u:40000u;
    if(count>total-f->frame)count=total-f->frame;
    uint8_t buffer[256];assert(count<=sizeof(buffer));
    assert(d->io->read(d->io->user_data,buffer,count)==count);
    for(size_t j=0;j<count;j++,f->frame++) {
        out[2*j]=(int16_t)((f->frame*31u)%24000u);
        out[2*j+1]=(int16_t)(-out[2*j]);
    }
    return count;
}
static void read_frames(int16_t *out,uint32_t n) {
    uint32_t got=0;
    for(unsigned spin=0;got<n && spin<200000;spin++) {
        mp3_probe_service();
        if(clock_pcm_ring_active()) {
            uint32_t take=n-got;if(take>128)take=128;
            got+=clock_pcm_ring_pop(out+2u*got,take);
        }
    }
    assert(got==n);
}
static void notification(void) {
    assert(mp3_play_start("07/001.mp3",44100));
    int16_t out[256];
    for(unsigned spin=0;mp3_play_active() && spin<10000;spin++) {
        mp3_probe_service();if(clock_pcm_ring_active())clock_pcm_ring_pop(out,128);
    }
    assert(!mp3_play_active());
}
int main(void) {
    static int16_t expected[20000*2],actual[20000*2];
    for(unsigned rate=0;rate<2;rate++) {
        const char *path=rate?"08/M48.mp3":"08/M44.mp3";
        assert(mp3_play_start(path,44100));read_frames(expected,20000);mp3_play_stop();assert(!decoders);
        assert(mp3_play_start(path,44100));read_frames(actual,5000);
        uint32_t before=clock_pcm_ring_consumed();
        fail_checkpoint_alloc=true;assert(!mp3_play_suspend());fail_checkpoint_alloc=false;
        assert(mp3_play_active() && clock_pcm_ring_consumed()==before);
        assert(mp3_play_suspend() && !mp3_play_active() && decoders==1);
        assert(!mp3_play_suspend());notification();assert(mp3_play_suspended());
        assert(mp3_play_restore(false) && clock_pcm_ring_consumed()==before && !mp3_play_suspended());
        read_frames(actual+10000,15000);
        assert(!memcmp(expected,actual,sizeof(expected)));
        mp3_play_stop();assert(!decoders);
        assert(mp3_play_start(path,44100));read_frames(actual,5000);assert(mp3_play_pause());
        assert(mp3_play_suspend());notification();assert(mp3_play_restore(false));
        assert(clock_pcm_ring_paused());assert(mp3_play_resume());mp3_play_stop();
        assert(mp3_play_start(path,44100));read_frames(actual,5000);assert(mp3_play_suspend());
        notification();assert(mp3_play_restore(true));assert(clock_pcm_ring_paused());
        assert(mp3_play_resume());mp3_play_stop();
        assert(mp3_play_start(path,44100));read_frames(actual,5000);assert(mp3_play_suspend());
        notification();fail_open=true;assert(!mp3_play_restore(false));fail_open=false;
        assert(!mp3_play_suspended() && !decoders);
        assert(mp3_play_start(path,44100));read_frames(actual,5000);assert(mp3_play_suspend());
        assert(mp3_play_start("07/001.mp3",44100) && decoders==2);
        mp3_play_discard_suspended();assert(!mp3_play_restore(false) && decoders==1 && mp3_play_active());
        mp3_play_stop();assert(!decoders);
    }
    // EOF may already have closed the music decoder while queued PCM remains.
    assert(mp3_play_start("08/TAIL.mp3",44100));
    for(unsigned spin=0;!clock_pcm_ring_eof() && spin<1000;spin++)mp3_probe_service();
    assert(clock_pcm_ring_eof() && !decoders && mp3_play_active());
    uint32_t tail=clock_pcm_ring_available();assert(tail>0 && mp3_play_suspend());
    notification();assert(mp3_play_restore(false) && clock_pcm_ring_available()==tail);
    while(mp3_play_active()) {
        mp3_probe_service();if(clock_pcm_ring_active())clock_pcm_ring_pop(actual,128);
    }
    assert(!decoders && !mp3_play_suspended());
    puts("MP3 interruptions: sample-exact 44.1/48 kHz resume, paused state, allocation/read failure and discard passed");
    return 0;
}
