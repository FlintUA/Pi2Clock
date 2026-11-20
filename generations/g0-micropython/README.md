# G0 archive — MicroPython firmware

Archived code and documents of the original MicroPython clock. Not maintained; do not install on the current G1 clock. The generation is described in [doc/generations/G0.md](../../doc/generations/G0.md).

| Path | Content |
| --- | --- |
| `source/speaking_timer_clock.py` | Version 1.x (last 1.16), single file |
| `source/speaking_timer_clock_v2.py` | Version 2, single file |
| `source/v2-modular/` | Version 2.0.0 modular rewrite (`main.py` + package `speaking_clock`), August 2026 |
| `source/v3/` | Version 3.x up to 3.10.0, the last firmware before the C migration; `main_local_backup.py` is a local variant from 2026-11-04 |
| `library/` | MicroPython drivers: LCD, DS1302, DFPlayer, rotary encoder, picozero |
| `schematic/` | Original Raspberry Pi Pico schematic |
| `doc/` | G0 test plans, bring-up, controls, roadmap, version notes and state notes |
| `tools/` | SD-card folder migration and missing-phrase generation scripts (August 2026) |
| `sound-drafts/` | Unused regenerated variant of German phrase 17/015 (2026-08-27) |
