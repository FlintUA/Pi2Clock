#pragma once
#include <stdint.h>
#include <stdbool.h>
#define PT_INFO_SINGLE_PARTITION 0x8000u
#define PT_INFO_PARTITION_LOCATION_AND_FLAGS 0x10u
#define PT_INFO_PT_INFO 1u
#define BOOT_TBYB_AND_UPDATE_FLAG_BUY_PENDING 1u
typedef struct {int8_t partition;uint8_t tbyb_and_update_info;} boot_info_t;
bool rom_get_boot_info(boot_info_t *);
int rom_get_partition_table_info(uint32_t *,uint32_t,uint32_t);
int rom_get_b_partition(unsigned);
intptr_t rom_flash_runtime_to_storage_addr(uintptr_t);
int rom_explicit_buy(uint8_t *,uint32_t);
int rom_reboot(uint32_t,uint32_t,uint32_t,uint32_t);
