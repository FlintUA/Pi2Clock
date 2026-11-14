#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "network_time.h"

typedef enum {PHONE_NET_IDLE,PHONE_NET_PENDING,PHONE_NET_CANCELLED,PHONE_NET_BUSY,
    PHONE_NET_ACCESS_CHANGED,PHONE_NET_DONE,PHONE_NET_FAILED} phone_network_state_t;
typedef struct {
    phone_network_state_t state;
    bool from_direct, to_direct;
    uint32_t epoch;
    uint64_t due_ms;
} phone_network_plan_t;
bool phone_network_schedule(phone_network_plan_t *plan,bool current,bool target,uint32_t epoch,uint64_t now);
void phone_network_cancel(phone_network_plan_t *plan);
bool phone_network_due(phone_network_plan_t *plan,bool current,bool idle,uint32_t epoch,uint64_t now);
typedef struct {
    bool supported, available, direct, configured, direct_key_ready;
    char home_ssid[33], home_address[16], address[16];
    network_home_status_t home;
    phone_network_plan_t plan;
    uint64_t now_ms;
} phone_network_view_t;
int phone_network_json(char *out,size_t capacity,const phone_network_view_t *view,uint32_t epoch,uint32_t snapshot_id);
