# Network and time

Wi-Fi, NTP, the two browser network modes and settings compatibility of the G1 firmware (release `g1-v1.1.0`). The default Bluetooth build includes Wi-Fi/NTP. The clock joins a configured 2.4 GHz network asynchronously, requests UTC from pool.ntp.org and writes Europe/Berlin local time to DS1302. Configuration is optional: without credentials, the clock keeps using its RTC.

## Local setup on Windows

Close any serial monitor. Build and flash the current firmware, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\configure-wifi.ps1 -Port COM8
```

The helper checks firmware support, prompts for SSID and password locally, sends them over USB and confirms saving. It does not display the password or put it in shell history. Credentials are stored in the device settings Flash; they are not encrypted. Do not publish serial-terminal input that contains credentials.

The current provisioning interface accepts an ASCII SSID of 1..32 characters, excluding |, and an empty password for an open network or an 8..64-character ASCII WPA2 key. The Pico wireless interface uses 2.4 GHz. For the 64-character PSK form, use hexadecimal digits.

Manual USB alternative:

```text
wifi-config YOUR_SSID|YOUR_PASSWORD
save
ntp-sync
ntp-status
```

Use actual values only in your local terminal. Do not send them to a public issue or chat. The first | separates SSID and password. The password may itself contain |.

## Behavior

- Wi-Fi connection attempts are asynchronous, with a 15-second join timeout and delayed retries.
- DNS/UDP NTP requests have a 10-second timeout. Failed requests retry after one minute.
- Successful samples are refreshed hourly.
- Reply validation checks server address/port, NTP version/mode, leap/stratum state, request nonce and a plausible supported timestamp. NTP is a conventional unauthenticated network time source.
- NTP callbacks stage a UTC sample. RTC writes run from the main loop only when timer, alarm, menus and audio are idle.
- Corrections of at most one second are treated as already synchronized.
- An ordinary significant correction consumes the current scheduler boundary rather than replaying missed announcements/alarms. The expected spring DST jump permits the new 03:00 boundary; after a backward correction, repeated civil time is suppressed until the previous clock time is reached.
- DST changes also wait for the same idle window as other RTC writes; they can be delayed while audio or a timer owns the device. Events in skipped minutes are not replayed.
- The monotonic countdown timer is independent of RTC adjustments.
- After an NTP sample, a RAM UTC anchor also allows DST conversion during a temporary network outage. On an offline reboot, DS1302 continues with its stored local time; a fresh NTP reference is needed to resolve a transition that occurred while the board was off.

Commands:
- ntp-status: configuration/radio/synchronization state and current UTC offset; no password.
- ntp-sync: request a fresh sample when the device is idle and online.
- wifi-clear: remove saved credentials, then wait for autosave=OK or use save.
- version: firmware version, source build ID and board.

Manual date/time editing remains available. Subsequent NTP synchronization corrects it to the network reference.

## Europe/Berlin

CET is UTC+1; CEST is UTC+2. Summer time starts at 01:00 UTC on the last Sunday of March and ends at 01:00 UTC on the last Sunday of October. The implementation uses these current rules for the supported RTC calendar, rather than hardcoded dates for one year.

References: [German federal time-change FAQ](https://www.bundeswirtschaftsministerium.de/Redaktion/DE/FAQ/zeitumstellung/faq-zeitumstellung.html), [EU 2022-2026 transition schedule](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX%3A52021XC0427%2801%29), [Raspberry Pi networking libraries](https://www.raspberrypi.com/documentation/pico-sdk/networking.html). A future legal change to time-zone rules would require a firmware update.

## Network modes (web profile)

The web profile serves the same browser page in one of two modes; they never run at the same time.

- **Home:** the clock joins a saved 2.4 GHz network and uses NTP. Two profiles can be saved, **Main** and **Backup**. Boot tries Main first; a failed join tries Backup (1-second handoff, 30-second backoff after both fail); a healthy Backup connection stays selected. Phone Control on the clock shows join, address and retry progress.
- **Direct:** the clock's own WPA2 access point `SpeakingClock` at `192.168.4.1`, without router or Internet; no NTP, the RTC keeps time. The Direct password is generated once, kept after saving and can be rotated in Phone Control.

Switching: SETTINGS → Phone Control on the clock, or the browser's Wi-Fi and Direct page (with confirmation, cancellation and instructions for moving the phone to the other network). After a browser update the clock returns to the network mode the update was sent from.

Browser setup of home networks (from Direct): **Test and save** joins the candidate network and saves it only after the join reached an IPv4 address; old credentials stay until then and a failure restores Direct with the same key. The page can search for networks, edit Main or Backup, **Connect** a saved profile on demand and forget a profile. Changing accepted home credentials turns home trust OFF. USB `wifi-config` changes Main and keeps Backup; `wifi-clear` clears both. Details: [browser Wi-Fi setup](WEB_WIFI_SETUP.md), [network modes](WEB_NETWORK_MODES.md).

Browser authorization is separate from the Wi-Fi key: a browser is paired once per mode with a six-digit code from the LCD (up to four entries); optional home trust lets any client on the home subnet control the clock without pairing. See [browser access](WEB_BROWSER_ACCESS.md). The page uses numeric HTTP addresses and needs no cloud service.

## Explicit clock changes

The browser can set the full date and time and request NTP separately ([clock controls](WEB_CLOCK.md)). Physical and browser edits share the scheduler protection against replaying or skipping events. After a manual write the previous NTP reference is discarded and the next hourly request is due one hour later; NTP then corrects the clock again. Local times in the missing spring hour are rejected.

## Settings compatibility and rollback

Settings live in two A/B Flash sectors with CRC and sequence numbers. The firmware reads every format v1–v18 and chooses the smallest format that holds the actual settings when it writes; loading never writes or migrates.

| Format | Written when | Bytes |
| --- | --- | --- |
| v11 | Stable baseline fields only (display light added to v10) | 348 |
| v12 | Phone settings present (Direct key, four browser entries, home trust) | 504 |
| v13 | A birth year in slots 1–5 is known | 512 |
| v14 | Any birthday slot 6–15 differs from its default | 616 |
| v15 | Timer completion choices differ from the defaults | 624 |
| v16 | Random timer or alarm music is used | 632 |
| v17 | Five-second timer warning is enabled | 640 |
| v18 | A Backup home network is saved | 744 |

Each format extends the previous one unchanged; v11–v13 use two 256-byte pages, v14–v18 three pages of the same sector. Older firmware cannot read a newer format: once both A/B sectors hold a newer record, a downgrade loads an older record or defaults. Before a rollback, note the intended settings (or remove the newer features and verify both records), and prefer a build from the same release in another profile (`-NoWifi` and the ordinary profile read and preserve all fields, including phone settings). Stable v1.0.0 reads only v1–v11. Snoozes and waiting birthday playback are RAM-only in every profile.

## Hardware acceptance

Status per feature: [FEATURE_STATUS.md](FEATURE_STATUS.md). The first acceptance on 2026-11-08 (build 7964939) reported configured, synchronized and Europe/Berlin UTC+1, with Portable streaming while Wi-Fi was active ([evidence](HARDWARE_TEST_EVIDENCE.md#november-8-wi-fintp-and-bluetooth-coexistence)). For a new installation:

1. Capture `version`, `flash-info`, `alarm-status`, `audio-settings` and `bt-known` before changing network settings.
2. Provision the network and wait for the save.
3. Check the Wi-Fi connected, validated UTC sample and RTC synchronized messages (`ntp-status`).
4. Compare the LCD with a trusted Europe/Berlin clock.
5. Play music on a Bluetooth speaker while the network is enabled.
6. Restart and confirm that credentials, alarms, volumes and speakers survive.

Still open: an overnight run, NTP server outage and recovery, access-point outage and recovery (deferred by the user), an actual DST transition. No offline RTC drift rate has been measured or enabled.

To build the Bluetooth-only radio profile, pass `-NoWifi` to `build-clock-bt.ps1`; network credentials are preserved unchanged in that profile.
