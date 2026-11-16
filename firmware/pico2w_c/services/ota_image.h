#pragma once
#include <stdbool.h>
#include <stdint.h>
bool ota_image_block(const uint8_t *block,uint32_t bytes,uint32_t sequence,uint32_t *next);
