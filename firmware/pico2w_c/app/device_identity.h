#pragma once
// Hardware family, independent of the firmware release and ordered OTA sequence.
// Preserve G1's original target value so existing OTA receivers can bootstrap.
// Reserve 0x23500202 for G2; never reuse G1's target for different audio hardware.
#define CLOCK_DEVICE_MODEL "Pi2Clock G1"
#define CLOCK_DEVICE_GENERATION "G1"
#define CLOCK_DEVICE_BUILD_PREFIX "g1-"
#define CLOCK_DEVICE_OTA_TARGET 0x23500002u
