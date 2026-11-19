#include <assert.h>
#include <stdlib.h>
#include "hardware/structs/powman.h"
clock_test_powman_t clock_test_powman;
static uint32_t clock_test_sequence=7;
#define CLOCK_OTA_SEQUENCE clock_test_sequence
#include "../services/ota_boot.c"
char *clock_test_end=(char *)0x10010000u;
static int current,fail_table,buy_error;static bool trial;
static unsigned buys,reboots,last_index;static uint32_t reboot_target;
static uint8_t boot_type;
static int reboot_error;
bool rom_get_boot_info(boot_info_t *b){*b=(boot_info_t){.partition=(int8_t)current,.tbyb_and_update_info=trial?1u:0u,.boot_type=boot_type};return true;}
int rom_get_partition_table_info(uint32_t *out,uint32_t cap,uint32_t flags){
 if(fail_table)return -1;
 if(flags==PT_INFO_PT_INFO){assert(cap==4);out[0]=1;out[1]=0x102;out[2]=out[3]=0;return 4;}
 unsigned i=flags>>24;assert(cap==3 && i<2 && (flags&0xffffu)==0x8010u);last_index=i;
 out[0]=0x8010;out[1]=0x0c000000u | ((i?0x181u:1u)) | ((i?0x300u:0x180u)<<13);out[2]=i?2u:0u;return 3;
}
int rom_get_b_partition(unsigned p){assert(p==0);return 1;}
intptr_t rom_flash_runtime_to_storage_addr(uintptr_t p){assert(p==XIP_BASE);return XIP_BASE+(current?CLOCK_OTA_B_START:CLOCK_OTA_A_START);}
int rom_explicit_buy(uint8_t *p,uint32_t n){assert(p && n>=4096 && ((uintptr_t)p%4u)==0);++buys;return buy_error;}
int rom_reboot(uint32_t type,uint32_t delay,uint32_t target,uint32_t other){assert(type==4u && delay==250 && !other);++reboots;reboot_target=target;return reboot_error;}
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
 assert(reboots==2);
 // One-shot Direct handoff: reserved ROM/low-power registers remain untouched.
 current=0;trial=false;boot_type=0;buy_error=0;clock_test_end=(char *)0x10010000u;
 for(unsigned i=4;i<8;i++)powman_hw->scratch[i]=0x12340000u+i;
 for(unsigned i=0;i<4;i++)powman_hw->boot[i]=0x56780000u+i;
 clock_ota_boot_init();assert(clock_ota_startup_confirm(true));
 assert(!clock_ota_trial_inactive_network(false,true,8));
 assert(!clock_ota_trial_inactive_network(true,true,7));
 assert(clock_ota_trial_inactive_network(true,true,8));
 assert(powman_hw->scratch[0] && powman_hw->scratch[1]==CLOCK_OTA_B_START && powman_hw->scratch[2]==8);
 current=1;trial=true;boot_type=BOOT_TYPE_FLASH_UPDATE;clock_test_sequence=8;
 clock_ota_boot_init();assert(!clock_ota_take_direct_resume());
 assert(resume_boot_type==BOOT_TYPE_FLASH_UPDATE && resume_checks==63u && resume_requested);
 for(unsigned i=0;i<4;i++)assert(powman_hw->scratch[i]==0);
 assert(clock_ota_startup_confirm(true));assert(clock_ota_take_direct_resume());assert(!clock_ota_take_direct_resume());
 assert(resume_requested); // Diagnostics retain the boot observation after the one-shot is consumed.
 assert(clock_ota_trial_inactive_network(true,true,9));assert(powman_hw->scratch[1]==CLOCK_OTA_A_START);
 current=0;trial=true;boot_type=BOOT_TYPE_FLASH_UPDATE;clock_test_sequence=9;
 clock_ota_boot_init();assert(clock_ota_startup_confirm(true));assert(clock_ota_take_direct_resume());assert(!clock_ota_take_direct_resume());
 for(unsigned i=4;i<8;i++)assert(powman_hw->scratch[i]==0x12340000u+i);
 for(unsigned i=0;i<4;i++)assert(powman_hw->boot[i]==0x56780000u+i);
 // Ordinary restart, stale sequence, corruption and wrong target never select Direct.
 for(unsigned scenario=0;scenario<5;scenario++) {
  current=1;trial=false;boot_type=0;clock_test_sequence=8;clock_ota_boot_init();assert(clock_ota_startup_confirm(true));
  assert(clock_ota_trial_inactive_network(true,true,9));
  current=0;trial=true;boot_type=BOOT_TYPE_FLASH_UPDATE;clock_test_sequence=9;
  if(scenario==0)boot_type=0;
  if(scenario==1)powman_hw->scratch[3]^=1;
  if(scenario==2)current=1;
  if(scenario==3)clock_test_sequence=10;
  if(scenario==4)trial=false;
  clock_ota_boot_init();assert(clock_ota_startup_confirm(true));assert(!clock_ota_take_direct_resume());
 }
 // A failed ROM request clears its handoff; Home OTA and serial trials never arm it.
 current=0;trial=false;clock_test_sequence=7;boot_type=0;clock_ota_boot_init();assert(clock_ota_startup_confirm(true));
 reboot_error=-1;assert(!clock_ota_trial_inactive_network(true,true,8));reboot_error=0;
 for(unsigned i=0;i<4;i++)assert(!powman_hw->scratch[i]);
 assert(clock_ota_trial_inactive_network(true,true,8));
 assert(clock_ota_trial_inactive_network(true,false,8));for(unsigned i=0;i<4;i++)assert(!powman_hw->scratch[i]);
 assert(clock_ota_trial_inactive_network(true,true,8));
 assert(clock_ota_trial_inactive(true));for(unsigned i=0;i<4;i++)assert(!powman_hw->scratch[i]);
 // Failure before acceptance consumes the request so a rollback cannot reuse it.
 assert(clock_ota_trial_inactive_network(true,true,8));current=1;trial=true;boot_type=4;clock_test_sequence=8;
 clock_ota_boot_init();assert(!clock_ota_startup_confirm(false));
 current=0;trial=false;clock_test_sequence=7;boot_type=0;clock_ota_boot_init();assert(clock_ota_startup_confirm(true));assert(!clock_ota_take_direct_resume());
 puts("ota_boot_test: PASS");return 0;
}
