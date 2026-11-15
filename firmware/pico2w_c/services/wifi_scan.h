#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define WIFI_SCAN_MAX 12u
typedef struct {char ssid[33];int16_t rssi;uint8_t auth;} wifi_scan_entry_t;
typedef struct {wifi_scan_entry_t entries[WIFI_SCAN_MAX];unsigned count;uint32_t revision;bool active;uint8_t state;} wifi_scan_t;
enum {WIFI_SCAN_IDLE,WIFI_SCAN_ACTIVE,WIFI_SCAN_DONE,WIFI_SCAN_FAILED,WIFI_SCAN_TIMEOUT};
void wifi_scan_begin(wifi_scan_t *scan);
void wifi_scan_add(wifi_scan_t *scan,const uint8_t *ssid,size_t length,int16_t rssi,uint8_t auth);
void wifi_scan_finish(wifi_scan_t *scan,unsigned state);
