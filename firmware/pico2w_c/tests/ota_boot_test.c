#include <assert.h>
#include <stdlib.h>
#include "../services/ota_boot.c"
char *clock_test_end=(char *)0x10010000u;
static int current,fail_table,buy_error;static bool trial;
static unsigned buys,reboots,last_index;static uint32_t reboot_target;
bool rom_get_boot_info(boot_info_t *b){*b=(boot_info_t){.partition=(int8_t)current,.tbyb_and_update_info=trial?1u:0u};return true;}
int rom_get_partition_table_info(uint32_t *out,uint32_t cap,uint32_t flags){
 if(fail_table)return -1;
 if(flags==PT_INFO_PT_INFO){assert(cap==4);out[0]=1;out[1]=0x102;out[2]=out[3]=0;return 4;}
 unsigned i=flags>>24;assert(cap==3 && i<2 && (flags&0xffffu)==0x8010u);last_index=i;
 out[0]=0x8010;out[1]=0x0c000000u | ((i?0x181u:1u)) | ((i?0x300u:0x180u)<<13);out[2]=i?2u:0u;return 3;
}
int rom_get_b_partition(unsigned p){assert(p==0);return 1;}
intptr_t rom_flash_runtime_to_storage_addr(uintptr_t p){assert(p==XIP_BASE);return XIP_BASE+(current?CLOCK_OTA_B_START:CLOCK_OTA_A_START);}
int rom_explicit_buy(uint8_t *p,uint32_t n){assert(p && n>=4096 && ((uintptr_t)p%4u)==0);++buys;return buy_error;}
int rom_reboot(uint32_t type,uint32_t delay,uint32_t target,uint32_t other){assert(type==4u && delay==250 && !other);++reboots;reboot_target=target;return 0;}
int main(void){
#ifdef _MSC_VER
 _set_error_mode(_OUT_TO_STDERR);_set_abort_behavior(0,_WRITE_ABORT_MSG|_CALL_REPORTFAULT);
#endif
 current=0;clock_ota_boot_init();assert(last_index==1 && clock_ota_layout_verified() && !clock_ota_writes_allowed());
 assert(!clock_ota_trial_inactive(true));assert(clock_ota_startup_confirm(false) && !buys); // An already accepted image retains offline clock operation.
 assert(clock_ota_writes_allowed());assert(!clock_ota_trial_inactive(false));assert(clock_ota_trial_inactive(true) && reboot_target==0x10181000u);
 current=1;trial=true;clock_ota_boot_init();assert(clock_ota_layout_verified() && !clock_ota_writes_allowed());
 assert(!clock_ota_startup_confirm(false) && !buys);assert(clock_ota_startup_confirm(true) && buys==1 && clock_ota_writes_allowed());
 assert(clock_ota_startup_confirm(true) && buys==1);assert(clock_ota_trial_inactive(true) && reboot_target==0x10001000u);
 clock_ota_boot_init();buy_error=-1;assert(!clock_ota_startup_confirm(true) && !clock_ota_writes_allowed());
 assert(!clock_ota_startup_confirm(true) && buys==2);assert(!clock_ota_trial_inactive(true));
 fail_table=1;clock_ota_boot_init();assert(!clock_ota_layout_verified() && !clock_ota_startup_confirm(true));
 fail_table=0;current=2;clock_ota_boot_init();assert(!clock_ota_layout_verified());
 current=0;clock_test_end=(char *)0x10180001u;clock_ota_boot_init();assert(!clock_ota_layout_verified());
 assert(reboots==2);puts("ota_boot_test: PASS");return 0;
}
