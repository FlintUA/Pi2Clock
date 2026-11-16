#include "ota_layout.h"
#include <assert.h>
#ifdef _MSC_VER
#include <stdlib.h>
#endif
#include <stdio.h>
#include <stdint.h>
int main(void){
#ifdef _MSC_VER
 _set_error_mode(_OUT_TO_STDERR);_set_abort_behavior(0,_WRITE_ABORT_MSG|_CALL_REPORTFAULT);
#endif
 clock_ota_layout_t p={.start={0x1000,0x181000},.end={0x181000,0x301000},.count=2,.boot_partition=0,.runtime_storage_start=0x1000,.linked=true};
 assert(clock_ota_layout_valid(&p,984892));assert(clock_ota_layout_valid(&p,CLOCK_OTA_SLOT_SIZE));
 assert(!clock_ota_layout_valid(&p,0));assert(!clock_ota_layout_valid(&p,CLOCK_OTA_SLOT_SIZE+1));
 assert(clock_ota_inactive_range(&p,0x181000,0x180000));
 assert(!clock_ota_inactive_range(&p,0x1000,256));assert(!clock_ota_inactive_range(&p,0x180fff,256));
 assert(!clock_ota_inactive_range(&p,0x300fff,2));assert(!clock_ota_inactive_range(&p,0x301000,1));
 assert(!clock_ota_inactive_range(&p,0x3fa000,4096));assert(!clock_ota_inactive_range(&p,0x181000,UINT32_MAX));
 p.boot_partition=1;p.runtime_storage_start=0x181000;assert(clock_ota_layout_valid(&p,100));
 assert(clock_ota_inactive_range(&p,0x1000,0x180000));assert(!clock_ota_inactive_range(&p,0x181000,1));
 p.runtime_storage_start=0x1000;assert(!clock_ota_layout_valid(&p,100));
 p.runtime_storage_start=0x181000;p.linked=false;assert(!clock_ota_layout_valid(&p,100));
 p.linked=true;p.count=3;assert(!clock_ota_layout_valid(&p,100));
 p.count=2;p.end[1]=0x400000;assert(!clock_ota_layout_valid(&p,100));
 puts("ota_layout_test: PASS");return 0;
}
