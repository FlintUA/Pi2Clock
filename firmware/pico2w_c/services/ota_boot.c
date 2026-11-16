#include "ota_boot.h"
#include "ota_layout.h"
#include "pico/bootrom.h"
#include "pico/stdlib.h"
#include "hardware/regs/addressmap.h"
#include "boot/picobin.h"
#include "boot/picoboot.h"
#include <stdio.h>
#include <inttypes.h>
static clock_ota_layout_t layout;
static bool verified,pending,confirmed,failed;
static uint32_t workarea[1024];
static bool partition(unsigned index,uint32_t *start,uint32_t *end,uint32_t *flags){
    uint32_t data[3]={0};
    int n=rom_get_partition_table_info(data,3,(index<<24)|PT_INFO_SINGLE_PARTITION|PT_INFO_PARTITION_LOCATION_AND_FLAGS);
    if(n!=3 || !(data[0]&PT_INFO_PARTITION_LOCATION_AND_FLAGS))return false;
    uint32_t perms=PICOBIN_PARTITION_PERMISSION_S_R_BITS|PICOBIN_PARTITION_PERMISSION_S_W_BITS;
    if((data[1]&perms)!=perms)return false;
    *start=(data[1]&PICOBIN_PARTITION_LOCATION_FIRST_SECTOR_BITS)*4096u;
    *end=(((data[1]&PICOBIN_PARTITION_LOCATION_LAST_SECTOR_BITS)>>PICOBIN_PARTITION_LOCATION_LAST_SECTOR_LSB)+1u)*4096u;
    *flags=data[2];return true;
}
void clock_ota_boot_init(void){
    boot_info_t boot={0};uint32_t info[4]={0},flags[2]={0};
    verified=pending=confirmed=failed=false;
    if(!rom_get_boot_info(&boot))return;
    pending=(boot.tbyb_and_update_info&BOOT_TBYB_AND_UPDATE_FLAG_BUY_PENDING)!=0;
    layout=(clock_ota_layout_t){.boot_partition=boot.partition};
    int n=rom_get_partition_table_info(info,4,PT_INFO_PT_INFO);
    if(n!=4 || !(info[0]&PT_INFO_PT_INFO) || !(info[1]&0x100u))return;
    layout.count=info[1]&0xffu;
    if(!partition(0,&layout.start[0],&layout.end[0],&flags[0]) || !partition(1,&layout.start[1],&layout.end[1],&flags[1]))return;
    layout.linked=(flags[0]&PICOBIN_PARTITION_FLAGS_LINK_TYPE_BITS)==0u &&
        ((flags[1]&PICOBIN_PARTITION_FLAGS_LINK_TYPE_BITS)>>PICOBIN_PARTITION_FLAGS_LINK_TYPE_LSB)==PICOBIN_PARTITION_FLAGS_LINK_TYPE_A_PARTITION &&
        (flags[1]&PICOBIN_PARTITION_FLAGS_LINK_VALUE_BITS)==0u && rom_get_b_partition(0)==1;
    intptr_t storage=rom_flash_runtime_to_storage_addr(XIP_BASE);
    if(storage<(intptr_t)XIP_BASE)return;
    layout.runtime_storage_start=(uint32_t)(storage-XIP_BASE);
    extern char __flash_binary_end;
    verified=clock_ota_layout_valid(&layout,(uint32_t)((uintptr_t)&__flash_binary_end-XIP_BASE));
}
bool clock_ota_layout_verified(void){return verified;}
bool clock_ota_writes_allowed(void){return verified && confirmed && !pending && !failed;}
bool clock_ota_get_layout(clock_ota_layout_t *out){if(!clock_ota_writes_allowed())return false;*out=layout;return true;}
bool clock_ota_startup_confirm(bool healthy){
    if(!verified || failed)return false;
    if(pending){
        if(!healthy)return false;
#ifdef CLOCK_OTA_TEST_REJECT_TRIAL
        puts("[OTA] Test: trial intentionally not accepted; waiting for ROM rollback");failed=true;return false;
#else
        int rc=rom_explicit_buy((uint8_t *)workarea,sizeof(workarea));
        if(rc){printf("[OTA] Trial acceptance failed=%d\n",rc);failed=true;return false;}
        pending=false;
#endif
    }
    confirmed=true;return true;
}
void clock_ota_status(void){
    printf("[OTA] layout=%s active=%c trial=%s accepted=%s writes=%s upload=WEB\n",
        verified?"OK":"INVALID",layout.boot_partition==0?'A':layout.boot_partition==1?'B':'?',pending?"YES":"NO",confirmed?"YES":"NO",clock_ota_writes_allowed()?"YES":"NO");
}
bool clock_ota_trial_inactive(bool idle){
    if(!idle || !clock_ota_writes_allowed())return false;
    uint32_t target=layout.start[(unsigned)layout.boot_partition^1u];
    printf("[OTA] Trial reboot to storage 0x%08" PRIx32 "; ROM validates the inactive image\n",target);
    fflush(stdout);
    return rom_reboot(REBOOT2_FLAG_REBOOT_TYPE_FLASH_UPDATE,250,XIP_BASE+target,0)==0;
}
