#pragma once
#include <stdint.h>
typedef struct {volatile uint32_t scratch[8];volatile uint32_t boot[4];} clock_test_powman_t;
extern clock_test_powman_t clock_test_powman;
#define powman_hw (&clock_test_powman)
