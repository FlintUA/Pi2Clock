#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "phone_bluetooth.h"

int main(void) {
    phone_bt_view_t v={0};char out[4096];
    assert(phone_bluetooth_json(out,sizeof(out),&v,1,2)>0);
    assert(strstr(out,"\"devices\":[]") && strstr(out,"\"supported\":false"));
    v.count=PHONE_BT_DEVICES;v.known_count=4;v.supported=v.available=v.scanning=true;
    memcpy(v.target,"FFFFFFFFFFFE",13);
    for(unsigned i=0;i<PHONE_BT_DEVICES;++i) {
        snprintf(v.devices[i].id,sizeof(v.devices[i].id),"0000000000%02X",i+1);
        memset(v.devices[i].name,1,24);v.devices[i].saved=i<4;
    }
    int n=phone_bluetooth_json(out,sizeof(out),&v,UINT32_MAX,UINT32_MAX);
    assert(n>0 && n<3800 && strstr(out,"\\u0001")); // Leaves room for the HTTP header.
    char short_buffer[9];memset(short_buffer,'!',sizeof(short_buffer));
    assert(phone_bluetooth_json(short_buffer,8,&v,1,2)==-1 && short_buffer[8]=='!');
    v.count=17;assert(phone_bluetooth_json(out,sizeof(out),&v,1,2)==-1);
    v.count=1;memcpy(v.devices[0].name,"A\"\\\n",5);
    assert(phone_bluetooth_json(out,sizeof(out),&v,1,2)>0 && strstr(out,"A\\\"\\\\\\u000a"));
    memcpy(v.devices[0].name,"\xd0\x9a\xd0\xbe",5);
    assert(phone_bluetooth_json(out,sizeof(out),&v,1,2)>0 && strstr(out,"\xd0\x9a\xd0\xbe"));
    memset(v.devices[0].name,0xff,1);v.devices[0].name[1]=0;
    assert(phone_bluetooth_json(out,sizeof(out),&v,1,2)>0 && strstr(out,"\\ufffd"));
    puts("phone_bluetooth_test: PASS");return 0;
}
