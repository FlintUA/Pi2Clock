#include <assert.h>
#ifdef _MSC_VER
#include <stdlib.h>
#endif
#include <string.h>
#include "../services/settings_store.c"
uint8_t test_flash[PICO_FLASH_SIZE_BYTES],test_flash_physical[PICO_FLASH_SIZE_BYTES];
uint8_t *test_image_end=test_flash+0x100000;
static bool layout_ok=true,write_ok;
static unsigned mutations;
void clock_ota_status(void){}
bool clock_ota_layout_verified(void){return layout_ok;}
bool clock_ota_writes_allowed(void){return write_ok;}
void flash_range_erase(uint32_t offset,size_t length){assert(offset==SLOT0_OFFSET || offset==SLOT1_OFFSET);assert(length==4096);++mutations;memset(test_flash_physical+offset,0xff,length);}
void flash_range_program(uint32_t offset,const uint8_t *data,size_t length){assert(offset==SLOT0_OFFSET || offset==SLOT1_OFFSET);assert(length<=768);++mutations;memcpy(test_flash_physical+offset,data,length);}
int flash_safe_execute(void (*cb)(void *),void *arg,unsigned timeout){(void)timeout;cb(arg);return PICO_OK;}
int main(void){
#ifdef _MSC_VER
 _set_error_mode(_OUT_TO_STDERR);_set_abort_behavior(0,_WRITE_ABORT_MSG|_CALL_REPORTFAULT);
#endif
 memset(test_flash,0xa5,sizeof(test_flash));memset(test_flash_physical,0xff,sizeof(test_flash_physical));
 assert(settings_store_blank());
 memset(test_flash_physical+LEGACY_SLOT_OFFSET,0x5a,4u*FLASH_SECTOR_SIZE);assert(!settings_store_blank());
 clock_settings_t cfg={.volume=10,.bt_volume=10,.quiet_start=22,.quiet_end=7,.timer_track=1,.timer_voice=1};
 alarm_defaults(cfg.alarms);birthday_defaults(cfg.birthdays);strcpy(cfg.wifi_ssid,"Main");strcpy(cfg.wifi_password,"main-key");strcpy(cfg.wifi_backup_ssid,"Backup");strcpy(cfg.wifi_backup_password,"backup-key");
 assert(settings_store_save(&cfg)==SETTINGS_STORE_FLASH_ERROR && !mutations);
 write_ok=true;assert(settings_store_save(&cfg)==SETTINGS_STORE_OK);
 clock_settings_t loaded;assert(settings_store_load(&loaded)==SETTINGS_STORE_OK);
 assert(!strcmp(loaded.wifi_ssid,"Main") && !strcmp(loaded.wifi_backup_password,"backup-key"));
 for(unsigned i=0;i<sizeof(test_flash);++i)assert(test_flash[i]==0xa5);
 for(unsigned i=LEGACY_SLOT_OFFSET;i<sizeof(test_flash_physical);++i)assert(test_flash_physical[i]==0x5a);
 unsigned saved=mutations;write_ok=false;cfg.volume=12;assert(settings_store_save(&cfg)==SETTINGS_STORE_FLASH_ERROR && mutations==saved);
 assert(settings_store_load(&loaded)==SETTINGS_STORE_OK && loaded.volume==10);
 layout_ok=false;assert(settings_store_load(&loaded)==SETTINGS_STORE_IMAGE_OVERLAP);
 layout_ok=true;test_image_end=test_flash+CLOCK_OTA_SLOT_SIZE+1;assert(!settings_store_layout_safe());
 puts("settings_store_ota_test: PASS");return 0;
}
