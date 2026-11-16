# OTA feasibility assessment - 2026-11-16

Status: feasible on the existing Pico 2 W. The opt-in [A/B foundation](OTA_FOUNDATION.md) subsequently passed separately approved device gates on November 16; the [browser uploader](OTA_WEB_UPDATE.md) is an uninstalled candidate. This is an assessment, not an OTA implementation or installation approval. The device, COM8, firmware sources, settings, OTP and installed partitioning were not modified by this assessment.

## Decision

Use the RP2350 bootrom's A/B application partitions and Try Before You Buy (TBYB), rather than overwriting the running application or depending on the SD card as the only recovery copy. Keep the CYW43 firmware embedded in each application for the first implementation: the current complete image fits easily, so separate radio-firmware partitions add unnecessary first-stage complexity. A custom first-stage bootloader is not required for the basic boot selection/rollback mechanism; the built-in ROM provides it.

First migration requires a separately approved USB installation with a reviewed partition table and partition-compatible application. Subsequent updates can be uploaded through the existing authenticated local web interface in either Home or Direct. Internet access and hardware replacement are not required by this design. Real Home/Direct OTA transport has not been implemented or measured yet.

## Measured current build

Source: 644cfffc093566d64dbc491826475059b2e6da9d, 1.0.0+46.g644cfff, bt-mp3-wifi-phone. Installed SDK and picotool: 2.3.1.

| Item | Measured value |
| --- | --- |
| Board Flash | 4,194,304 bytes / 4 MiB, consistent with prior flash-info and SDK board definition |
| Raw .bin | 984,892 bytes / 961.81 KiB |
| UF2 container | 1,970,688 bytes; its size is not the application Flash requirement |
| ELF virtual image end | 0x100f073c |
| Main SRAM allocation end | 0x2002b7f4 |
| Main SRAM heap ceiling | 0x20080000 |
| Unoccupied linker span between those addresses | 346,124 bytes / 338.01 KiB, before runtime allocations; NOT measured free/peak RAM |
| Main stack | 4096 bytes in SCRATCH_Y |
| Web lwIP MEM_SIZE configuration | 49,152 bytes; runtime allocation/resource margin remains unmeasured |

The official example uses a 2048-byte receive buffer plus a 4096-byte ROM work area and additional TCP/hash state. Bounded streaming avoids keeping the roughly 1 MiB application in RAM. A preliminary incremental-buffer target around 8-16 KiB is a design estimate, not measured integration cost. Pause music/Bluetooth activity during update and serialize the upload/flash operations; real memory and radio timing must be measured on the assembled clock.

## Offline partition validation

An assessment-only JSON and UF2 were generated in C:/pico_clock_compile/ota-feasibility. picotool partition create and picotool info -m accepted the table, A/B linkage and hash. No device load, reboot or erase command was issued.

| Physical storage interval, end exclusive | Purpose |
| --- | --- |
| 0x000000..0x001000 | Boot partition-table area |
| 0x001000..0x181000 | Application A, 1536 KiB |
| 0x181000..0x301000 | Application B, 1536 KiB, linked to A |
| 0x301000..0x3fa000 | 996 KiB spare/reserved growth area |
| 0x3fa000..0x3fc000 | Existing clock settings A/B sectors |
| 0x3fc000..0x3fd000 | Existing read-only legacy settings sector |
| 0x3fd000..0x3ff000 | Existing SDK Bluetooth banks |
| 0x3ff000..0x400000 | Existing reserved RP2350-E10 workaround sector |

Each application slot has 587,972 bytes / 574.19 KiB beyond the current raw image. The draft retains the default picotool BTstack compatibility check. Table hash: 55735F751BF7215D6A31D5B4940A8EF4F43D129C9B67342A591C4599772DB8F4.

This proves format validity and non-overlap at the file level, not bootability, address-translation correctness or power-loss safety on the device. Draft permissions are not a finalized production access policy. Never install the draft table on its own over the existing image: the current application begins at physical zero and is not partition-ready.

## Existing support and necessary adaptation

