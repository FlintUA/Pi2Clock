#include "phone_wifi.h"
#include <stddef.h>
#include <string.h>
static int hex_digit(char c) {
    return c>='0' && c<='9'?c-'0':c>='a' && c<='f'?c-'a'+10:c>='A' && c<='F'?c-'A'+10:-1;
}
static bool decode_bytes(const char *text,size_t length,char *out,size_t maximum) {
    if(length%2 || length/2>maximum) return false;
    for(size_t i=0;i<length;i+=2) {
        int a=hex_digit(text[i]),b=hex_digit(text[i+1]);
        if(a<0 || b<0) return false;
        unsigned byte=(unsigned)(a*16+b);
        if(byte<32u || byte==127u) return false; // No NUL/control bytes or log injection.
        out[i/2]=(char)byte;
    }
    out[length/2]=0;return true;
}
bool phone_wifi_decode(const char *text,phone_wifi_config_t *config) {
    const char *space=strchr(text,' ');
    *config=(phone_wifi_config_t){0};
    if(!space || space==text || !decode_bytes(text,(size_t)(space-text),config->ssid,32)) return false;
    const char *key=space+1;
    if(strcmp(key,"-")==0) return true; // Explicit open network.
    size_t length=strlen(key);
    if(length<16 || !decode_bytes(key,length,config->password,64)) return false;
    if(length==128u) {
        for(unsigned i=0;i<64u;++i) if(hex_digit(config->password[i])<0) return false;
    }
    return true;
}
bool phone_wifi_busy(const phone_wifi_plan_t *p) {
    return p->state==WIFI_SETUP_PENDING || p->state==WIFI_SETUP_TESTING || p->state==WIFI_SETUP_RESTORE;
}
void phone_wifi_clear_secret(phone_wifi_plan_t *p) { memset(p->candidate.password,0,sizeof(p->candidate.password)); }
bool phone_wifi_schedule(phone_wifi_plan_t *p,const phone_wifi_config_t *config,uint32_t epoch,uint32_t id,uint64_t now) {
    if(phone_wifi_busy(p) || !config->ssid[0]) return false;
    *p=(phone_wifi_plan_t){.candidate=*config,.state=WIFI_SETUP_PENDING,.epoch=epoch,.request_id=id,.due_ms=now+5000u};
    return true;
}
bool phone_wifi_schedule_saved(phone_wifi_plan_t *p,const phone_wifi_config_t *c,unsigned slot,unsigned restore_profile,
    bool from_direct,uint32_t epoch,uint32_t id,uint64_t now) {
    if(slot>1u || restore_profile>1u || !phone_wifi_schedule(p,c,epoch,id,now))return false;
    p->saved_connect=true;p->from_direct=from_direct;p->slot=(uint8_t)slot;p->restore_profile=(uint8_t)restore_profile;
    return true;
}
void phone_wifi_cancel(phone_wifi_plan_t *p,phone_wifi_reason_t reason) {
    if(p->state==WIFI_SETUP_PENDING) {p->state=WIFI_SETUP_CANCELLED;phone_wifi_clear_secret(p);}
    else if(p->state==WIFI_SETUP_TESTING) p->state=WIFI_SETUP_RESTORE;
    else return;
    p->reason=reason;
}
phone_wifi_action_t phone_wifi_step(phone_wifi_plan_t *p,uint64_t now,bool idle,bool direct,uint32_t epoch,bool home_ready) {
    if(p->state==WIFI_SETUP_PENDING) {
        if(epoch!=p->epoch || direct!=(p->saved_connect?p->from_direct:true)) phone_wifi_cancel(p,WIFI_REASON_CHANGED);
        else if(!idle) phone_wifi_cancel(p,WIFI_REASON_BUSY);
        else if(now>=p->due_ms) {
            p->state=WIFI_SETUP_TESTING;p->due_ms=now+45000u;return WIFI_ACTION_START;
        }
    } else if(p->state==WIFI_SETUP_TESTING) {
        if(direct) phone_wifi_cancel(p,WIFI_REASON_CHANGED);
        else if(!idle) phone_wifi_cancel(p,WIFI_REASON_BUSY);
        else if(now>=p->due_ms) phone_wifi_cancel(p,WIFI_REASON_TIMEOUT);
        else if(home_ready) {p->state=WIFI_SETUP_SAVED;return WIFI_ACTION_SAVE;}
    }
    return p->state==WIFI_SETUP_RESTORE && idle?WIFI_ACTION_RESTORE:WIFI_ACTION_NONE;
}
void phone_wifi_recovered(phone_wifi_plan_t *p,bool success) {
    p->state=success?WIFI_SETUP_FAILED:WIFI_SETUP_RECOVERY_FAILED;phone_wifi_clear_secret(p);
}
const char *phone_wifi_state_name(phone_wifi_state_t state) {
    static const char *const names[]={"idle","pending","testing","restoring","saved","failed","cancelled","recovery_failed"};
    return (unsigned)state<8u?names[state]:names[0];
}
const char *phone_wifi_reason_name(phone_wifi_reason_t reason) {
    static const char *const names[]={"none","cancelled","busy","timeout","changed","radio"};
    return (unsigned)reason<6u?names[reason]:names[0];
}
