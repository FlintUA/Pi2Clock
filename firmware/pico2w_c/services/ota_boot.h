#pragma once
#include <stdbool.h>
void clock_ota_boot_init(void);
bool clock_ota_layout_verified(void);
bool clock_ota_writes_allowed(void);
bool clock_ota_startup_confirm(bool healthy);
void clock_ota_status(void);
// Serial-only bring-up command; the inactive image must first be verified off-device.
bool clock_ota_trial_inactive(bool idle);