1. The installed official pico-examples/pico_w/wifi/ota_update demonstrates inactive-partition reception, hashing, ROM update reboot and TBYB. Its default split radio-firmware layout is not needed for the proposed initial monolithic clock design. Its TCP port-4242 demonstration is not a browser upload or a production parser; do not copy it unchanged.
2. SDK 2.3.1 exposes rom_get_uf2_target_partition, rom_flash_op and rom_explicit_buy. Flash-mutating wrappers use flash_safe_execute. Strictly check every erase/program/read/hash result and restrict all upload writes to the inactive application partition.
3. settings_store.c currently reads settings and the reserved tail through XIP_BASE + physical offset. A/B boot uses QMI address translation. Those physical-storage reads must use the RP2350 untranslated window, as the SDK BTstack driver already does using XIP_NOCACHE_NOALLOC_NOTRANSLATE_BASE. Keep the physical tail offsets, A/B CRC/ownership rules and current settings versions intact. The current image guard must additionally enforce the active partition limit, rather than only the whole-Flash settings boundary.
4. Current image metadata is ARM Secure, without TBYB or a numeric image version. Add partition-compatible packaging, image integrity checking, an internal ordered boot-image version and trial confirmation. Preserve the Git-derived display version; its text alone is not bootrom version-selection metadata.
5. TBYB allows about 16.7 seconds for explicit acceptance. Confirm after bounded local startup checks and main-loop progress, without waiting for a router, Bluetooth speaker or NTP server. The existing 3-second serial startup delay consumes part of that budget. Delay settings migration/autosave and other persistent mutations until trial acceptance, so rollback does not encounter incompatible new records. Long-term health checks after acceptance are separate from the initial ROM trial.
6. Current USB UF2 contains an absolute-address RP2350 workaround block in addition to application-family blocks. An OTA receiver must not blindly apply arbitrary UF2 addresses. Generate/validate an OTA-specific artifact or deliberately handle that packaging while denying partition-table/settings/Bluetooth/reserved-region writes.
7. The updater and build/review checks need partition-aware image/build verification. Preserve physical BOOTSEL USB recovery and prepare a compatible rollback artifact before migration. Do not assume an old ordinary USB image can be safely used unchanged after adopting the new layout.
8. Existing HTTP POST command bodies are bounded to 288 bytes. Add a separate authenticated streaming upload path, bounded buffers, ordering/length/target/chip/version/hash validation, progress and restart/status handling. Reuse the local access and same-origin protections. Accept one update at a time; block conflicting settings/audio/network-mode actions while it is committed. Download the full candidate and validate it before initiating a trial boot; never erase the running slot.

## Failure model

- Broken upload or power loss while writing inactive storage must leave the active image bootable.
- A malformed, wrong-target, too-large or corrupt package must not start a trial or write shared data.
- An invalid or unaccepted trial image should fall back through ROM TBYB behavior. Verify interrupted acceptance, not just an application watchdog reboot.
- Settings-format compatibility is distinct from application rollback. Keep trial firmware from changing shared records before it is accepted; later schema changes require an explicit backward-compatibility plan.
- A successful explicit acceptance is not proof of indefinite runtime correctness. TBYB is a bounded startup safeguard, not a complete long-term application-health monitor.

## Implementation order and acceptance gates

1. Review a concrete OTA specification and migration/rollback package, preserving all protected sectors.
2. Implement partition-aware storage access and guards; exercise builds and tests without writing hardware.
3. In a separately approved USB experiment, prove boot A, boot B and TBYB acceptance/rollback with retained settings and Bluetooth pairing data. Keep a reviewed USB recovery image.
4. Add the authenticated bounded uploader, first with failure-injection/host parser tests, then Home and Direct device uploads.
5. Add the final About > Firmware update UI: artifact selection, version/result, progress, confirmation and reconnection instructions.
6. Test wrong/corrupt/truncated input, Wi-Fi interruption, interrupted power at write/trial/acceptance, settings preservation, low-memory/refused-busy cases and recovery through BOOTSEL. Hardware tests remain unperformed.

## Sources

- [Official Pico 2 W OTA example](https://github.com/raspberrypi/pico-examples/tree/master/pico_w/wifi/ota_update) - installed copy inspected and online primary source checked.
- [OTA example explanation](https://github.com/raspberrypi/pico-examples/blob/master/pico_w/wifi/ota_update/README.md) - A/B operation and TBYB.
- [Pico SDK runtime/bootrom documentation](https://www.raspberrypi.com/documentation/pico-sdk/runtime.html) - flash operations, partition selection and explicit acceptance.
- Installed SDK sources: pico_bootrom/include/pico/bootrom.h, pico_btstack/btstack_flash_bank.c, RP2350 addressmap.h; project settings_store.c, CMakeLists.txt, current ELF map/bin/UF2 and picotool file metadata.
