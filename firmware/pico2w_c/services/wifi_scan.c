#include "wifi_scan.h"
#include <string.h>
static void sort_entries(wifi_scan_t *s){
    for(unsigned i=0;i<s->count;++i)for(unsigned j=i+1;j<s->count;++j)if(s->entries[j].rssi>s->entries[i].rssi){wifi_scan_entry_t t=s->entries[i];s->entries[i]=s->entries[j];s->entries[j]=t;}
}
void wifi_scan_begin(wifi_scan_t *s){uint32_t rev=s->revision+1u;*s=(wifi_scan_t){.revision=rev?rev:1u,.active=true,.state=WIFI_SCAN_ACTIVE};}
void wifi_scan_finish(wifi_scan_t *s,unsigned state){s->active=false;s->state=(uint8_t)state;}
void wifi_scan_add(wifi_scan_t *s,const uint8_t *ssid,size_t length,int16_t rssi,uint8_t auth){
    if(!s->active || !length || length>32u)return;
    for(size_t i=0;i<length;++i)if(ssid[i]<32u || ssid[i]==127u)return;
    char name[33]={0};memcpy(name,ssid,length);
    for(unsigned i=0;i<s->count;++i)if(!strcmp(s->entries[i].ssid,name)){
        if(rssi>s->entries[i].rssi){s->entries[i].rssi=rssi;s->entries[i].auth=auth;sort_entries(s);}return;
    }
    unsigned index=s->count;
    if(index==WIFI_SCAN_MAX){index=0;for(unsigned i=1;i<s->count;++i)if(s->entries[i].rssi<s->entries[index].rssi)index=i;
        if(rssi<=s->entries[index].rssi)return;
    }else ++s->count;
    s->entries[index]=(wifi_scan_entry_t){.rssi=rssi,.auth=auth};memcpy(s->entries[index].ssid,name,sizeof(name));
    sort_entries(s);
}
