#include "wifi_scan.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){wifi_scan_t s={0};wifi_scan_begin(&s);
 const uint8_t name[]="Home";wifi_scan_add(&s,name,4,-80,4);wifi_scan_add(&s,name,4,-40,4);assert(s.count==1 && s.entries[0].rssi==-40);
 wifi_scan_add(&s,name,0,-1,4);wifi_scan_add(&s,(const uint8_t *)"a\nb",3,-1,4);assert(s.count==1);
 for(unsigned i=0;i<20;++i){char n[12];int size=snprintf(n,sizeof(n),"Network%02u",i);wifi_scan_add(&s,(const uint8_t *)n,(size_t)size,(int16_t)(-100+(int)i),4);}
 assert(s.count==WIFI_SCAN_MAX);for(unsigned i=1;i<s.count;++i)assert(s.entries[i-1].rssi>=s.entries[i].rssi);
 wifi_scan_add(&s,(const uint8_t *)"Network19",9,-5,4);assert(s.entries[0].rssi==-5);
 wifi_scan_finish(&s,WIFI_SCAN_TIMEOUT);wifi_scan_add(&s,(const uint8_t *)"Late",4,-1,0);assert(strcmp(s.entries[0].ssid,"Late"));
 uint32_t rev=s.revision;wifi_scan_begin(&s);assert(s.active && !s.count && s.revision!=rev);
 puts("wifi_scan_test: PASS");return 0;}
