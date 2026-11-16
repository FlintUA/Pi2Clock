# OTA foundation - A/B bring-up stage

Status: initial migration, deliberate-rejection rollback and successful acceptance into B were installed with separate approvals on 2026-11-16. The user accepted ordinary operation after each gate and reported success after the requested power-cycle check; serial inspection then confirmed accepted B. Browser upload is a new [uninstalled candidate](OTA_WEB_UPDATE.md), separate from this foundation evidence.

## Scope and invariants

The opt-in CLOCK_ENABLE_OTA_AB build uses the [reviewed layout](OTA_FEASIBILITY.md): table in sector 0, 1536 KiB application A at physical 0x001000, 1536 KiB B at 0x181000, and all six existing tail sectors preserved at 0x3fa000..0x400000. It requires pico2_w, rp2350-arm-s and the phone-web profile. Ordinary profiles keep their previous layout and storage behavior.

The boot adapter checks the resident ROM table hash through the ROM query API, table presence/count, exact A/B locations/size/linkage, booted partition and runtime-to-storage translation. Invalid layout means no configuration writes or trial activation. An additional linker assertion and package size checks reject images exceeding one slot. The receiver write-range policy can only select the inactive application region, never the table/current image/shared tail.

OTA builds read saved settings and the reserved tail through XIP_NOCACHE_NOALLOC_NOTRANSLATE_BASE. SDK 2.3.1 already uses this physical-read window for Bluetooth banks. Settings CRC, record v18, legacy ownership protection and physical tail offsets are unchanged. No data migration or OTP configuration is introduced.

## Trial acceptance

Initial images have ordered ROM version 1.1 without TBYB. Acceptance-test images have version 1.2 with TBYB. Deliberate-rejection images have version 1.3 with TBYB and a compile-time test refusal. These fixed numbers are for the first bring-up package only; subsequent production OTA will require a monotonic release sequence. Git-derived display/build identity remains separate and includes -otaN/-trial/-reject qualifiers.

For a pending trial, the first application event-loop checkpoint requires the verified layout, radio initialization and a readable settings record (or genuinely empty storage). SD-card/catalog operations, Bluetooth initialization and application settings writes are deferred until that checkpoint. Configuration writes and mutating serial commands are refused until acceptance; read-only ota-status/flash-info/version and the existing guarded BOOTSEL entry remain available. A pending trial calls rom_explicit_buy with an aligned 4 KiB work area only after those checks. Any ROM error keeps writes disabled. No router, NTP server, SD card or speaker is required to pass the local checkpoint.

An image that is already accepted continues ordinary offline clock operation if the radio is unavailable; local health refusal applies to a pending trial. Unknown/corrupt records are not treated as genuinely erased storage.

The reject-test build intentionally never confirms a trial. RP2350 ROM TBYB is expected to reboot and select the previous accepted image after its watchdog interval. This behavior is NOT yet verified on this clock. The checkpoint demonstrates local startup, not every late-running feature; acceptance does not establish long-term health. No clock settings/schema write occurs before it; Bluetooth key storage starts afterward.

## Build and package

On a clean committed checkout:

```powershell
.\build-ota-foundation.ps1 -OutputDirectory C:\pico_clock_compile\ota-foundation -HelixPath C:\pico_clock_compile\third_party\Helix-MP3-Decoder
```

This command builds three variants and only creates files. It never opens a COM port, loads an image or changes OTP. The packager checks clean and matching Git identities, ordered versions, ROM metadata versions, ARM Secure image type, TBYB flags, image/table hashes, per-slot bounds, UF2 family, count/order and every write address.

The package directory contains:

- partitions.uf2 and its parsed metadata/hash.
- initial-a.uf2, the first non-trial application at physical A.
- accepted-a.uf2 / accepted-b.uf2, the same trial executable packaged for either inactive slot.
- rejected-a.uf2 / rejected-b.uf2, a deliberately unaccepted trial for either inactive slot.
- manifest.json with identities, versions, roles, lengths, slot limits and SHA-256 fingerprints.

These are explicit physical-address bring-up files, not normal OTA-upload files and not interchangeable with the ordinary updater's single-image input. Never concatenate the table and application and assume the currently running BOOTSEL session has already reloaded a new partition table. Never write an accepted/rejected image to the active slot. No automatic installer is provided at this gate. The ordinary updater refuses a running image whose flash-info includes OTA A/B status; an already-BOOTSEL board still requires explicit operator inspection and the documented partition-aware procedure. Never bypass that procedure by dragging an ordinary image onto an A/B device.

## Separately approved initial USB migration

