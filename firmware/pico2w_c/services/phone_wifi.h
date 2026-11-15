#pragma once
#include <stdbool.h>
#include <stdint.h>

typedef struct { char ssid[33], password[65]; } phone_wifi_config_t;
typedef enum { WIFI_SETUP_IDLE, WIFI_SETUP_PENDING, WIFI_SETUP_TESTING, WIFI_SETUP_RESTORE,
    WIFI_SETUP_SAVED, WIFI_SETUP_FAILED, WIFI_SETUP_CANCELLED, WIFI_SETUP_RECOVERY_FAILED } phone_wifi_state_t;
typedef enum { WIFI_REASON_NONE, WIFI_REASON_CANCEL, WIFI_REASON_BUSY, WIFI_REASON_TIMEOUT,
    WIFI_REASON_CHANGED, WIFI_REASON_RADIO } phone_wifi_reason_t;
typedef enum { WIFI_ACTION_NONE, WIFI_ACTION_START, WIFI_ACTION_SAVE, WIFI_ACTION_RESTORE } phone_wifi_action_t;
typedef struct {
    phone_wifi_config_t candidate; // Private; never publish the password.
    phone_wifi_state_t state;
    phone_wifi_reason_t reason;
    uint32_t epoch, request_id;
    uint64_t due_ms;
} phone_wifi_plan_t;
typedef struct {
    phone_wifi_state_t state;
    phone_wifi_reason_t reason;
    uint32_t request_id, seconds;
    bool direct, available;
    char saved_ssid[33], test_ssid[33], address[16];
} phone_wifi_view_t;
bool phone_wifi_decode(const char *text, phone_wifi_config_t *config);
bool phone_wifi_busy(const phone_wifi_plan_t *plan);
bool phone_wifi_schedule(phone_wifi_plan_t *plan, const phone_wifi_config_t *config,
    uint32_t epoch, uint32_t id, uint64_t now);
void phone_wifi_cancel(phone_wifi_plan_t *plan, phone_wifi_reason_t reason);
phone_wifi_action_t phone_wifi_step(phone_wifi_plan_t *plan, uint64_t now, bool idle,
    bool direct, uint32_t epoch, bool home_ready);
void phone_wifi_recovered(phone_wifi_plan_t *plan, bool success);
void phone_wifi_clear_secret(phone_wifi_plan_t *plan);
const char *phone_wifi_state_name(phone_wifi_state_t state);
const char *phone_wifi_reason_name(phone_wifi_reason_t reason);
