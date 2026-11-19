#include "phone_ota.h"
#include "ota_upload.h"
#include "ota_image.h"
#include "ota_boot.h"
#include "phone_web.h"
#include "pico/bootrom.h"
#include "pico/cyw43_arch.h"
#include "pico/sha256.h"
#include "hardware/regs/addressmap.h"
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
static ota_upload_t upload;
typedef struct {char action[8],owner[33];uint32_t session,offset,epoch;size_t size;uint8_t data[OTA_CHUNK_SIZE];} request_t;
static request_t mailbox;
static volatile bool queued,busy,available;
static char owner[33],view[384]="{\"supported\":true,\"state\":\"idle\",\"available\":false}";
static uint32_t owner_epoch;
static uint64_t apply_at;
static uint32_t word(const uint8_t *p) {uint32_t v;memcpy(&v,p,4);return v;}
static const uint8_t *physical(uint32_t offset) {return (const uint8_t *)(XIP_NOCACHE_NOALLOC_NOTRANSLATE_BASE+offset);}
static bool erase_sector(uint32_t offset) {
    clock_ota_layout_t layout;
    if(!clock_ota_get_layout(&layout) || !clock_ota_inactive_range(&layout,offset,4096))return false;
    cflash_flags_t flags={.flags=(CFLASH_SECLEVEL_VALUE_SECURE<<CFLASH_SECLEVEL_LSB)|(CFLASH_OP_VALUE_ERASE<<CFLASH_OP_LSB)};
    return rom_flash_op(flags,XIP_BASE+offset,4096,NULL)==0;
}
static bool program_sector(uint32_t offset,const uint8_t *data) {
    clock_ota_layout_t layout;
    if(!clock_ota_get_layout(&layout) || !clock_ota_inactive_range(&layout,offset,4096))return false;
    cflash_flags_t flags={.flags=(CFLASH_SECLEVEL_VALUE_SECURE<<CFLASH_SECLEVEL_LSB)|(CFLASH_OP_VALUE_PROGRAM<<CFLASH_OP_LSB)};
    return rom_flash_op(flags,XIP_BASE+offset,4096,(uint8_t *)data)==0 && !memcmp(physical(offset),data,4096);
}
static bool validate_image(uint32_t offset,uint32_t size,const uint8_t *first,const uint8_t *header) {
    // Restrict browser packages to the reviewed monolithic ARM Secure/TBYB build format.
    uint32_t next,back,seq=word(header+16);
    if(!ota_image_block(first+0x138u,28u,seq,&next) || next>size-0x138u)return false;
    uint32_t last=0x138u+next;
    if(last<4096u || last>=size || size-last>384u ||
       !ota_image_block(physical(offset+last),size-last,seq,&back) || last+back!=0x138u)return false;
    pico_sha256_state_t hash;sha256_result_t result;
    if(pico_sha256_try_start(&hash,SHA256_BIG_ENDIAN,false)!=0)return false;
    pico_sha256_update_blocking(&hash,first,4096);
    for(uint32_t at=4096;at<size;at+=4096) {
        uint32_t n=size-at;if(n>4096)n=4096;
        pico_sha256_update_blocking(&hash,physical(offset+at),n);
    }
    pico_sha256_finish(&hash,&result);
    return !memcmp(result.bytes,header+24,32);
}
static bool reboot_trial(void) {return clock_ota_trial_inactive_network(true,phone_web_direct(),upload.sequence);}
static int nibble(char c) {return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;}
static bool number(const char **p,uint32_t *out) {
    if(**p<'0' || **p>'9')return false;
    uint32_t n=0;
    while(**p>='0' && **p<='9') {unsigned digit=(unsigned)(*(*p)++-'0');if(n>(UINT32_MAX-digit)/10u)return false;n=n*10u+digit;}
    if(*(*p)++!=' ')return false;
    *out=n;return true;
}
bool phone_ota_submit(const char *body,const char *who,uint32_t epoch) {
    if(queued)return false;
    request_t r={0};const char *end=strchr(body,' ');
    if(!end || end==body || end-body>=8)return false;
    memcpy(r.action,body,(size_t)(end-body));const char *hex=end+1;
    if(!number(&hex,&r.session) || !number(&hex,&r.offset) || !r.session)return false;
    size_t n=strlen(hex);
    if(strcmp(hex,"-")) {
        if(!n || n%2 || n>2u*OTA_CHUNK_SIZE)return false;
        r.size=n/2;
        for(size_t i=0;i<r.size;i++) {int a=nibble(hex[2*i]),b=nibble(hex[2*i+1]);if(a<0 || b<0)return false;r.data[i]=(uint8_t)(a*16+b);}
    }
    if(strcmp(r.action,"begin") && strcmp(r.action,"chunk") && strcmp(r.action,"finish") && strcmp(r.action,"cancel") && strcmp(r.action,"apply"))return false;
    if(strcmp(r.action,"chunk") && r.offset)return false;
    if(!strcmp(r.action,"begin") ? r.size!=OTA_HEADER_SIZE : !strcmp(r.action,"chunk") ? !r.size : r.size!=0)return false;
    if(strlen(who)>32)return false;
    if(!strcmp(r.action,"begin")) {if(!available || busy)return false;busy=true;}
    strcpy(r.owner,who);r.epoch=epoch;mailbox=r;queued=true;return true;
}
bool phone_ota_busy(void) {return busy;}
int phone_ota_json(char *out,size_t size) {return snprintf(out,size,"%s",view);}
void phone_ota_service(bool idle,uint64_t now,uint32_t epoch) {
    request_t r;bool have;
    cyw43_arch_lwip_begin();have=queued;if(have)r=mailbox;cyw43_arch_lwip_end();
    bool accepted=false;
    if(ota_upload_busy(&upload) && owner_epoch!=epoch)ota_upload_cancel(&upload,upload.session);
    if(have && r.epoch==epoch) {
        if(!strcmp(r.action,"begin")) {
            clock_ota_layout_t layout;
            if(idle && !ota_upload_busy(&upload) && clock_ota_get_layout(&layout)) {
                ota_upload_ops_t ops={erase_sector,program_sector,validate_image,reboot_trial};
                accepted=ota_upload_begin(&upload,&layout,ops,r.data,CLOCK_OTA_SEQUENCE,r.session,now);
                if(accepted){strcpy(owner,r.owner);owner_epoch=epoch;}
            }
        } else if(!strcmp(owner,r.owner) && r.session==upload.session) {
            if(!strcmp(r.action,"chunk"))accepted=ota_upload_chunk(&upload,r.session,r.offset,r.data,r.size,now);
            else if(!strcmp(r.action,"finish"))accepted=ota_upload_finish(&upload,r.session,now);
            else if(!strcmp(r.action,"cancel"))accepted=ota_upload_cancel(&upload,r.session);
            else if(!strcmp(r.action,"apply") && upload.state==OTA_READY){accepted=true;apply_at=now+1500u;upload.state=OTA_REBOOTING;}
        }
    }
    ota_upload_tick(&upload,now);
    static const char *states[]={"idle","receiving","ready","rebooting","error"};
    cyw43_arch_lwip_begin();
    busy=ota_upload_busy(&upload);available=idle && !busy && clock_ota_writes_allowed();
    snprintf(view,sizeof(view),"{\"supported\":true,\"state\":\"%s\",\"available\":%s,\"session\":%" PRIu32 ",\"received\":%" PRIu32 ",\"size\":%" PRIu32 ",\"sequence\":%u,\"current_sequence\":%u,\"mode_restore\":true,\"restart_mode\":\"%s\",\"active\":\"%c\",\"error\":\"%s\",\"request_ok\":%s}",
        states[upload.state],available?"true":"false",upload.session,upload.received,upload.size,(unsigned)upload.sequence,(unsigned)CLOCK_OTA_SEQUENCE,phone_web_direct()?"direct":"home",
        rom_flash_runtime_to_storage_addr(XIP_BASE)==XIP_BASE+CLOCK_OTA_A_START?'A':'B',upload.error?upload.error:"none",!have || accepted?"true":"false");
    if(have)queued=false;
    cyw43_arch_lwip_end();
    if(apply_at && now>=apply_at) {
        apply_at=0;upload.state=OTA_READY;
        ota_upload_apply(&upload,upload.session);
    }
}
