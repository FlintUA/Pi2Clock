#include "phone_network.h"
#include "phone_overview.h"
#include <inttypes.h>
#include <stdio.h>

bool phone_network_schedule(phone_network_plan_t *p,bool current,bool target,uint32_t epoch,uint64_t now) {
    if(p->state==PHONE_NET_PENDING) return p->epoch==epoch && p->from_direct==current && p->to_direct==target;
    *p=(phone_network_plan_t){.state=current==target?PHONE_NET_IDLE:PHONE_NET_PENDING,
        .from_direct=current,.to_direct=target,.epoch=epoch,.due_ms=now+5000u};
    return true;
}
void phone_network_cancel(phone_network_plan_t *p) {
    if(p->state==PHONE_NET_PENDING) p->state=PHONE_NET_CANCELLED;
}
bool phone_network_due(phone_network_plan_t *p,bool current,bool idle,uint32_t epoch,uint64_t now) {
    if(p->state!=PHONE_NET_PENDING) return false;
    if(p->epoch!=epoch || p->from_direct!=current) {p->state=PHONE_NET_ACCESS_CHANGED;return false;}
    if(!idle) {p->state=PHONE_NET_BUSY;return false;}
    if(now<p->due_ms) return false;
    p->state=PHONE_NET_DONE;return true;
}
int phone_network_json(char *out,size_t capacity,const phone_network_view_t *v,uint32_t epoch,uint32_t snapshot_id) {
    if(!out || !v) return -1;
    static const char *const states[]={"idle","pending","cancelled","cancelled_busy","cancelled_changed","done","failed"};
    static const char *const home[]={"offline","unconfigured","suspended","wait_idle","connecting","address","retry","ready"};
    char ssid[193];
    if(!phone_json_text(ssid,sizeof(ssid),v->home_ssid,32)) return -1;
    uint64_t left=v->plan.state==PHONE_NET_PENDING && v->plan.due_ms>v->now_ms ? (v->plan.due_ms-v->now_ms+999u)/1000u:0;
    int n=snprintf(out,capacity,"{\"epoch\":%" PRIu32 ",\"snapshot_id\":%" PRIu32
        ",\"supported\":%s,\"available\":%s,\"mode\":\"%s\",\"configured\":%s,\"direct_key_ready\":%s,"
        "\"home_ssid\":\"%s\",\"home_address\":\"%s\",\"address\":\"%s\",\"home_state\":\"%s\",\"home_seconds\":%" PRIu32 ","
        "\"transition\":\"%s\",\"target\":\"%s\",\"seconds\":%" PRIu64 "}",epoch,snapshot_id,
        v->supported?"true":"false",v->available?"true":"false",v->direct?"direct":"home",
        v->configured?"true":"false",v->direct_key_ready?"true":"false",ssid,v->home_address,v->address,
        (unsigned)v->home.state<8u?home[v->home.state]:home[0],v->home.seconds,
        (unsigned)v->plan.state<7u?states[v->plan.state]:states[0],v->plan.to_direct?"direct":"home",left);
    return n<0 || (size_t)n>=capacity ? -1:n;
}
