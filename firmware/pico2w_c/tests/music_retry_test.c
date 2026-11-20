#include "music_retry.h"
#include <assert.h>
int main(void) {
    music_retry_t s={0};
    assert(music_retry_ready(&s,0));
    for(unsigned i=0;i<77;i++) {
        uint64_t now=1000u+i*200u;
        assert(music_retry_failed(&s,78,false,now));
        assert(!music_retry_ready(&s,now+199) && music_retry_ready(&s,now+200));
    }
    assert(!music_retry_failed(&s,78,false,16400));
    music_retry_reset(&s);assert(s.failures==0 && music_retry_ready(&s,0));
    assert(!music_retry_failed(&s,78,true,0));
    music_retry_reset(&s);assert(!music_retry_failed(&s,1,false,0));
    music_retry_reset(&s);assert(!music_retry_failed(&s,0,false,0));
    music_retry_reset(&s);assert(music_retry_failed(&s,78,false,100));
    music_retry_reset(&s);assert(music_retry_failed(&s,78,false,100));
    assert(s.failures==1); // A successful file or explicit stop resets the pass.
    return 0;
}
