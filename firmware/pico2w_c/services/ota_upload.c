#include "ota_upload.h"
#include <string.h>
static uint32_t le32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
bool ota_upload_header(const uint8_t *h,uint32_t current,uint32_t *size,uint32_t *sequence) {
    if(memcmp(h,"CLOCKOT1",8) || le32(h+8)!=0x23500002u || le32(h+20)!=1u) return false;
    *size=le32(h+12); *sequence=le32(h+16);
    if(*size<4096u || *size>CLOCK_OTA_SLOT_SIZE || *sequence<=current || *sequence>65535u) return false;
    for(unsigned i=120;i<128;i++) if(h[i]) return false;
    bool ended=false;
    for(unsigned i=56;i<120;i++) {
        if(!h[i]) ended=true;
        else if(ended || h[i]<32 || h[i]>126) return false;
    }
    return ended && h[56];
}
bool ota_upload_busy(const ota_upload_t *u) {
    return u->state==OTA_RECEIVING || u->state==OTA_READY || u->state==OTA_REBOOTING;
}
static bool fail(ota_upload_t *u,const char *error) {u->state=OTA_ERROR;u->error=error;return false;}
static bool range(ota_upload_t *u,uint32_t offset) {return clock_ota_inactive_range(&u->layout,offset,4096u);}
bool ota_upload_begin(ota_upload_t *u,const clock_ota_layout_t *layout,ota_upload_ops_t ops,
                      const uint8_t *header,uint32_t current,uint32_t session,uint64_t now) {
    uint32_t size,seq;
    if(ota_upload_busy(u) || !session || !clock_ota_layout_valid(layout,1u) ||
       !ops.erase || !ops.program || !ops.validate || !ops.reboot || !ota_upload_header(header,current,&size,&seq)) return false;
    memset(u,0,sizeof(*u));u->layout=*layout;u->ops=ops;u->size=size;u->sequence=seq;
    u->session=session;u->target=layout->start[(unsigned)layout->boot_partition^1u];u->touched=now;
    memcpy(u->header,header,OTA_HEADER_SIZE);memset(u->first,255,4096);memset(u->sector,255,4096);
    // Invalidate the candidate first. Keep its first sector in RAM until all data validates.
    if(!range(u,u->target) || !ops.erase(u->target)) return fail(u,"erase_failed");
    u->state=OTA_RECEIVING;u->error="none";return true;
}
bool ota_upload_chunk(ota_upload_t *u,uint32_t session,uint32_t offset,const uint8_t *data,size_t size,uint64_t now) {
    if(u->state!=OTA_RECEIVING || session!=u->session || offset!=u->received || !size ||
       size>OTA_CHUNK_SIZE || size>u->size-u->received ||
       (size!=OTA_CHUNK_SIZE && size!=u->size-u->received)) return false;
    uint32_t in_sector=offset%4096u;
    uint8_t *buffer=offset<4096u?u->first:u->sector;
    memcpy(buffer+in_sector,data,size);u->received+=(uint32_t)size;u->touched=now;
    if(offset>=4096u && (u->received%4096u==0 || u->received==u->size)) {
        uint32_t address=u->target+(offset&~4095u);
        if(!range(u,address) || !u->ops.erase(address) || !u->ops.program(address,buffer)) return fail(u,"write_failed");
        memset(u->sector,255,4096);
    }
    return true;
}
bool ota_upload_finish(ota_upload_t *u,uint32_t session,uint64_t now) {
    if(u->state!=OTA_RECEIVING || session!=u->session || u->received!=u->size) return false;
    if(!u->ops.validate(u->target,u->size,u->first,u->header)) return fail(u,"validation_failed");
    if(!range(u,u->target) || !u->ops.program(u->target,u->first)) return fail(u,"commit_failed");
    u->state=OTA_READY;u->touched=now;return true;
}
bool ota_upload_cancel(ota_upload_t *u,uint32_t session) {
    if(!ota_upload_busy(u) || u->state==OTA_REBOOTING || session!=u->session) return false;
    if(!range(u,u->target) || !u->ops.erase(u->target)) return fail(u,"cancel_failed");
    u->state=OTA_IDLE;u->error="cancelled";return true;
}
bool ota_upload_apply(ota_upload_t *u,uint32_t session) {
    if(u->state!=OTA_READY || session!=u->session) return false;
    u->state=OTA_REBOOTING;
    if(!u->ops.reboot()) return fail(u,"reboot_failed");
    return true;
}
void ota_upload_tick(ota_upload_t *u,uint64_t now) {
    if((u->state==OTA_RECEIVING || u->state==OTA_READY) && now-u->touched>=120000u) {
        if(ota_upload_cancel(u,u->session)) fail(u,"timeout");
    }
}
