# Browser firmware update candidate

Status: Home and Direct uploads have installed accepted images through sequence 8. The user accepted the sequence-7 restart/sound/timer gate, then installed sequence 8 through the phone Direct workflow and cycled power. Read-only inspection confirmed accepted A sequence 8 in Home afterward. Immediate Direct restoration before that power cycle was not independently observed. The sequence-9 upload-feedback/boot-diagnostics candidate is not installed. Thirty-three host checks pass.

## Network mode after restart

**Sequence 6 and earlier (legacy behavior):** every normal restart or full power-on starts in **Home Wi-Fi**. This also applies to **Install and restart**, even if the update was uploaded through **Direct**. SpeakingClock disappears when the clock restarts. Rejoin the home network on the phone, then open the clock home address shown in Phone Control. This was the observed sequence-6 behavior, not a failed Direct upload. Saved Direct Wi-Fi passwords and browser permissions are retained.

The user confirmed the requested sequence-6 restart/sound/timer checks on 2026-11-19. General function is accepted; focused failure cases remain separate.

**Installed sequence-7/8 support (immediate Direct restoration still unconfirmed):** a browser OTA sent from a supporting firmware asks the newly accepted image to restore the same network mode once. Direct OTA returns to SpeakingClock/192.168.4.1; Home OTA returns Home. An ordinary power-on/restart still uses Home. If the phone switches networks during the restart, rejoin SpeakingClock manually. If Direct startup fails, the clock keeps its existing Home fallback. Rollback does not promise a Direct connection.

Both the sending and receiving firmware must support this handoff. Installed sequence 6 cannot send it. The first update from sequence 6 therefore still starts Home; only a subsequent update from the supporting candidate can exercise Direct restoration. The receiving/sending bootstrap sequence 7 was installed through Home and accepted in B. The subsequent sequence-8 phone test was followed by a power cycle before independent observation, so the immediate Direct-restoration gate remains open. The next observed test must precede any power cycle.

