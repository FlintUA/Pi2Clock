#include "ota_upload.h"
#include "ota_image.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t flash[0x400000],payload[8707],header[128];
static clock_ota_layout_t layout;
static unsigned erases,programs,reboots;
static bool erase_ok=true,program_ok=true,validate_ok=true,reboot_ok=true;
static bool erase(uint32_t offset) {
    assert(clock_ota_inactive_range(&layout,offset,4096));assert(!(offset%4096));++erases;
    if(!erase_ok)return false;memset(flash+offset,255,4096);return true;
}
static bool program(uint32_t offset,const uint8_t *data) {
    assert(clock_ota_inactive_range(&layout,offset,4096));++programs;
    if(!program_ok)return false;
    for(unsigned i=0;i<4096;i++)assert(flash[offset+i]==255);
    memcpy(flash+offset,data,4096);return true;
}
static bool validate(uint32_t offset,uint32_t size,const uint8_t *first,const uint8_t *h) {
    assert(size==sizeof(payload) && !memcmp(header,h,128));
    assert(!memcmp(first,payload,4096));assert(!memcmp(flash+offset+4096,payload+4096,size-4096));
    for(unsigned i=0;i<4096;i++)assert(flash[offset+i]==255);
    return validate_ok;
}
static bool reboot(void) {++reboots;return reboot_ok;}
static void put32(uint8_t *p,uint32_t x) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(x>>(i*8));}
static void prepare(unsigned active) {
    layout=(clock_ota_layout_t){{0x1000,0x181000},{0x181000,0x301000},2,(int)active,active?0x181000:0x1000,true};
    memset(flash,0xa5,sizeof(flash));memset(header,0,sizeof(header));memcpy(header,"CLOCKOT1",8);
    put32(header+8,0x23500002);put32(header+12,sizeof(payload));put32(header+16,5);put32(header+20,1);
    memcpy(header+56,"g1-test-ota5-trial",18);
    for(unsigned i=0;i<sizeof(payload);i++)payload[i]=(uint8_t)(i*19);
    erases=programs=reboots=0;erase_ok=program_ok=validate_ok=reboot_ok=true;
}
static ota_upload_ops_t ops={erase,program,validate,reboot};
static void fill(ota_upload_t *u) {
    for(uint32_t offset=0;offset<sizeof(payload);offset+=512) {
        size_t n=sizeof(payload)-offset;if(n>512)n=512;
        assert(ota_upload_chunk(u,123,offset,payload+offset,n,10+offset));
    }
}
static void block_test(void) {
    uint8_t b[100]={0};uint32_t next;
    put32(b,0xffffded3);put32(b+4,0x90210142);put32(b+8,0x248);put32(b+12,0x10005);
    put32(b+16,0x3ff);put32(b+20,100);put32(b+24,0xab123579);
    assert(ota_image_block(b,28,5,&next) && next==100);
    assert(!ota_image_block(b,27,5,&next));assert(!ota_image_block(b,28,4,&next));
    put32(b+4,0x10210142);assert(!ota_image_block(b,28,5,&next)); // Non-trial rejected.
    put32(b+4,0x91210142);assert(!ota_image_block(b,28,5,&next)); // Wrong CPU rejected.
    put32(b+4,0x90210142);put32(b+16,0x4ff);assert(!ota_image_block(b,28,5,&next));
    put32(b+16,0x3ff);put32(b+24,0);assert(!ota_image_block(b,28,5,&next));
}
int main(void) {
    block_test();
    for(unsigned active=0;active<2;active++) {
        prepare(active);ota_upload_t u={0};uint32_t n,v;
        assert(ota_upload_header(header,4,&n,&v));assert(!ota_upload_header(header,5,&n,&v));
        header[8]^=1;assert(!ota_upload_header(header,4,&n,&v));header[8]^=1;
        // Reject another generation before erasing anything, even with a G1 target.
        header[57]='2';
        assert(!ota_upload_begin(&u,&layout,ops,header,4,123,1) && erases==0);
        header[57]='1';put32(header+8,0x23500202u);
        assert(!ota_upload_begin(&u,&layout,ops,header,4,123,1) && erases==0);
        put32(header+8,0x23500002u);
        header[56]='x';assert(!ota_upload_header(header,4,&n,&v));header[56]='g';
        assert(ota_upload_begin(&u,&layout,ops,header,4,123,1));
        assert(ota_upload_busy(&u) && erases==1 && !programs);
        assert(!ota_upload_begin(&u,&layout,ops,header,4,124,2));
        assert(!ota_upload_chunk(&u,124,0,payload,512,2));
        assert(!ota_upload_chunk(&u,123,512,payload,512,2));
        assert(!ota_upload_chunk(&u,123,0,payload,511,2));
        assert(!ota_upload_finish(&u,123,2) && !ota_upload_apply(&u,123));
        fill(&u);assert(programs==2 && ota_upload_finish(&u,123,9000));
        assert(programs==3 && u.state==OTA_READY && !memcmp(flash+u.target,payload,sizeof(payload)));
        for(uint32_t i=0x3fa000;i<sizeof(flash);i++)assert(flash[i]==0xa5);
        uint32_t active_start=layout.start[active];for(uint32_t i=0;i<0x180000;i++)assert(flash[active_start+i]==0xa5);
        for(uint32_t i=0;i<4096;i++)assert(flash[i]==0xa5);
        assert(!ota_upload_apply(&u,124));assert(ota_upload_apply(&u,123) && reboots==1);
        assert(!ota_upload_cancel(&u,123));
    }
    prepare(1);ota_upload_t u={0};assert(ota_upload_begin(&u,&layout,ops,header,4,123,1));fill(&u);
    validate_ok=false;assert(!ota_upload_finish(&u,123,9000) && u.state==OTA_ERROR && !reboots);
    for(unsigned i=0;i<4096;i++)assert(flash[u.target+i]==255);
    validate_ok=true;assert(ota_upload_begin(&u,&layout,ops,header,4,123,1));fill(&u);
    assert(ota_upload_finish(&u,123,9000));assert(ota_upload_cancel(&u,123) && !ota_upload_busy(&u));
    assert(ota_upload_begin(&u,&layout,ops,header,4,123,1));ota_upload_tick(&u,120001);assert(u.state==OTA_ERROR && !strcmp(u.error,"timeout"));
    erase_ok=false;assert(!ota_upload_begin(&u,&layout,ops,header,4,123,1));assert(u.state==OTA_ERROR);
    erase_ok=true;assert(ota_upload_begin(&u,&layout,ops,header,4,123,1));program_ok=false;
    for(unsigned i=0;i<15;i++)assert(ota_upload_chunk(&u,123,i*512,payload+i*512,512,i));
    assert(!ota_upload_chunk(&u,123,15*512,payload+15*512,512,16) && u.state==OTA_ERROR);
    puts("OTA upload bounds, A/B preservation, ordering, metadata, cancellation, timeout and injected failures passed");
    return 0;
}
