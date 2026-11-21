# Bluetooth audio chain: review and load reduction (2026-11-21)

The user reported Bluetooth music that stutters or audibly speeds up and slows down, on Portable and, more mildly, on Nest, without an obvious trigger. It improved when a second browser tab (on a PC) was closed and occurred in Direct and in Home mode, more on the 2.4 GHz network `flint.net` than on `Magenta`.

## Chain

1. **Source:** SPI card → Helix MP3 decoder (main loop, `-O3`) → resampling to 44.1 kHz where needed → PCM ring of 8,192 stereo frames (about 186 ms).
2. **Sender:** the BTstack A2DP source runs in the CYW43 async context, the same context that runs lwIP and the web server. A 10 ms timer credits elapsed samples (`samples_ready`), the SBC encoder fills one media packet from the ring, and the packet waits for a can-send event.
3. **Radio:** the CYW43439 has one antenna and one SPI bus to the RP2350 for both Wi-Fi and Bluetooth; it shares air time between them internally.
4. **Speaker:** the sink buffers packets and adjusts playback when they arrive irregularly.

## Findings

- **The source keeps up.** A COM8 capture on OTA 18 showed `underruns=0` and a ring 70–90 % full for every speaker. The decoder, the card and `-Os` in the main loop are not the cause.
- **Codec settings are equal.** Portable, Nest and a third speaker all ran SBC 44.1 kHz joint stereo, bitpool up to 53. Lowering the bitpool to 35 (OTA 19) silenced Portable and SSTB 10 and was reverted in OTA 20.
- **Web traffic shares the radio and the sender's context.** Each open page fetched seven files every second (status, Bluetooth, network, browser list, Wi-Fi, Wi-Fi scan, update state), each over a new TCP connection. Two open pages meant about 14 requests and well over 100 Wi-Fi packets per second, plus JSON generation in the context that paces A2DP. This matches the improvement after closing the PC tab.
- **The sender bursts after a stall.** The upstream sender sends one packet per can-send event and refills only on its next 10 ms tick. After a delay it owed the speaker the whole backlog and sent it as fast as possible: a gap followed by a burst, which a speaker hears as stutter followed by speed-up.

## Changes (OTA 21 candidate)

| Area | Change |
| --- | --- |
| Page | Status still every second; the other six snapshots refresh every poll only while their view or flow needs them (Bluetooth page or speaker sheet, network page or switch, browser access, firmware update), otherwise every 10–30 s. A pending command or a new epoch always refreshes. A hidden tab polls every 15 s and catches up when shown. Measured on the API stand-in: 25 requests in 20 s on the main page instead of about 140. |
| Sender | After each sent packet the encoder refills at once and asks for the next can-send event, instead of waiting up to 10 ms. The backlog owed to the speaker is capped at 125 ms; older audio stays in the PCM ring, so nothing is skipped from the music, the stream only shifts later. |
| Diagnostics | `bt-status` prints `[A2DP-PACING] late_packets max_gap_ms skipped_backlog_ms`; while streaming the same line is printed at most once a minute when new late packets (gap over 60 ms) occurred. |
| Build | `services/phone_web.c` (HTTP and JSON) is compiled with the default `-O3` instead of `-Os`, because it runs in the same context as the A2DP sender. |

Response formats, endpoints, guards, the SBC bitpool (53) and the fast busy-connect retry from OTA 19 are unchanged.

## Checks after installation

1. Music on Nest, PRO X 2, Portable and SSTB 10, with one page open, with two pages open, and with all pages closed.
2. A COM8 capture during playback (`tools/capture-pico-log.ps1`), then `bt-status`: compare `late_packets` and `max_gap_ms` with and without open pages and between `flint.net`, `Magenta` and Direct.
3. Alarms, timer completion and the ringing-alarm banner still appear within about a second while a page is open.

## OTA 21 result and next step (OTA 22 candidate)

On OTA 21 the user no longer heard speed changes; PRO X 2 played almost cleanly, but Portable still had strong crackling and distortion regardless of distance (on the desk next to the clock or 1 m away), volume, Wi-Fi network or Direct.

Volume path, for reference: the Bluetooth level 0..30 is sent as AVRCP Absolute Volume (`level × 127 / 30`, for example 16 → 68 of 127); the clock itself only attenuates MP3 PCM by 8/15 before SBC encoding and cannot clip. Distortion that does not depend on volume therefore points at audio data the speaker cannot decode cleanly, not at overload.

Both Portable failures so far concern packet contents: bitpool 35 (13 SBC frames per packet) produced silence, bitpool 53 (8 frames, about 952 bytes) produces crackling. OTA 22 prints the packet geometry at stream start (`[A2DP-PACKET] mtu_payload frame_bytes frames_per_packet`) and adds the USB test command `bt-frames N` (1–15; 0 = automatic, not saved) to try smaller packets on a speaker without rebuilding.

## OTA 22 measurement and adaptive packets (OTA 23 candidate)

Portable negotiates a media payload of only 656 bytes, so the automatic packet carries 5 SBC frames of 118 bytes (14.5 ms of audio; about 69 packets per second). With 5 frames the sender fell behind continuously: `late_packets` grew and the backlog trimmed by the 125 ms cap reached 4.3 s before the test and grew by about 18 s within one minute after returning to automatic, which the user heard as strong crackling. With `bt-frames 4` it still crackled moderately; with `bt-frames 2` (236 bytes, about 172 packets per second) the user heard no crackling and the trimmed backlog grew by only 0.13 s. A short underrun burst in that window coincided with a manual track change.

A plausible reason is that 2-frame packets fit a 3-slot baseband packet while 5-frame packets need 5-slot packets, which this speaker's link loses or retransmits more often; this is an inference, not a radio measurement.

OTA 23 makes the packet size adaptive: when more than 100 ms of backlog is trimmed within 3 s, the sender reduces the frames per packet (5 → 3 → 2), logs `[A2DP-PACKET] adaptive: …`, and keeps the smaller size for that speaker until restart. Speakers that keep up (PRO X 2, Nest) keep the automatic size. `bt-frames N` still overrides it; `bt-frames 0` returns to automatic with adaptation.

If stalls remain with no page open, the next candidates are Wi-Fi power management and HTTP keep-alive; both need separate measurement.
