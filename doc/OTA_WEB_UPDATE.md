# Browser firmware update candidate

Status: implemented; 33 host checks and SDK builds pass; NOT installed or hardware-accepted. The clock currently runs the user-tested foundation image in accepted slot B. Home/Direct browser uploads are not yet device-proven.

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

The installed sequence-2 image does not contain this uploader. A separately approved, partition-aware USB installation into inactive A is required once, followed by the explicit trial activation and settings-preservation checks already proven during foundation testing. Do not rewrite the table or use the ordinary updater. Stop for user acceptance before a separately approved real browser trial.

Pending physical checks: receive/program/readback while the radio serves HTTP, SHA/metadata validation on actual physical Flash, successful and interrupted Home/Direct transfers, cancellation, wrong file/version/hash, concurrent admission, reconnect/rollback feedback, actual duration and memory, power loss during upload/commit, and persistence after a full restart. Host tests do not establish these cases.

ROM storage/translation, Flash permission checks and explicit-buy behavior follow the [official SDK runtime documentation](https://www.raspberrypi.com/documentation/pico-sdk/runtime.html).
