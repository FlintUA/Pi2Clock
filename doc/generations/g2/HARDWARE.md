# G2 hardware: modules, pins, wiring and power

> **Status (2026-11-23): engineering draft for a hardware prototype, not a verified schematic.** Every connection must first be tested with temporary wiring; solder permanently only after the checks in [section 8](#8-acceptance-before-permanent-soldering). Translated and structured from the user's document `Pi2Clock_G2_WIRING_AND_ASSEMBLY.md` ([original](sources/docs/Pi2Clock_G2_WIRING_AND_ASSEMBLY.md)). Review notes are marked **Review**.

**Platform:** Raspberry Pi Pico 2 W (RP2350). G2 replaces the DFPlayer with a MAX98357A I2S amplifier and one microSD card, and the LCD1602 with an SSD1322 256×64 OLED. Controls: two encoders with push buttons and five TTP223 touch sensors; four WS2812 LEDs; Wi-Fi/Bluetooth with full offline operation. The enclosure and front panel do not affect the electrical design.

**Decisions of 2026-11-24:** GP6 keeps the G1 LED output circuit and now drives the **touch-key backlight** (the OLED sets its own brightness by command); GP5 becomes the **external alert output** for a vibration pad or lamp; the OLED reset uses an **RC power-on reset** instead of a GPIO.

**Decisions of 2026-11-23:** two encoders (a one-encoder variant follows only after the two-encoder G2 release); the **DS3231 is part of Base** and replaces the DS1302 with the same role as in G1; the **INMP441 is wired on the board** but has no function at first (a capture test at most); Base is built first. See [G2.md](../G2.md#decisions).

Markers: **[G1]** pin assignment verified on the G1 clock; **[G2]** proposed, needs testing; **[OPTION]** additional function.

## 1. Sources and confidence

- The current G1 pin map, G1 and G2 documents on `main` (checked 2026-11-23).
- The user's `raspberry-pi-pico-2-w-clock-audio-system.csv/.cir` describe **G1** (DFPlayer, DS1302, LCD1602, mechanical buttons). The `.cir` is a draft netlist with some supplies written as `0`; it is not an electrical schematic ([sources](sources/references/original_connections/)).
- OLED: seller data (SSD1322, 3.12", 256×64, 16-pin module, VCC 3.3/5 V, 4-wire SPI), the upiir example <https://github.com/upiir/ssd1322_256x64px_oled_display_arduino> and photos of board Ver 2.1. The BS0/BS1 jumpers and connector orientation must be checked before power-up.
- Datasheets: [Pico 2 W](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf), [MAX98357A](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf), [DS3231](https://www.analog.com/en/products/ds3231.html). Values of specific modules must be confirmed from their markings and with a multimeter.

## 2. Bill of materials

| Module / parts | Base | Full adds | Notes |
| --- | ---: | ---: | --- |
| Raspberry Pi Pico 2 W | 1 | – | Wi-Fi/Bluetooth, C firmware |
| OLED SSD1322 SPI 256×64, 3.12" | 1 | – | SSD1322 driver to be written |
| microSD SPI module + FAT32 card | 1+1 | – | Must work at 3.3 V and never drive 5 V onto MISO |
| MAX98357A I2S DAC + mono class-D amplifier | 1 | – | One speaker |
| Speaker 8 Ω 3 W | 1 | – | Bridge-tied output: SPK+ and SPK−, neither to ground |
| Mechanical rotary encoder with push button | 2 | – | TIMER and VOLUME, 3 GPIOs each |
| DS3231 + backup cell | 1 | – | I2C real-time clock, replaces the DS1302; check the charging circuit |
| INMP441 | 1 | – | I2S microphone, wired on the board, VDD 3.3 V; no function at first |
| TTP223 touch sensor | 5 | – | Logic output, not a mechanical contact |
| WS2812 | 4 | – | Daisy-chained on one data line |
| 74AHCT125 / 74AHCT1G125 | 1 | – | 3.3 → 5 V level shift for the WS2812 data line |
| USB-C panel socket | 1 | – | Check CC1/CC2 2×5.1 kΩ and current rating |
| WS2812 data resistor 220–470 Ω, bulk capacitor 100–470 µF on 5 V | 1+1 | – | Next to the first LED and the power input |
| Local decoupling 0.1 µF, 10–100 µF | as needed | – | SD, I2S and logic supplies |
| White backlight for the five touch keys | 1 set | – | LEDs with resistors behind the keys, one common PWM channel on GP6 through the G1 transistor/MOSFET switch |
| External alert output: logic-level MOSFET or NPN switch, flyback diode, 2-pin socket | 1 | – | On GP5; drives a 5 V vibration pad (bed shaker) or an external lamp |
| Vibration pad (bed shaker), 5 V | – | 1 | Plugs into the alert socket; typically 100–300 mA |
| OLED reset RC: about 10 kΩ + 1 µF | 1 | – | Unless the OLED module already has a reset circuit |
| BME280 | – | 1 | I2C, indoor climate in an outside-air channel |
| LiPo 103450, 2500 mAh | – | 1 | Not to be mixed with 14500 cells; needs protection |
| Charger + power path + stable rails | – | 1 | Choose a proven design, verify with an oscilloscope |
| ADC divider / INA226 | – | optional | Power monitoring; protect ADC inputs |
| MCP23017 I2C GPIO expander | – | optional | Only for an independent microphone clock or individual key LEDs |

The DIY kit is meant as one main board with prepared modules and connectors, so that the end user needs no soldering; this document is for the prototype builder.

## 3. Pico 2 W pin assignment (base plan)

Keeps the G1 microSD and both encoders, and uses the freed DFPlayer pins for the MAX98357A.

| GPIO | Pin | G2 function | Status |
| --- | ---: | --- | --- |
| GP0 | 1 | I2C0 SDA → DS3231, optional BME280 / MCP23017 | [G1] LCD → [G2] shared I2C |
| GP1 | 2 | I2C0 SCL → same | [G1] → [G2] |
| GP2 | 4 | WS2812 data through 74AHCT125 | [G2] |
| GP3 | 5 | OLED D/C | [G2] |
| GP4 | 6 | INMP441 SD → Pico (BCLK/WS shared with the amplifier) | [G2] wired, no function at first |
| GP5 | 7 | External alert output → MOSFET/NPN switch → vibration pad or lamp | [G2] |
| GP6 | 9 | Touch-key backlight PWM through the G1 switch circuit | [G1] circuit, new load |
| GP7 | 10 | OLED CS# | [G2] |
| GP8 | 11 | SPI1 RX / SD MISO | [G1] |
| GP9 | 12 | SD CS | [G1] |
| GP10 | 14 | SPI1 SCK → SD SCK and OLED CLK | [G1]+[G2] |
| GP11 | 15 | SPI1 TX → SD MOSI and OLED DIN | [G1]+[G2] |
| GP12 | 16 | TIMER encoder DT | [G1] |
| GP13 | 17 | TIMER encoder CLK | [G1] |
| GP14 | 19 | VOLUME encoder DT | [G1] |
| GP15 | 20 | VOLUME encoder CLK | [G1] |
| GP16 | 21 | PIO I2S BCLK → MAX BCLK and INMP441 SCK | [G2] |
| GP17 | 22 | PIO I2S WS/LRCLK → MAX LRC and INMP441 WS | [G2] |
| GP18 | 24 | PIO I2S TX data → MAX DIN | [G2] |
| GP19 | 25 | TIMER encoder switch | [G1] |
| GP20 | 26 | VOLUME encoder switch | [G1] |
| GP21 | 27 | TTP223 1: ALARM | [G2] (G1: mechanical) |
| GP22 | 29 | TTP223 2: MODE | [G2] |
| GP26 | 31 | TTP223 3: MINUS | [G2] |
| GP27 | 32 | TTP223 4: SETTINGS/PLUS | [G2] |
| GP28 | 34 | TTP223 5: TIMER_MODE | [G2] |
| 3V3(OUT) | 36 | External 3.3 V loads only after a current budget | [G2] |
| GND | 3, 8, 13, 18, 23, 28, 33, 38 | Common digital ground | [G2] |
| VSYS | 39 | Pico supply input through a power-selection circuit | [G2] |
| VBUS | 40 | Pico's own USB supply; **not** an output for the external 5 V rail | [G2] |

The DS1302 of G1 (GP2/GP4/GP5) is replaced by the DS3231 on the I2C bus. All usable GPIOs are assigned; the OLED reset needs no GPIO (RC reset).

**INMP441 caveat (original):** sharing BCLK/WS with the amplifier saves pins but requires identical clock rate and format for TX and RX and a PIO+DMA implementation. Independent rates (for example 16 kHz recording and 44.1 kHz playback) need more GPIOs; see [section 7](#7-full-variant-with-an-independent-i2s-microphone).

**Review:** G1 already resamples every source to 44.1 kHz for Bluetooth. If G2 runs the I2S clocks permanently at 44.1 kHz (silence when nothing plays), the INMP441 (specified for 7.8–50 kHz word clocks) can record at 44.1 kHz and the firmware can decimate to 16 kHz. Then the shared-clock variant needs no MCP23017 and no extra pins. To be confirmed on the prototype.

## 4. Wiring by module

### 4.1 OLED SSD1322, 16-pin, 4-wire SPI (seven wires)

| OLED pin | Signal | Connect to | Notes |
| ---: | --- | --- | --- |
| 1 | VSS / GND | GND | Common ground |
| 2 | VCC_IN | Stable 3.3 V | Rated 3.3/5 V; at 3.3 V verify start-up and current |
| 4 | D0 / CLK | GP10 (pin 14) | SCK shared with SD |
| 5 | D1 / DIN | GP11 (pin 15) | MOSI shared with SD |
| 14 | D/C# | GP3 (pin 5) | Data/command |
| 15 | RES# | RC power-on reset: ~10 kΩ to 3.3 V, ~1 µF to GND | No GPIO; fallback: GP5 (see below) |
| 16 | CS# | GP7 (pin 10) | Own chip select, idle HIGH |

**Reset:** the SSD1322 needs RES# low for a short time after its supply is stable; an RC network does this at power-up, and the firmware additionally sends the controller's software initialisation. Many modules already carry such a network — check board Ver 2.1 before adding one. **Fallback** if the display starts unreliably on the prototype: connect RES# to GP5 and move the alert output to a later MCP23017 or drop it. Brightness is set by SSD1322 commands (contrast and segment current); the OLED needs no PWM pin.

Leave OLED pins 3 and 6–13 open, but only after confirming that the board matches the seller's table; do not tie them to GND "for safety". Check the BS0/BS1 jumpers for SPI mode and mark pin 1 before soldering. Drive both chip selects HIGH before the bus starts. Never access SPI from different contexts without a common bus lock; change SPI speed only with both CS released.

### 4.2 microSD on SPI1 (six wires)

| SD module | Connect to | Notes |
| --- | --- | --- |
| CS | GP9 (pin 12) | Not shared with the OLED |
| SCK | GP10 (pin 14) | Shared bus |
| MOSI | GP11 (pin 15) | Shared bus |
| MISO | GP8 (pin 11) | SD → Pico only |
| VCC | Stable 3.3 V | Confirm the module accepts 3.3 V; do not use 5 V by default |
| GND | GND | Short wire, local decoupling |

First tests: FAT32 reads on SPI1 with the OLED present, then MP3 playback together with screen updates. Nothing on the shared SPI bus runs in parallel, even with DMA (serialise transactions, release CS, wait for completion).

### 4.3 MAX98357A amplifier (six required connections)

| MAX pin | Connect to | Notes |
| --- | --- | --- |
| VIN / VDD | Stable 5 V | The chip accepts 2.5–5.5 V; check power and heat |
| GND | GND | Common point with digital ground |
| BCLK | GP16 (pin 21) | PIO I2S bit clock |
| LRC / WS | GP17 (pin 22) | I2S word clock |
| DIN | GP18 (pin 24) | PCM serial data |
| SPK+, SPK− | One 8 Ω speaker | **Never** connect either output to GND |

If the board exposes `SD/MODE` and `GAIN`, check their state, pull resistors and the mode table of the actual board before power-up. Depending on `SD/MODE` the MAX98357A plays left, right or (L+R)/2. The robust choice is a **software downmix to mono duplicated into both channels**, so the channel selection cannot lose music; Bluetooth keeps full stereo. Do not tie `SD/MODE` blindly to 5 V or 3.3 V — it controls shutdown and channel mode. Start with limited volume and an 8 Ω speaker; never apply DC to the speaker.

### 4.4 Two encoders (six signals)

| Encoder | CLK | DT | SW | Supply |
| --- | --- | --- | --- | --- |
| TIMER | GP13 | GP12 | GP19 | Passive module: COM/GND to GND; `+` and pull-ups according to the module, not guessed |
| VOLUME | GP15 | GP14 | GP20 | Same |

As in G1, inputs use the Pico's pull-ups and the switches are active low. Add debouncing RC if needed, keep wires short and away from the speaker.

### 4.5 Five TTP223 touch sensors — not like mechanical buttons

| Sensor | Output to | Function |
| --- | --- | --- |
| TTP223 1 | GP21 | ALARM |
| TTP223 2 | GP22 | MODE |
| TTP223 3 | GP26 | MINUS |
| TTP223 4 | GP27 | SETTINGS/PLUS |
| TTP223 5 | GP28 | TIMER_MODE |

Each module: `VCC → 3.3 V`, `GND → GND`, `OUT → GPIO`. **Never connect OUT to ground like a button.** A basic TTP223 outputs active HIGH while touched; A/B and toggle/momentary modes depend on solder jumpers. G2 firmware must invert the G1 active-low button logic, use momentary mode, filter, detect long touches, wait for the sensors' start-up calibration and suppress false triggers from moisture or interference. Test through the actual panel material before closing the enclosure.

### 4.6 Four WS2812 in a chain

Wiring as specified by the user on 2026-11-24 (one buffer channel of the 74AHCT125, DIP-14/SOIC-14):

```text
Raspberry Pi Pico 2 W
GP2 (pin 4)
      |
      +--------> 74AHCT125 pin 2 (1A)

74AHCT125
pin 14 (VCC) ---- +5V
pin 7  (GND) ---- GND
pin 1  (/1OE) --- GND
pin 2  (1A)  <--- Pico GP2
pin 3  (1Y)  ----[330 Ω]---- DIN LED1

WS2812 (4 in series)
LED1 DOUT ---> LED2 DIN
LED2 DOUT ---> LED3 DIN
LED3 DOUT ---> LED4 DIN

All LED VDD ---> +5V
All LED GND ---> GND

Capacitor 100 nF:
74AHCT125 pin 14 ---||--- pin 7
```

| 74AHCT125 pin | Signal | Connect to |
| ---: | --- | --- |
| 1 | /1OE | GND (channel 1 always enabled) |
| 2 | 1A | Pico GP2 (pin 4) |
| 3 | 1Y | 330 Ω → DIN of LED1 |
| 7 | GND | GND |
| 14 | VCC | +5 V, 100 nF to pin 7 close to the chip |

**Review:** the unused channels 2–4 should not float (CMOS inputs): tie their inputs 2A, 3A, 4A (pins 5, 9, 12) to GND and their enables /2OE, /3OE, /4OE (pins 4, 10, 13) to +5 V, so the spare outputs stay high-impedance. Keep the ≥ 100 µF electrolytic across +5 V/GND next to LED1 and 0.1 µF ceramics near the LEDs. Until the 74AHCT125 is available, LEDs can be tested temporarily by feeding their VDD through a diode from 5 V (about 4.3 V, so 3.3 V is a valid HIGH); not for the final board. Identify DIN/DOUT from the markings of the LEDs actually received. A 74AHCT input reads 3.3 V as HIGH at 5 V supply; **a 74HC without T is not equivalent**. Limit maximum brightness in software (night mode, current and heat budget). The four RGB indicators are not individual backlights for the five touch keys.

### 4.7 DS3231 and [OPTION] BME280 on I2C0

`GP0 → SDA`, `GP1 → SCL`, `GND`, `3.3 V → VCC` of both modules. Pull-ups only to 3.3 V; if several boards carry pull-ups, measure the parallel value. Addresses: BME280 `0x76`/`0x77`, DS3231 `0x68` (no conflict). Place the BME280 in the outside-air channel, away from display, amplifier and battery, and **check by chip ID that it is a BME280, not a BMP280 without humidity**. Many DS3231 modules have a charging circuit for the backup cell — remove it or use a rechargeable cell, never charge a CR2032. Read the oscillator-stop flag before trusting the RTC time.

The DS3231 takes the DS1302's role from G1: the clock reads local time from it, writes it on manual date/time changes and NTP corrections (Europe/Berlin DST rules in the firmware, as in G1), and keeps running from the backup cell without power. Its temperature-compensated oscillator (about ±2 ppm) makes the offline drift calibration of G1 unnecessary.

### 4.8 INMP441 microphone (wired; shared I2S clocks, experimental)

| INMP441 | Connect to | Condition |
| --- | --- | --- |
| VDD | 3.3 V | Not a 5 V module |
| GND | GND | Common ground |
| SCK | GP16 / BCLK | Only with a synchronous shared configuration |
| WS | GP17 / LRCLK | Same |
| SD | GP4 | Pico I2S RX (PIO) |
| L/R | GND | Left slot (VDD for the right slot) |

The board gets the full wiring now; the firmware does nothing with the microphone in the first G2 release except, at most, a capture test (see [MICROPHONE.md](MICROPHONE.md)). The sound port must face outside, unobstructed and not right next to the speaker. Muting the speaker while recording is simpler than full echo cancellation. The user's module may have a different pinout — check the markings before wiring.

### 4.9 Touch-key backlight on GP6

The G1 LCD backlight output (GP6, active-high PWM through a transistor or MOSFET switch, LED with current-limiting resistor; see [G1 pin map](../../HARDWARE_PICO2W.md)) is kept unchanged and now lights the five touch keys: white LEDs with their own resistors behind the panel, all on one switched channel. Firmware keeps the G1 behaviour — OFF / ON / AUTO with day and night levels — for the keys. Individually controlled key LEDs would need a driver or expander and are not planned.

### 4.10 External alert output on GP5

`GP5 → gate resistor (~100 Ω) → logic-level N-MOSFET (or NPN with base resistor) → load to 5 V`, flyback diode across the load (motor), 2-pin socket at the back. Intended loads: a 5 V vibration pad under the pillow (bed shaker) for deaf or hard-of-hearing users, or an external lamp. Budget 100–300 mA on the 5 V rail. Firmware drives it in on/off patterns (alarm) and must limit the duty cycle. No vibration motor inside the clock: on a desk it would mostly rattle and is barely felt ([UI concept](UI_CONCEPT.md#light-signals-and-accessibility)).

### 4.11 [OPTION] Battery monitoring

INA226 on I2C0 (GP0/GP1); check its common-mode and shunt limits separately. A simple high-impedance divider for a 1S LiPo needs an ADC pin; GP28 is the only free ADC candidate and would have to be taken from TTP223 5, otherwise use an external ADC or an I2C fuel gauge. **Never feed up to 4.2 V battery voltage directly into a 3.3 V Pico ADC input.**

## 5. Power

```text
USB-C 5 V input -> protection/filter -> POWER_5V
                                     |-> MAX98357A VIN
                                     |-> 74AHCT125 VCC, WS2812 VDD
                                     |-> Pico 2 W through a properly isolated VSYS selection circuit
                                     +-> 3.3 V regulator (if needed)

Pico 3V3_OUT or a separate 3.3 V regulator (per current budget)
  -> OLED VCC_IN (after verifying the voltage)
  -> microSD, 5x TTP223, BME280, DS3231, INMP441, I2C logic

OPTION BATTERY: USB-C -> charger with power path -> system 5 V rail and 1S LiPo
  -> 5 V and 3.3 V must stay up while the source changes
```

**Warning.** The Pico 2 W has `VSYS` and a separate `VBUS` from its micro-USB socket. Do **not** join external 5 V, `VBUS` and `VSYS` into one node if two USB sources can be present; use the documented power-selection approach (diode or power path) from the Pico datasheet. If the panel USB-C is power-only, leave D+/D− open; firmware access is then through the Pico's own micro-USB inside the enclosure or over OTA. A data-capable external USB-C needs a proper USB 2.0 path and must exclude two simultaneous hosts.

**USB-C sink:** join the VBUS contacts, join the GND contacts, **CC1 and CC2 each through its own 5.1 kΩ to GND** (never CC1 to CC2). The previously inspected JRC-BC08 socket needs rework and checking here. CC resistors do not guarantee a current — verify the source, cable and the device's real current. Adapter: 5 V / 3 A as headroom, not a promise that the source grants 3 A.

| Block | Supply | Notes |
| --- | --- | --- |
| Pico 2 W | VSYS within the datasheet range | Preferably the standard power circuit |
| MAX98357A | 2.5–5.5 V, planned 5 V | Current depends on volume; bridge output |
| 4× WS2812 | 5 V | Up to about 240 mA at full white (3×20 mA each); check the actual LEDs |
| 74AHCT125 | 5 V | 3.3 V input from GP2, 5 V logic output |
| microSD module | 3.3 V | Peaks of roughly 100–200 mA depending on the card |
| SSD1322 module | 3.3/5 V per seller, planned 3.3 V | **Measure** — depends on brightness and lit pixels |
| TTP223 ×5 | 3.3 V | |
| BME280 | 3.3 V | Chip maximum 3.6 V |
| DS3231 | 3.3 V | Backup CR2032 separately; do not charge |
| INMP441 | 1.8–3.3 V, use 3.3 V | Never 5 V |
| Key backlight LEDs (GP6) | 5 V with current limiting / transistor | Low brightness preferred |
| Vibration pad or lamp (GP5) | 5 V through the alert switch | About 100–300 mA; check the actual pad |
| LiPo 1S | 3.0–4.2 V | Needs charger, protection, boost/PMIC |

**3V3_OUT:** keep the external load below about **300 mA**; the available current depends on RP2350, Wi-Fi and VSYS. SD and OLED peaks can cause dips. Measure each board (steady and peak) before powering everything from 3V3_OUT; for a repeatable kit a separate good 3.3 V regulator without back-feeding is preferable. All signals share a common ground.

**Bring-up order:** measure 5 V and 3.3 V without the Pico; then Pico + OLED; then SD; then the amplifier with speaker at limited volume; then touch sensors and encoders; LEDs; options and battery last. Measure current with the USB-C adapter and separately on battery.

## 6. Soldering rules

1. Check each pinout against a **photo of the actual board** and with a multimeter — modules with the same name often differ. Label connectors `OLED1`, `SD1`, `AMP1`, `ENC_TIMER`, `ENC_VOL`, `TOUCH1..5`, `RGB1..4`, `I2C-OPT`, `MIC-OPT`.
2. Use removable, keyed connectors for OLED, microSD, I2C, microphone, power and speaker.
3. Run separate 5 V branches with adequate cross-section to the amplifier and the WS2812. Reduce the class-D amplifier's influence on SD, OLED and microphone with local capacitors, return-current routing and cable fixing.
4. Low-resistance power and ground connections; short I2S and SPI lines, never parallel to the speaker wires.
5. Keep the BME280 away from regulators and the amplifier; do not cover its membrane; mount TTP223 sensors against the panel without air gaps.
6. microSD and USB-C at the back, BME280 at the bottom vent, indicators and OLED at the front. **No enclosure dimensions before a test fit and measurements.**
7. The common key backlight is on GP6; individually controlled key LEDs would need a driver and are not planned.

### Electrical and software conflicts to check

| Risk | Cause | Check / solution |
| --- | --- | --- |
| OLED + SD | Shared SPI1, different speeds and chip selects | Stress test SD reads with OLED redraws; bus lock or transaction queue |
| SD at 3.3 V | Start-up and peak current; a breakout designed for 5 V | Check the board's regulator/level shifter, measure dips |
| I2S + Bluetooth/Wi-Fi | PIO, DMA and decoder together with CYW43 | Monitor underruns and free SRAM |
| MAX98357A stereo → mono | `SD/MODE` may select only L or R | Check `SD/MODE`; software mono mix if needed |
| INMP441 on shared I2S | TX and RX clock rate may differ | Record with the same clocks first (44.1 kHz, decimate) |
| TTP223 instead of buttons | Active HIGH instead of a short to ground; toggle jumpers | Confirm the outputs, change the input handling |
| WS2812 data | 3.3 V is a marginal HIGH at 5 V supply | 74AHCT125, local decoupling |
| DS3231 with CR2032 | Charging circuit on cheap modules can damage the cell | Check and remove the charging path or use a suitable module |
| OLED pin numbering | Risk of a mirrored pinout | Follow the board markings, not the front view |
| OLED RC reset | Slow or noisy power-up may leave the controller unreset | Repeated cold starts; fallback RES# on GP5 |
| Alert motor on GP5 | Motor start current and back-EMF on the 5 V rail | Flyback diode, local capacitor, check for Pico resets |
| USB-C CC and two USB sources | Wrong CC resistors, back-feeding | Separate 5.1 kΩ per CC line; power-path / OR-ing circuit |

## 7. Full variant with an independent I2S microphone

If simultaneous 16 kHz capture and 44.1 kHz playback with separate clocks are needed:

- MCP23017 on I2C0 (GP0/GP1), 3.3 V, address by A0–A2, polled or with INT. **Move the five TTP223 to GPA0–GPA4**; the firmware must no longer assume direct Pico GPIOs.
- Use the freed GP21/GP22/GP26 as `MIC_BCLK`, `MIC_WS`, `MIC_SD`; keep GP4 spare (any three free GPIOs work, the I2S is PIO-based).
- Individual key backlights through a separate LED driver or MCP23017 outputs with transistor switches and current limiting.
- This is a different build variant: two firmware profiles or expander detection, and the five keys must keep working. Base needs no MCP23017. **Review:** probably unnecessary if the shared 44.1 kHz clock works (see section 3).

## 8. Acceptance before permanent soldering

- [ ] CC1/CC2 and 5 V at the USB-C socket in both C-C orientations, with the Pico disconnected.
- [ ] `3V3_OUT`, OLED and microSD current, peak currents and regulator margin.
- [ ] OLED `CS`, `D/C`, RC reset (cold start 20 times, also with slow power-up), a 256×64 test image, connector orientation.
- [ ] Key backlight on GP6: OFF/ON/AUTO levels, no flicker, no interference with the touch sensors.
- [ ] Alert output on GP5: vibration pad and lamp, current, flyback diode, no resets of the Pico when the motor starts.
- [ ] FAT32 with long file names, nested paths, no file mix-ups; cards above 32 GB only after explicit tests.
- [ ] SD + OLED together: throughput and concurrent stress test.
- [ ] 16/24/44.1/48 kHz PCM and MP3, mono and stereo, no lost left or right channel.
- [ ] Local audio and Bluetooth A2DP separately, output switching, music, speech over music.
- [ ] Both encoders: direction, switch, bounce, long presses.
- [ ] All five TTP223: active HIGH, momentary mode, through the panel material.
- [ ] Four RGB LEDs: colours, brightness, no false touches while they blink.
- [ ] Three timers, five alarms, date, offline stability (after the G2 functions exist).
- [ ] NTP, time zone, DST, optional RTC, wrong time without network, power loss.
- [ ] Maximum volume and 5 V current without dips, heat, speaker connector.
- [ ] With LiPo: charge, discharge, USB → battery → USB transitions on an oscilloscope, protection cut-off, no back-feeding.

## 9. Not yet decided

- OLED power and the overall current budget are not measured.
- The BS0/BS1 jumpers and levels of the SSD1322 board are not measured.
- The `SD/MODE` state of the purple MAX98357A breakout is not measured.
- Enclosure dimensions, the microphone chamber and the panel LEDs are designed separately.
- Three timers are a G2 requirement; G1 has one countdown and five alarms.
- G2 takes over G1's NTP, browser control, Bluetooth A2DP and A/B OTA only after implementation and a resource check.
