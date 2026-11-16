#include "ota_layout.h"
bool clock_ota_layout_valid(const clock_ota_layout_t *p,uint32_t size){
    return p && p->count==2u && p->linked && p->boot_partition>=0 && p->boot_partition<2 &&
        p->start[0]==CLOCK_OTA_A_START && p->start[1]==CLOCK_OTA_B_START &&
        p->end[0]==CLOCK_OTA_B_START && p->end[1]==CLOCK_OTA_B_START+CLOCK_OTA_SLOT_SIZE &&
        p->end[1]<=CLOCK_OTA_PROTECTED_START && size>0u && size<=CLOCK_OTA_SLOT_SIZE &&
        p->runtime_storage_start==p->start[p->boot_partition];
}
bool clock_ota_inactive_range(const clock_ota_layout_t *p,uint32_t offset,uint32_t length){
    if(!clock_ota_layout_valid(p,1u) || !length)return false;
    unsigned other=(unsigned)p->boot_partition^1u;
    return offset>=p->start[other] && offset<p->end[other] && length<=p->end[other]-offset;
}
