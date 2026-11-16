#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
// Submit runs in lwIP context. Flash operations run only in service on core 0.
bool phone_ota_submit(const char *body,const char *owner,uint32_t epoch);
void phone_ota_service(bool idle,uint64_t now,uint32_t epoch);
bool phone_ota_busy(void);
int phone_ota_json(char *out,size_t size);
