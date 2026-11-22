# Bluetooth audio chain: review and load reduction (2026-11-21)

The user reported Bluetooth music that stutters or audibly speeds up and slows down, on Portable and, more mildly, on Nest, without an obvious trigger. It improved when a second browser tab (on a PC) was closed and occurred in Direct and in Home mode, more on the 2.4 GHz network `flint.net` than on `Magenta`.

## Chain

1. **Source:** SPI card → Helix MP3 decoder (main loop, `-O3`) → resampling to 44.1 kHz where needed → PCM ring of 8,192 stereo frames (about 186 ms).
2. **Sender:** the BTstack A2DP source runs in the CYW43 async context, the same context that runs lwIP and the web server. A 10 ms timer credits elapsed samples (`samples_ready`), the SBC encoder fills one media packet from the ring, and the packet waits for a can-send event.
3. **Radio:** the CYW43439 has one antenna and one SPI bus to the RP2350 for both Wi-Fi and Bluetooth; it shares air time between them internally.
4. **Speaker:** the sink buffers packets and adjusts playback when they arrive irregularly.

## Findings

- **The source kept up in that capture.** A COM8 capture on OTA 18 showed `underruns=0` and a ring 70–90 % full for every speaker. This rules out the decoder and the card for that capture only; it is not proof for every track and load (correction, OTA 25).
- **Codec settings are equal.** Portable, Nest and a third speaker all ran SBC 44.1 kHz stereo (not joint stereo, as first written; a frame at bitpool 53 is 118 bytes), bitpool up to 53. Lowering the bitpool to 35 (OTA 19) silenced Portable and SSTB 10 and was reverted in OTA 20; the cause was a packet-size bug, see [OTA 25](#ota-25-audit-fixes-and-diagnostics).
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

## OTA 23 result: packet size is not the cause (OTA 24 candidate)

On OTA 23 the user heard crackling through almost the whole test, while the log showed Portable running at 2 frames per packet the entire time (adaptation had already reduced it before the test; `bt-frames 0` dropped back to 2 within about 6 s). Even at 2 frames the trimmed backlog grew from 85.9 s to 135.3 s in 189 s: the sender delivers only about 74 % of real time to Portable, with few long gaps (`late_packets` +65, `max_gap_ms` 282). The earlier "clean at 2 frames" window was therefore not reproducible. A likely explanation was that the link to Portable carries too few bytes per second for SBC at bitpool 53 (about 328 kbit/s). This is a hypothesis: the trimmed backlog shows that the sender fell behind, not why, and packets refused by BTstack were not counted before OTA 25.

OTA 24 removes the adaptive packet size (manual `bt-frames` remains) and adds the USB test command `bt-bitpool N`: the encoder uses a lower bitpool within the range the speaker negotiated, without renegotiation, as phones do. Every SBC frame carries its bitpool, so a compliant speaker decodes it. Expected rates at 44.1 kHz stereo: 53 ≈ 328, 45 ≈ 281, 37 ≈ 240, 31 ≈ 207 kbit/s. Unlike OTA 19, the negotiated maximum stays 53, so the configuration Portable accepted is unchanged. A test with Portable decides whether a lower rate removes the crackling; only then becomes it automatic.

If stalls remain with no page open, the next candidates are Wi-Fi power management and HTTP keep-alive; both need separate measurement.

## OTA 25: audit fixes and diagnostics

An external audit of the chain (checked against the BTstack sources) found defects that make the earlier measurements hard to interpret. OTA 25 fixes them before more listening tests.

| Finding | Effect before OTA 25 | OTA 25 |
| --- | --- | --- |
| The one-byte SBC media header was not reserved: frames filled the whole payload the speaker allows, and the header made the packet one byte too large. | BTstack refuses such a packet (`ERROR_CODE_MEMORY_CAPACITY_EXCEEDED`). With bitpool 35 on Portable, 8 × 82 + 1 = 657 > 656 bytes, so every packet was refused: this explains the silence on OTA 19, which was wrongly attributed to the speaker rejecting bitpool 35. At bitpool 53 (5 × 118 = 590) the bug did not trigger. | The payload limit keeps one byte for the header and never exceeds 15 frames (4-bit frame count). |
| The return value of the send call was ignored. | A packet refused for full ACL buffers (`BTSTACK_ACL_BUFFERS_FULL`) was dropped, while the RTP timestamp advanced: the speaker received a hole in the audio. Such drops were invisible in the log. | On full buffers the packet and its timestamp are kept and sent on the next can-send event. Other errors are counted as lost; counters appear in `bt-status` (`[A2DP-SEND]`). |
| After a bitpool change the frame length came from the encoder, which updates it only after encoding a frame. | The first packets after `bt-bitpool` could be computed with the old frame size (possible over-filled packet). | The frame length is computed from the SBC configuration (A2DP specification); a bitpool whose frame does not fit one packet is refused. |
| Bluetooth calls from the main loop (volume, connect, disconnect, scan, test tones) ran without the async context lock. | Rare corruption of BTstack state, because the stack runs in a background interrupt and is not thread-safe. | All such calls take the (recursive) async context lock. |
| Play/pause buttons on the speaker suspended or stopped the A2DP stream. | The main loop treated the inactive stream as a lost link and moved music to the built-in speaker. | The buttons pause or resume the music player; the stream stays open (`[BT-REMOTE]`). |
| AVRCP Absolute Volume was assumed whenever AVRCP connected. | A speaker that refuses Absolute Volume stayed at a fixed level and the clock did not attenuate. | If the speaker answers SetAbsoluteVolume with REJECTED or NOT IMPLEMENTED, the clock switches to PCM volume for that connection (`[BT-VOL]`). |

New diagnostics: while the stream is active, one line every 10 s, printed only when something went wrong in that interval:

`[BT-DIAG] 10s sent retried lost err gap_avg gap_max late trimmed underruns silence http_get http_post bitpool payload`

`retried` counts packets delayed by full ACL buffers, `lost` refused packets, `gap_*` the time between sent packets, `trimmed` the backlog dropped by the 125 ms cap, `silence` the duration of ring underruns, and `http_*` the requests the clock served in the interval (page polling shares the radio).

Not changed: SBC configuration and default bitpool 53, packet pacing, page polling, Wi-Fi settings. The next step is a series of 10-minute tests with fixed settings (pages closed, one page with the screen on, two pages; each speaker), compared by these counters and the user's marks of audible crackling.

## OTA 25 result: no lost packets, but stalls remain (OTA 26 candidate)

Test on 2026-11-22 (Portable, one phone page open, about 11 minutes of `[BT-DIAG]` lines). The user heard crackling and "dragging" speed almost all the time, more noticeable at loud levels. Speaker play/pause buttons worked and music stayed on Bluetooth.

- **Sending works as intended.** `retried=0 lost=0` in every interval and 68,598 packets sent: no packet was refused or dropped. The packet geometry is unchanged at bitpool 53 (5 frames, 590 bytes; the header fix only matters at other bitpools).
- **The sender still falls behind.** Real time needs 689 packets per 10 s (44,100 / 640 samples). Intervals delivered 594–694, never more than real time, with 1–8 gaps over 60 ms and gaps of up to 291 ms in most intervals. The backlog dropped by the 125 ms cap grew by 27 s in 11 minutes (about 4 % of real time, against 26 % on OTA 23). What the cap drops never reaches the speaker, so its buffer runs short after every long gap; an adaptive speaker answers with slower playback or crackling, which matches the user's description. This is an inference from the counters, not a measurement inside the speaker.
- **Ring underruns follow the gaps.** After a gap the sender takes up to 125 ms from the PCM ring at once; with the ring only partly full this produced 0–23 underruns per 10 s (up to 63 ms of inserted silence). Underruns appear only in intervals with trimming.
- **Web traffic is not the driver.** About 10 requests per 10 s throughout; intervals without gaps (for example 3 minutes from 08:01:29 UTC) had the same request count as intervals with the largest gaps.
- **Diagnostic bug.** The ring's underrun count restarts with every track, so the first interval after a track change printed a wrapped value (about 4.29 billion). Fixed in OTA 26.

The gaps of up to about 290 ms are close to the Wi-Fi driver's default power-saving timer (PM2 with 200 ms return to sleep), which was never changed in this firmware. OTA 26 adds the USB test command `wifi-pm default|none|perf|aggr` (not saved; reapplied when Wi-Fi comes up) and shows the mode in `[BT-DIAG]`. The planned comparison: baseline, `wifi-pm none`, `bt-bitpool 35` (7 frames per packet, 49 instead of 69 packets per second, now valid after the header fix) and both together, each for several minutes with the user marking audible crackle.

## OTA 26 blind test: Wi-Fi power saving and packet rate (OTA 27 candidate)

Blind test on 2026-11-22 (Portable, Home mode, one phone page; the user did not know the settings). `[BT-DIAG]` lines appear only for intervals with a problem, so missing lines mean clean intervals.

| Segment | Setting | User verdict | Packets per 10 s (needed) | Longest gap | Trimmed per 10 s | Underruns |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | power saving on (driver default), bitpool 53 | crackle 2 of 3, dragging | 596–688 (689) | 318 ms | 70–1,270 ms | 143 |
| 2 | power saving off, bitpool 53 | crackle 1, dragging | 626–644 (689), steady | 115 ms | 650–930 ms, steady | 2 |
| 3 | power saving on, bitpool 35 | single crackle every 5–7 s or rarer, no dragging | 481–495 (492) | 282 ms | 0–232 ms | 0 |
| 4 | power saving off, bitpool 35 | no crackle, no dragging | 480–493 (492); most intervals clean and not printed | 95 ms (267 ms right after switching) | 0 (240 ms once after switching) | 0 |

Two separate effects:

1. **Wi-Fi power saving causes the long gaps.** With power saving off the longest gap fell from about 300 ms to about 110 ms and the ring underruns disappeared (segments 1→2, 3→4).
2. **The Portable link carries about 63 packets per second.** In segment 2, without long gaps, the sender still delivered a steady 92 % of real time: bitpool 53 in a 656-byte payload means 5 frames per packet and 69 packets per second. At bitpool 35 a packet holds 7 frames (49 packets per second) and the sender kept up. Whether the limit is the packet rate or the byte rate is not yet separated; the 590- and 574-byte packets both fit one baseband packet, which points to the packet rate.

OTA 27:

- **Automatic Wi-Fi power saving:** off while an A2DP stream is active, driver default otherwise (`[WIFI-PM]` logs each change). `wifi-pm auto|none|default|aggr` overrides it for tests.
- **Automatic bitpool:** the highest bitpool within the negotiated range that puts at least 7 SBC frames into one packet (never below 30). For a 656-byte payload this is bitpool 40 (92-byte frames, 7 per packet, the same 49 packets per second as bitpool 35, with 14 % more data per frame). Speakers whose payload already holds 7 frames at the negotiated maximum keep it. `bt-bitpool N` overrides it for tests; `bt-bitpool 0` returns to automatic. `[A2DP-PACKET] bitpool=… auto|manual` shows the choice at every stream start.

Open: acceptance on Portable (automatic, compared blind with bitpool 35), the bitpool chosen for Nest, PRO X 2 and SSTB 10, and Direct mode. Quality could later improve with Joint Stereo at the same bitpool; the speakers currently negotiate Stereo.

## OTA 27 acceptance and stall recovery (OTA 28 candidate)

Acceptance test on 2026-11-22 (power saving automatic, bitpool automatic):

| Speaker, mode | Bitpool, frames per packet | User verdict | Trimmed | Longest gap |
| --- | --- | --- | --- | --- |
| Portable, Home | 40 auto, 7 | first track clean; 4–5 short crackles in the second | 926 ms, all within one minute | 287 ms |
| Portable, Home | 35 manual, 7 | clean, no dragging | 0 | 74 ms |
| Portable, Direct | 40 auto, 7 | clean, same as bitpool 35 | 0 | 113 ms |
| PRO X 2, Home | 53 auto, 7 (883-byte payload) | clean | 0 after connection | 100 ms |

All crackles of the first segment fell into one minute in which the phone page also nearly stopped reaching the clock (3 instead of about 11 requests per 10 s), so it was a disturbance of the radio as a whole rather than of bitpool 40. Bitpool 40 and 35 send the same number of packets; the test does not separate them. Nest and SSTB 10 were not tested. OTA 27 is the working baseline.

What remains are such disturbances: after a stall the sender sent at most 125 ms of backlog and dropped the rest, so the speaker's own buffer stayed lower and the next stall emptied it. OTA 28:

- The backlog owed to the speaker is capped at 300 ms instead of 125 ms. With 7 frames per packet the Portable link has about 28 % spare packet rate (about 63 packets per second against 49 needed), so a 300 ms stall is caught up in about a second.
- The PCM ring grows from 8,192 to 16,384 frames (about 372 ms, 64 KiB; the checkpoint used to resume music after an announcement grows likewise) so the catch-up does not empty it.
- `[BT-DIAG]` is printed only for intervals with trimmed backlog, underruns, refused or retried packets, or a gap over 150 ms; gaps of 61–150 ms are harmless at 20 ms per packet.

A stall longer than the speaker's own buffer still produces a crackle. The check needs 20–30 minutes of music on Portable (random disturbances), compared with OTA 27 by crackles heard and trimmed backlog, and a listen for speed-up after stalls.
