#pragma once
#include <stdbool.h>
#include <stdint.h>
#define CLOCK_OTA_SLOT_SIZE 0x180000u
#define CLOCK_OTA_A_START 0x001000u
#define CLOCK_OTA_B_START 0x181000u
#define CLOCK_OTA_PROTECTED_START 0x3fa000u
typedef struct {uint32_t start[2],end[2];unsigned count;int boot_partition;uint32_t runtime_storage_start;bool linked;} clock_ota_layout_t;
bool clock_ota_layout_valid(const clock_ota_layout_t *layout,uint32_t image_size);
bool clock_ota_inactive_range(const clock_ota_layout_t *layout,uint32_t offset,uint32_t length);
