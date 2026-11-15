#include "phone_wifi.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void) {
    phone_wifi_config_t c;
    assert(phone_wifi_decode("486f6d652057694669 70617373776f7264",&c));
    assert(!strcmp(c.ssid,"Home WiFi") && !strcmp(c.password,"password"));
    assert(phone_wifi_decode("e4bda0e5a5bd -",&c));
    assert(strlen(c.ssid)==6 && !c.password[0]);
    assert(!phone_wifi_decode(" -",&c));assert(!phone_wifi_decode("00 -",&c));
    assert(!phone_wifi_decode("0a -",&c));assert(!phone_wifi_decode("ff0 -",&c));
    assert(!phone_wifi_decode("486f6d65 1234",&c));
    assert(!phone_wifi_decode("486f6d65 70617373776f7264 extra",&c));
    char text[200];memset(text,'6',64);memcpy(text+64," -",3);
    assert(phone_wifi_decode(text,&c) && strlen(c.ssid)==32);
    memset(text,'6',66);memcpy(text+66," -",3);assert(!phone_wifi_decode(text,&c));
    strcpy(text,"41 ");memset(text+3,'3',128);text[131]=0;
    assert(phone_wifi_decode(text,&c) && strlen(c.password)==64);
    memcpy(text+3,"7a",2);assert(!phone_wifi_decode(text,&c)); // 64-byte PSK must itself be hexadecimal.
    assert(phone_wifi_decode("486f6d65 70617373776f7264",&c));
    phone_wifi_plan_t p={0};uint64_t now=(uint64_t)UINT32_MAX+100000u;
    assert(phone_wifi_schedule(&p,&c,9,1,now));
    assert(!phone_wifi_schedule(&p,&c,9,2,now));
    assert(phone_wifi_step(&p,now+4999,true,true,9,false)==WIFI_ACTION_NONE);
    assert(phone_wifi_step(&p,now+5000,true,true,9,false)==WIFI_ACTION_START);
    assert(phone_wifi_step(&p,now+5001,true,false,10,false)==WIFI_ACTION_NONE); // Own mode/IP epoch changes are expected.
    assert(phone_wifi_step(&p,now+5002,true,false,10,true)==WIFI_ACTION_SAVE);
    phone_wifi_clear_secret(&p);assert(!p.candidate.password[0]);
    assert(phone_wifi_step(&p,now+6000,true,false,10,true)==WIFI_ACTION_NONE);
    assert(phone_wifi_schedule(&p,&c,11,2,now));phone_wifi_cancel(&p,WIFI_REASON_CANCEL);
    assert(p.state==WIFI_SETUP_CANCELLED && !p.candidate.password[0]);
    assert(phone_wifi_step(&p,now+5000,true,true,11,false)==WIFI_ACTION_NONE);
    assert(phone_wifi_schedule(&p,&c,11,3,now));
    assert(phone_wifi_step(&p,now+2,false,true,11,false)==WIFI_ACTION_NONE && p.state==WIFI_SETUP_CANCELLED);
    assert(phone_wifi_schedule(&p,&c,11,4,now));
    assert(phone_wifi_step(&p,now+2,true,true,12,false)==WIFI_ACTION_NONE && p.reason==WIFI_REASON_CHANGED);
    assert(phone_wifi_schedule(&p,&c,11,5,now));
    assert(phone_wifi_step(&p,now+5000,true,true,11,false)==WIFI_ACTION_START);
    assert(phone_wifi_step(&p,now+50000,true,false,12,true)==WIFI_ACTION_RESTORE); // Timeout wins over late READY.
    assert(p.reason==WIFI_REASON_TIMEOUT);phone_wifi_recovered(&p,true);
    assert(p.state==WIFI_SETUP_FAILED && !p.candidate.password[0]);
    assert(phone_wifi_schedule(&p,&c,11,6,now));
    assert(phone_wifi_step(&p,now+5000,true,true,11,false)==WIFI_ACTION_START);
    assert(phone_wifi_step(&p,now+5001,false,false,12,true)==WIFI_ACTION_NONE);
    assert(p.state==WIFI_SETUP_RESTORE && p.reason==WIFI_REASON_BUSY);
    assert(phone_wifi_step(&p,now+99999,false,false,12,false)==WIFI_ACTION_NONE);
    assert(phone_wifi_step(&p,now+100000,true,false,12,false)==WIFI_ACTION_RESTORE);
    phone_wifi_recovered(&p,false);assert(p.state==WIFI_SETUP_RECOVERY_FAILED && !p.candidate.password[0]);
    assert(phone_wifi_schedule(&p,&c,11,7,now));
    assert(phone_wifi_step(&p,now+5000,true,true,11,false)==WIFI_ACTION_START);
    phone_wifi_cancel(&p,WIFI_REASON_CANCEL);
    assert(phone_wifi_step(&p,now+5001,true,false,12,false)==WIFI_ACTION_RESTORE);
    phone_wifi_recovered(&p,true);
    assert(!strcmp(phone_wifi_state_name(p.state),"failed"));
    assert(!strcmp(phone_wifi_reason_name(p.reason),"cancelled"));
    puts("phone_wifi_test: PASS");return 0;
}
