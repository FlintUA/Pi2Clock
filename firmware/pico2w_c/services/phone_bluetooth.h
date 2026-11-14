#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define PHONE_BT_DEVICES 16u
typedef struct {
    char id[13]; // Stable 48-bit peer address, hex without separators; never a row index.
    char name[25];
    bool saved;
} phone_bt_device_t;
typedef struct {
    bool supported, available, scanning, connected;
    char target[13];
    uint8_t count, known_count;
    phone_bt_device_t devices[PHONE_BT_DEVICES];
} phone_bt_view_t;
int phone_bluetooth_json(char *out,size_t capacity,const phone_bt_view_t *view,
                         uint32_t epoch,uint32_t snapshot_id);
