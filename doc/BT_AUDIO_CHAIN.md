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

If stalls remain with no page open, the next candidates are Wi-Fi power management and HTTP keep-alive; both need separate measurement.
