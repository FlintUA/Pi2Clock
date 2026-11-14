#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "phone_network.h"

int main(void) {
    phone_network_plan_t p={0};uint64_t start=UINT64_C(0xffffffff)-1000u;
    assert(phone_network_schedule(&p,false,true,42,start));
    assert(p.state==PHONE_NET_PENDING && p.due_ms==start+5000u);
    assert(phone_network_schedule(&p,false,true,42,start+1000u) && p.due_ms==start+5000u);
    assert(!phone_network_schedule(&p,false,false,42,start+1000u));
    assert(!phone_network_due(&p,false,true,42,start+4999u));
    assert(phone_network_due(&p,false,true,42,start+5000u) && p.state==PHONE_NET_DONE);
    assert(!phone_network_due(&p,false,true,42,start+5001u));
    assert(phone_network_schedule(&p,true,false,42,100));phone_network_cancel(&p);
    assert(p.state==PHONE_NET_CANCELLED && !phone_network_due(&p,true,true,42,9999));
    assert(phone_network_schedule(&p,true,false,42,100));
    assert(!phone_network_due(&p,true,false,42,200) && p.state==PHONE_NET_BUSY);
    assert(!phone_network_due(&p,true,true,42,9999)); // No unexpected replay after audio becomes idle.
    assert(phone_network_schedule(&p,true,false,42,100));
    assert(!phone_network_due(&p,true,true,43,200) && p.state==PHONE_NET_ACCESS_CHANGED);
    assert(phone_network_schedule(&p,true,false,43,100));
    assert(!phone_network_due(&p,false,true,43,200) && p.state==PHONE_NET_ACCESS_CHANGED);
    assert(phone_network_schedule(&p,true,true,43,100) && p.state==PHONE_NET_IDLE);

    phone_network_view_t v={.supported=true,.available=true,.configured=true,.direct_key_ready=true,
        .home={NETWORK_HOME_READY,UINT32_MAX},.now_ms=100};
    memset(v.home_ssid,1,32);memcpy(v.home_address,"255.255.255.255",16);memcpy(v.address,v.home_address,16);
    assert(phone_network_schedule(&v.plan,false,true,42,100));
    char out[2048];int n=phone_network_json(out,sizeof(out),&v,UINT32_MAX,UINT32_MAX);
    assert(n>0 && n<1200 && strstr(out,"\"seconds\":5") && strstr(out,"\\u0001"));
    assert(!strstr(out,"password") && !strstr(out,"token"));
    char small[9];memset(small,'!',9);assert(phone_network_json(small,8,&v,1,2)==-1 && small[8]=='!');
    memcpy(v.home_ssid,"\xd0\xa1\xd0\xb5\xd1\x82\xd1\x8c",9);
    assert(phone_network_json(out,sizeof(out),&v,1,2)>0 && strstr(out,v.home_ssid));
    puts("phone_network_test: PASS");return 0;
}
