#pragma once
#include <stdint.h>
extern uint8_t test_flash[];
#define XIP_BASE ((uintptr_t)test_flash)

#ifdef CLOCK_ENABLE_OTA_AB
extern uint8_t test_flash_physical[];
#define XIP_NOCACHE_NOALLOC_NOTRANSLATE_BASE ((uintptr_t)test_flash_physical)
#endif