The operator must use a single identified Pico 2 W and abort on ambiguous device identity. Verify package hashes and retain a reviewed ordinary recovery image before any device writes. Close browser/serial activity and wait for audio/timers, editors and settings autosave to be idle.

1. Capture version, flash-info, all scalar settings, alarms, birthdays, speakers, network profiles and browser permissions while the original image is running. Do not expose passwords.
2. Enter BOOTSEL using existing bootsel arm/confirm. Verify RP2350 identity. Read the full 4 MiB Flash to a private off-repository BIN backup with readback verification; stop if backup/driver access fails. This backup contains credentials and must not be published.
3. Load/verify only partitions.uf2 using absolute addressing. Reboot to BOOTSEL again so ROM reloads the table. Inspect the resident table and verify the exact expected ranges and shared tail.
4. Load/verify initial-a.uf2 with explicit physical addressing and reboot normally. Never erase all Flash. Check ota-status reports layout=OK active=A trial=NO accepted=YES writes=YES, matching version/build, Flash guard and prior settings/network/browser/speaker data.
5. Stop for user testing. No trial activation or browser updater is implied by approving this first migration.

Relevant picotool 2.3.1 operations, shown as operator references rather than an unattended script:

```text
picotool save -r 0x10000000 0x10400000 -v <private-backup.bin> -t bin
picotool load --ignore-partitions -v <package/partitions.uf2>
picotool reboot -u
picotool partition info
picotool load --ignore-partitions -v <package/initial-a.uf2>
picotool reboot
```

Do not run these commands until the matching stage is explicitly approved and the backup is verified. USB driver availability on the actual host is checked at that gate. In a failure, physical BOOTSEL remains the recovery entry; a reviewed full backup can restore the previous byte layout with an absolute-address, verified BIN load. An ordinary unqualified UF2 load after partitioning may be routed to an app partition and is not a full-layout rollback.

## Next separately approved A/B tests

After initial A is accepted, prove rollback first: load rejected-b.uf2 to inactive B, reboot normally into the accepted application, issue ota-trial arm then ota-trial confirm within 15 seconds, and observe return to A without acceptance. No settings mutation should occur. Then replace inactive B with accepted-b.uf2 and prove acceptance into B, retained data and a cold restart from B. A later rejection test from B must use rejected-a.uf2, never overwrite active B.

The serial arm/confirm path requires an idle, accepted application and saved settings. It invokes only a ROM trial reboot to the inactive physical slot; ROM performs boot validation. Loading an inactive file, triggering a trial and each subsequent test need their own concrete review/approval. A normal reboot is not a substitute for the explicit FLASH_UPDATE trial request.

## Software verification

Thirty registered checks pass, including new partition/range tests, real boot-adapter tests with mocked ROM responses and errors, physical-versus-translated settings tests, trial write blocking and Python packaging/header/identity tests. The existing tests still cover v1-v18 records, alarms, birthdays, audio control and browser workflow. SDK builds cover ordinary, initial, TBYB-accept and TBYB-reject profiles. picotool verifies embedded image hashes, versions and trial attributes; file-only parsing verifies package address bounds.

Device evidence on 2026-11-16: a private full 4 MiB Flash backup was saved twice, readback-verified and SHA-256 matched before migration. Initial A booted with layout=OK/guard=OK. The deliberate-rejection B reported trial=YES accepted=NO writes=NO, then automatically returned to A about 24 seconds after the request. The corrected B was explicitly accepted and stayed active beyond that interval. Pre/post serial and HTTP comparisons preserved scalar settings, five alarms, fifteen birthdays, four saved speakers, two Wi-Fi profiles, browser entries and Home policy. The user confirmed ordinary operation after each stage. After the requested user power-cycle test, serial reported layout=OK active=B trial=NO accepted=YES writes=YES. The installed build is b7adb188bc4d-bt-mp3-wifi-phone-ota2-trial, version 1.0.0+47.gb7adb18; its historical upload status remains NOT_IMPLEMENTED. Private backups and logs are off-repository and contain no published credentials.

Not yet verified: rollback in the opposite direction after accepting B, power interruption during installation/trial, peak runtime RAM and authenticated Home/Direct upload. No additional hardware acceptance is inferred from host tests.

## Follow-up after the boot gate

Implement the bounded authenticated inactive-slot upload service and browser Firmware update UI, with manifest/hash/target/version validation, one upload at a time, conflicting-operation guards, progress/cancellation/reconnection and failure injection. Retain USB recovery. Only after the A/B boot gate is physically accepted should the Wi-Fi upload path be enabled.
