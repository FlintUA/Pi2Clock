#include "phone_bluetooth.h"
#include "phone_overview.h"
#include <inttypes.h>
#include <stdio.h>

int phone_bluetooth_json(char *out,size_t capacity,const phone_bt_view_t *v,
                         uint32_t epoch,uint32_t snapshot_id) {
    if(!out || !v || v->count>PHONE_BT_DEVICES) return -1;
    int n=snprintf(out,capacity,"{\"epoch\":%" PRIu32 ",\"snapshot_id\":%" PRIu32
        ",\"supported\":%s,\"available\":%s,\"scanning\":%s,\"connected\":%s,\"target\":\"%s\",\"known_count\":%u,\"devices\":[",
        epoch,snapshot_id,v->supported?"true":"false",v->available?"true":"false",
        v->scanning?"true":"false",v->connected?"true":"false",v->target,(unsigned)v->known_count);
    if(n<0 || (size_t)n>=capacity) return -1;
    size_t used=(size_t)n;
    for(unsigned i=0;i<v->count;++i) {
        char name[151];phone_json_name(name,v->devices[i].name);
        n=snprintf(out+used,capacity-used,"%s{\"id\":\"%s\",\"name\":\"%s\",\"saved\":%s}",
            i?",":"",v->devices[i].id,name,v->devices[i].saved?"true":"false");
        if(n<0 || (size_t)n>=capacity-used) return -1;
        used+=(size_t)n;
    }
    n=snprintf(out+used,capacity-used,"]}");
    return n<0 || (size_t)n>=capacity-used ? -1 : (int)(used+(size_t)n);
}
