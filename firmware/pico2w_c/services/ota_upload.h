#pragma once
#include "ota_layout.h"
#include <stddef.h>
#define OTA_HEADER_SIZE 128u
#define OTA_CHUNK_SIZE 512u
typedef enum { OTA_IDLE, OTA_RECEIVING, OTA_READY, OTA_REBOOTING, OTA_ERROR } ota_upload_state_t;
typedef struct {
    bool (*erase)(uint32_t offset);
    bool (*program)(uint32_t offset,const uint8_t *data);
    bool (*validate)(uint32_t offset,uint32_t size,const uint8_t *first,const uint8_t *header);
    bool (*reboot)(void);
} ota_upload_ops_t;
typedef struct {
    ota_upload_state_t state;
    const char *error;
    uint32_t session,size,received,target,sequence;
    uint64_t touched;
    uint8_t header[OTA_HEADER_SIZE];
    uint8_t first[4096],sector[4096];
    clock_ota_layout_t layout;
    ota_upload_ops_t ops;
} ota_upload_t;
bool ota_upload_header(const uint8_t *header,uint32_t current,uint32_t *size,uint32_t *sequence);
bool ota_upload_begin(ota_upload_t *u,const clock_ota_layout_t *layout,ota_upload_ops_t ops,
                      const uint8_t *header,uint32_t current,uint32_t session,uint64_t now);
bool ota_upload_chunk(ota_upload_t *u,uint32_t session,uint32_t offset,const uint8_t *data,size_t size,uint64_t now);
bool ota_upload_finish(ota_upload_t *u,uint32_t session,uint64_t now);
bool ota_upload_cancel(ota_upload_t *u,uint32_t session);
bool ota_upload_apply(ota_upload_t *u,uint32_t session);
void ota_upload_tick(ota_upload_t *u,uint64_t now);
bool ota_upload_busy(const ota_upload_t *u);
