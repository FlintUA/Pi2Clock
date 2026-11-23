# G2 microphone (INMP441): plan and ideas

> **Status (2026-11-23):** the INMP441 is **wired on the G2 board** (see [HARDWARE.md](HARDWARE.md#48-inmp441-microphone-wired-shared-i2s-clocks-experimental)), but the first G2 release gives it **no function** — at most a test that audio can be captured. The ideas below are a plan for later releases, structured from material the user supplied on 2026-11-23 ([original](sources/MICROPHONE_IDEAS_2026-11-23.txt)). Nothing here is implemented or measured.

## Hardware

The INMP441 outputs 24-bit audio over I2S at 3.3 V, so no ADC or microphone amplifier is needed.

| INMP441 | Pico 2 W | Note |
| --- | --- | --- |
| VDD | 3V3 | Supply |
| GND | GND | Common ground |
| SCK | GP16 | Bit clock shared with the MAX98357A |
| WS | GP17 | Word clock shared with the MAX98357A |
| SD | GP4 | Microphone data input |
| L/R | GND | Left slot |

Shared clocks allow simultaneous playback and recording if the sample rate, PIO programs, DMA and buffers agree. Proposed: run the I2S clocks permanently at 44.1 kHz (silence when nothing plays) and decimate the microphone stream in software, for example to 16 kHz. Examples of RP2350 projects using an I2S microphone together with a MAX98357A exist, so the approach is realistic; it is unverified on this device.

## First release: capture test only

- Start the PIO receive program and DMA next to the playback path, read the microphone, report the level over USB (and optionally on the OLED).
- Measure: CPU load and RAM of the capture path; whether playback stays free of underruns with Wi-Fi, Bluetooth, web server and OLED active; noise from the class-D amplifier and supply at the microphone.
- The biggest uncertainty is not the microphone itself but its I2S stream together with the MAX98357A, Bluetooth audio and the MP3 decoder at full RP2350 load. This must be measured before any voice feature is promised.

## Later functions (ideas, by effort)

| Function | Works | Effort | Notes |
| --- | --- | --- | --- |
| Sound level indicator | Offline | Low | Relative level on the OLED, not calibrated dB SPL |
| Clap or knock detection | Offline | Low | Amplitude and timing only, no speech recognition; for example two claps = OLED light, one clap = silence the alarm or show the time |
| Room noise monitoring | Offline | Low | Relative level; dim the display in a quiet night |
| Music and sound visualisation | Offline | Medium | Small real-time FFT, band spectrum on the 256×64 OLED |
| Voice notes | Offline | Medium | Touch key starts a short WAV recording to `/PI2CLOCK/recordings/`; understanding its content and due time is a speech-recognition task |
| Push-to-talk commands | Offline | High | Touch key held while speaking; fewer false triggers and less CPU than permanent listening |
| 5–10 local keywords | Offline | High | Keyword spotting (TensorFlow Lite Micro has shown two-word recognition on Pico 2 W); not free Russian/German speech alongside MP3 and Bluetooth |
| Voice commands over Wi-Fi | Home server or cloud | High | The clock records and sends audio; a server recognises it and returns a structured command, for example "set the second timer to twenty minutes and start music" |
| AI assistant | Home server or cloud | High | The clock acts as an audio terminal; answers played through the speaker or Bluetooth |
| Permanent wake-word listening | Offline | Highest | Continuous CPU and power cost; only after the above |

A full voice assistant and local recognition of a few commands are different tasks; plans should not mix them.

## Privacy rules (to keep from the start)

- The microphone can be switched off in software (and the supply optionally switched off in hardware).
- Recording or listening is always visible on the OLED (and optionally on the WS2812).
- No audio leaves the clock over the network without the user's explicit permission.

## Suggested order

1. Capture test (first G2 release).
2. Level indicator and clap detection.
3. WAV voice notes on the card.
4. Push-to-talk with a few local commands.
5. Network voice commands and assistant, as an optional service.
6. Wake word last, if at all.
