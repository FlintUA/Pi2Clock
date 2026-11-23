# Pi2Clock G2 — SD card skeleton

This folder contains **no speech and no music yet**. It is the directory skeleton for a new FAT32 microSD card of the planned G2 device, not a playable card.

Copy the `PI2CLOCK` folder to the root of a separate, empty card so that `/PI2CLOCK/` is at the top level. Do not use it on the card of the current G1 clock (G1 uses the numbered folders in [`sound/_sdcard`](../../_sdcard/)). The structure only works once G2 firmware supports long file names and the JSON manifests.

Specification: [doc/generations/g2/SD_LAYOUT.md](../../../doc/generations/g2/SD_LAYOUT.md). Empty folders carry `.gitkeep` files so that they survive copying and Git.