The one-shot marker uses application-owned POWMAN scratch 0..3, commits its magic last, checks target partition/ordered sequence/checksum and requires a pending ROM Flash Update boot. It is consumed before layout/health acceptance; failed, stale, corrupt, wrong-slot or ordinary boots cannot request Direct. The saved settings layout, Flash record v18 and sectors do not change. Watchdog scratch reboot parameters, POWMAN BOOT vectors and SDK low-power scratch 6..7 are untouched. ROM behavior follows the [official reboot implementation](https://github.com/raspberrypi/pico-bootrom-rp2350/blob/master/src/main/arm/varm_apis.c); POWMAN register ownership was checked against the installed SDK 2.3.1 register/low-power sources. Actual retention and restoration across the ROM trial remain unverified on this board.

## User workflow

1. Connect through the existing Home or Direct web interface with ordinary browser admission. Stop playback/timers, disconnect Bluetooth, close physical editors and wait for settings to save.
2. Open **Firmware update**, select a compatible `.clockota` file and press **Upload update**. The page shows its build and progress. Uploading does not restart the clock.
3. After the device validates the complete file, press **Install and restart**, or cancel to keep the current firmware. Confirm the restart. The browser reconnects and compares the running build with the selected build; a different build is reported as a possible rollback, not success.
4. Verify ordinary operation and a full power restart. USB BOOTSEL remains the recovery path.

During an active upload, verification, ready-to-install state and restart, physical/application commands, autosave and scheduled sounds are paused. The LCD shows Firmware update / Use web browser. Do not start an update when an imminent alarm is needed. The RTC hardware continues keeping time. Idle receiving/ready sessions automatically cancel after 120 seconds without progress. Interrupted transfers are not automatically resumed; cancel/retry instead. A power cut while writing the inactive image must leave the accepted running slot available; this still needs physical fault testing.

## Bounded transport and access

`POST /ota` uses the existing exact Host/Origin validation and Home/Direct browser admission. Its body is ASCII:

```text
credential epoch action session offset hex-data-or-minus
```

The credential is the remembered browser token, or `-` for a verified peer admitted by trusted Home policy. Epoch prevents requests from an earlier boot. Begin reserves one upload before other HTTP commands can enter. A session is bound to its credential and epoch; another remembered browser cannot send chunks, cancel or apply it. Trusted Home peers share that policy identity. Other application POST commands are blocked, except read-only browser access checks. There is one bounded mailbox; Flash operations never run inside lwIP callbacks or while its lock is held.

Actions are begin (128-byte package header), chunk (at most 512 bytes, strictly ordered offset), finish, cancel and apply. Bodies are at most 1199 bytes; ordinary command bodies retain their previous 287-byte limit. Four bounded POST contexts remain, but only one update session is admitted. A duplicate/out-of-order chunk never programs Flash twice. `/ota.json` publishes non-secret state/progress; it is not an authorization endpoint. The page waits for device progress after every chunk. No settings/partition addresses supplied by the client are used.

Before erasing, the service requires an idle application, saved settings, no Wi-Fi transition/scan and no active A2DP stream. Each ROM Flash operation rechecks the actual inactive partition and uses physical storage addressing, including when executing in B. Only 4 KiB sectors in that inactive application region can be erased/programmed. Sector programming is read back. Table, active application and shared settings/BT tail are excluded.

The first candidate sector is erased at begin, retained in RAM during transfer and committed only after complete validation. Remaining sectors are streamed through a single 4 KiB buffer. Final validation hashes the RAM first sector plus physical stored payload and requires the reviewed monolithic RP2350 ARM Secure/TBYB metadata, matching ordered ROM version and a closed metadata loop. The ROM performs its own embedded image validation on the subsequent explicit trial reboot. Strictly newer sequences are required; browser downgrades are refused. Hashes detect corruption; this format does not provide publisher signatures or internet-grade transport security. Use the existing local access policy, not port forwarding.

The two 4 KiB sector buffers, bounded POST contexts and mailbox add 12680 bytes (12.4 KiB) of BSS in the measured candidate build, plus about 14.3 KiB of linked code/data. The candidate ELF reports 185196 bytes BSS versus 172516 for the foundation. These are build measurements; peak live network/Flash RAM and timings remain hardware checks. No whole-image RAM allocation or SD staging is used.

## Package and ordered versions

`.clockota` is slot independent: a 128-byte little-endian header followed by the exact monolithic `.bin` bytes. Header fields:

| Offset | Field |
| --- | --- |
| 0..7 | `CLOCKOT1` |
| 8..11 | Pico 2 W target `0x23500002` |
| 12..15 | Payload byte length, 4096..1536 KiB |
| 16..19 | Ordered ROM minor version, 1..65535 |
| 20..23 | Format flags, exactly 1 (trial) |
| 24..55 | Payload SHA-256 |
| 56..119 | NUL-terminated printable build ID, at most 63 bytes |
| 120..127 | Reserved zero bytes |

Build on a clean committed source revision with `-OtaAb -OtaTrial -OtaSequence N`. The sequence must exceed every deployed accepted sequence; do not recycle the bring-up values. The candidate receiver uses sequence 4 after foundation 1/2 and reject-test 3. A subsequent transport test must use sequence 5 or higher.

```powershell
.\build-clock-bt.ps1 -Mp3 -PhoneWeb -OtaAb -OtaTrial -OtaSequence 5 -HelixPath C:\pico_clock_compile\third_party\Helix-MP3-Decoder -BuildDirectory C:\pico_clock_compile\ota-web-next
python .\tools\ota_web_package.py --build C:\pico_clock_compile\ota-web-next --picotool C:\Users\Flint123\.pico-sdk\picotool\2.3.1\picotool\picotool.exe --output C:\pico_clock_compile\ota-web-next\clock-ota5.clockota
```

Packaging refuses dirty/reject/non-trial builds, wrong ROM version, invalid image hashes, oversize payloads and overwriting an existing artifact. Its review JSON records build, sequence and hashes. Ordinary `.uf2` files and foundation absolute-address files are not browser-update inputs.

## Installation and pending acceptance

The foundation sequence-2 image did not contain this uploader. A separately approved USB installation of edc486e394bf-bt-mp3-wifi-phone-ota4-trial into A succeeded, followed by explicit trial acceptance and settings comparison. The user confirmed operation after the requested power restart; read-only serial/HTTP inspection confirmed accepted A and the idle uploader. No table rewrite occurred. The first approved Home transfer subsequently installed sequence 5 into B. Future changes must still use separate installation approval and stop for user testing.

## First Home transport evidence - 2026-11-16

The operator supplied a physical pairing code for the test client; no Home-trust policy was changed. The additional authorized Home entry was saved before the comparison baseline. A PC HTTP client exercised the production /ota endpoints with ordinary token/epoch and exact Origin checks; it did not drive a phone browser's file picker or progress widget.

The reviewed clock-ota5.clockota package contained 1000588 payload bytes (1000716 bytes including the header), SHA-256 2198c7c422b46e86416cea679d95e3984c2811e2632650f152cbd91d6bdf0111. Begin/chunk/finish over Home reached ready in 87.191 seconds; all 512-byte chunks were acknowledged, physical sector readback and final SHA/metadata verification succeeded. A remained active until the separate apply request. Apply over HTTP initiated the trial; serial showed build edc486e394bf-bt-mp3-wifi-phone-ota5-trial, active=B trial=NO accepted=YES writes=YES upload=WEB and continued beyond 30 seconds. Display version remains 1.0.0+48.gedc486e because sequences 4 and 5 deliberately use the same source revision; the build ID and ordered ROM version distinguish them.

The serial recording observed automatic Wi-Fi retry attempts before reconnection; subsequent HTTP and NTP checks succeeded. Separately, the user reported access restored about ten seconds after boot. This is a user observation, not a measured upper bound for all network conditions.

Five alarms, fifteen birthdays, four saved speakers, both Wi-Fi profiles, admitted browser entries/Home policy, language, routing and display preferences matched. The boot log loaded the original local volume 15; the later snapshot showed 13 and one new Flash settings record. The user explicitly confirmed adjusting the physical volume encoder after reboot. This is an expected runtime change, not an unchanged-Flash claim. Bluetooth volume remained 15. COM8 was released after inspection. Private credentials and detailed snapshots remain off-repository.

Pending physical checks: Direct transport, interrupted transfers, cancellation, wrong file/version/hash, concurrent admission, actual phone-browser picker/progress/reconnect/rollback feedback, peak live memory, power loss during upload/commit and browser-update rollback. The successful Home HTTP test does not establish these cases.

ROM storage/translation, Flash permission checks and explicit-buy behavior follow the [official SDK runtime documentation](https://www.raspberrypi.com/documentation/pico-sdk/runtime.html).


## Phone Direct workflow evidence - 2026-11-19

The repository was renamed to FlintUA/Pi2Clock. A clean sequence-6 trial package was built from c3440d9cb6d1; its display version is 1.0.0+51.gc3440d9. The reviewed clock-ota6.clockota file contains 1000716 bytes, SHA-256 bf8415b1c366d0207ee694558abe52b4d4fb92edecfeb76d423f7cf5ee654993. The phone first downloaded the file through the home LAN and stored it on its SD card. The user switched the clock to Direct, joined SpeakingClock, opened 192.168.4.1, selected/uploaded the file and performed Install and restart. The user reported success.

Read-only serial/HTTP inspection then confirmed c3440d9cb6d1-bt-mp3-wifi-phone-ota6-trial, layout=OK active=A trial=NO accepted=YES writes=YES upload=WEB, Flash guard=OK and idle sequence 6. The clock returned to Home at 192.168.2.116 and synchronized NTP. COM8 was released. This proves the normal phone selection/upload/install path through Direct; transfer duration and detailed progress rendering were not measured.

Five alarms, fifteen birthdays, both Wi-Fi profiles and admitted browser entries matched the November 16 snapshot. Scalar differences from that older snapshot were local volume 13 to 15 and Bluetooth volume 15 to 4. No immediate pre-Direct full preferences snapshot was captured, so those differences cannot be attributed to the update and this test does not claim exact volume preservation. Existing saved speaker entries were readable.

Pending: network-return candidate acceptance, interrupted/cancelled/corrupt transfers, concurrent admission, power loss during upload/commit, peak memory and rollback/reconnection feedback in a browser. No failure-case acceptance follows from this successful normal-path test.


## Sequence-7 bootstrap installation - 2026-11-19

After separate approval, clock-ota7.clockota (1003436 bytes; SHA-256 370855a6b620980f0bb93f6f3d25f04fbdd082d66886b63798edfdf6679d87dd) was uploaded through the existing Home HTTP service into inactive B. Transfer reached ready in 67.248 seconds, then apply requested the trial. Serial confirmed version 1.0.0+53.gb1dd2c3, build b1dd2c31fc0d-bt-mp3-wifi-phone-ota7-trial, accepted B and continued operation beyond 30 seconds. It returned Home as expected because the sending sequence-6 image does not arm network context. Home connected on attempt 1 and NTP synchronized.

Immediate pre/post comparison matched scalar preferences (including local volume 15 and Bluetooth volume 4), alarms, birthdays, saved speakers, both Wi-Fi profiles, browser entries/Home policy and both Flash settings record sequences. Guard was OK. HTTP reported idle sequence 7, mode_restore=true and restart_mode=home; the network hint was present in served HTML. COM8 was released. This establishes the bootstrap installation and Home behavior, not a successful Direct handoff. The user subsequently confirmed the requested full-power, sound and timer checks; serial/HTTP inspection verified accepted B sequence 7, guard=OK and idle Home mode. The separately approved sequence-8 Direct restoration test remains pending.


## Sequence-8 phone report and upload-feedback candidate - 2026-11-19

The user reported selecting/uploading clock-ota8.clockota from the phone through Direct, installing and restarting, and then cycling power. Subsequent read-only serial inspection confirmed b1dd2c31fc0d-bt-mp3-wifi-phone-ota8-trial, accepted A sequence 8 and guard=OK; the clock was Home with working NTP. Home after the later power cycle is expected. No independent observation was captured between OTA restart and that power cycle, so this result does not yet close the immediate Direct-restoration gate. COM8 was released. Saved alarms, birthdays and speakers were readable; an exact immediate pre-OTA preferences baseline was not captured for this manual test.

The user also reported an unexplained pause after Upload and uncertainty about whether another Upload was required after verification. The source previously supplied its first transfer message only after the first chunk acknowledgement, leaving begin/file-reading/verification waits unclear. The exact cause of the reported delay/retry is not established by the transcript. A new uninstalled sequence-9 candidate adds immediate file-reading/preparation/upload/verification messages, a bounded acknowledgement wait, explicit install guidance and a hidden/disabled Upload in ready state, even if an available flag is stale. Already-installed files cannot be uploaded again after reconnection. Network uncertainty keeps Upload disabled until fresh status is received. Completion feedback persists rather than disappearing at the next poll.

The candidate also records non-secret boot handoff diagnostics in serial ota-status: [OTA-NET] boot_type, validation check mask and direct_intent. Check-mask bits 0..5 represent magic, target slot, ordered sequence, checksum, Flash Update boot and pending trial. These observations survive consumption of the one-shot within the current running image; a subsequent power cycle creates a new observation. The restoration policy itself is unchanged. A separately approved next Direct test should be observed before cycling power.


### Upload-button layout follow-up

The user's phone screenshot showed the sequence-7 Direct page with a full progress bar and Update stopped: timeout. This confirms that the captured session had expired; active Upload and disabled Install are consistent with expiry, not a ready-to-install state. It does not establish the cause of the initial unreported delay. The same screenshot showed the third action touching the preceding row: the OTA section used an unstyled actions wrapper, unlike the existing form action groups.

The revised, still-uninstalled ota9 candidate uses a dedicated firmware-actions layout. At widths up to 34 rem, buttons form a full-width vertical stack; wider views use an evenly spaced flexible row. Both directions use a 0.75 rem gap and buttons have a 3 rem minimum height. The enabled primary action is filled, while Cancel remains secondary. Existing hidden-state behavior remains authoritative. Actual-CSS browser previews at 320, 393 and 640 px showed 48 px minimum button height and 12 px gaps, with no touching buttons. These static previews validate geometry, not device installation or Android acceptance. The earlier ota9 artifact remains a reviewed archive; the combined replacement is prepared in a separate output directory and still requires installation approval.
