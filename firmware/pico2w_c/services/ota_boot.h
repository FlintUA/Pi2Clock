#pragma once
#include <stdbool.h>
#include "ota_layout.h"
void clock_ota_boot_init(void);
bool clock_ota_layout_verified(void);
bool clock_ota_writes_allowed(void);
bool clock_ota_get_layout(clock_ota_layout_t *out);
bool clock_ota_startup_confirm(bool healthy);
void clock_ota_status(void);
// Trial reboot; the inactive image must first be verified by the installer/uploader.
bool clock_ota_trial_inactive(bool idle);
