# Browser firmware update candidate

Status: receiver sequence 4 was installed and user-accepted after the requested power-cycle check on 2026-11-16. The first separately approved Home HTTP update to sequence 5 then passed transfer, device validation, explicit activation, accepted B startup and settings comparison. The user reported restored web access about 10 seconds after boot. The user subsequently confirmed normal operation after the requested full power restart; read-only serial/HTTP checks confirmed accepted B sequence 5, guard=OK and an idle uploader. On 2026-11-19 the user then completed the phone-browser Direct upload/install workflow to accepted A sequence 6. Its cold power restart and focused failure cases remain pending. Thirty-three host checks pass.

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

Pending: sequence-6 full power restart and focused sound/timer acceptance, interrupted/cancelled/corrupt transfers, concurrent admission, power loss during upload/commit, peak memory and rollback/reconnection feedback in a browser. No failure-case acceptance follows from this successful normal-path test.
