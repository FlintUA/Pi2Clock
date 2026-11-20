# Device generations and firmware identity

## Independent identifiers

- **Pi2Clock G1** identifies the existing Pico 2 W clock with DFPlayer and two SD cards.
- **Pi2Clock G2** is reserved for the planned I2S/MAX98357A device with one shared SD card. No G2 firmware or branch is created by this change.
- The firmware version comes from a reachable Git release tag, independently of the hardware generation and OTA counter.
- The build ID identifies source revision, tracked local modifications and build profile. New G1 IDs begin with `g1-`.
- The OTA sequence strictly increases within a device family. G1 continues from 10 to 11; do not reset it when a release version changes. Non-OTA builds report 0 (not applicable).

The LCD retains two About pages: `Pi2Clock G1 / Pico 2 W`, then the compact version and `FlintUA OTA<n>` for OTA builds (author only otherwise). Browser About and USB `version` provide full version/build, model and OTA sequence. The startup splash also identifies G1. A trailing `+` on the compact LCD version indicates development or modified sources; browser/USB show the complete version.

## Tags and branches

New tags use `g1-v<major>.<minor>.<patch>` and, in the future, `g2-v<major>.<minor>.<patch>`, optionally with a prerelease suffix. These are examples, not assigned releases. G1 prefers valid, reachable `g1-v*` tags and ignores G2 tags. Until the first G1 tag exists, existing reachable `v*` tags remain its baseline. Untagged descendants include commit distance/revision; tracked modifications retain the dirty marker. Source archives do not borrow tags from a containing checkout.

Current work stays on `codex/phone-control`. Create `codex/gen2` when second-generation work starts. Release tagging, merging and installation remain separate steps.

## Packages and transition

Without `--output`, `tools/ota_web_package.py` names packages `Pi2Clock-G1-v<firmware-version>-ota<sequence>.clockota` in the build directory. Development versions may contain `+<distance>.g<revision>`. Review JSON includes model, generation, version, target, build, sequence and hashes. Renaming a file does not change compatibility.

The canonical identity is `firmware/pico2w_c/app/device_identity.h`; a copy accompanies the generated version header. The packager verifies that the built identity matches its source identity. G1 retains CLOCKOT1 target `0x23500002` for compatibility with installed ota10. Flags, reserved bytes, layout and saved settings format remain unchanged. The `g1-` prefix embeds the generation in the existing build field.

The new receiver checks the target and G1 prefix **before erasing the inactive slot**, including requests bypassing browser validation. Browser and packager also reject incompatible/unidentified builds. Legacy unprefixed packages are no longer accepted by the new receiver. Existing ota10 does not enforce the prefix but enforces the target, so it can install the transition package. Reserve **`0x23500202` for G2**, even if its MCU is also Pico 2 W; future G2 packages must use that separate target and `g2-` prefix so old G1 receivers reject them too.

These compatibility checks are not publisher authentication: CLOCKOT1 is unsigned. G2 packaging, receiver and sequence policy still require implementation and hardware validation on its future branch.

## Acceptance

Tests cover generation tags and legacy fallback, source/build identity, package naming, browser rejection and device rejection before Flash erase. The unchanged header fields preserve the ota10 bootstrap path. SDK builds and package metadata are verified separately. Installation and LCD/browser hardware acceptance require separate user approval; host tests are not hardware acceptance.

### Candidate verified on 2026-11-20

All 33 registered host tests passed, including new generation/tag/package/About cases. Both MP3/Bluetooth/Wi-Fi/phone-web SDK builds passed: ordinary (OTA sequence 0) and A/B trial (sequence 11). Source revision `accbeb708131` produces version `1.0.0+61.gaccbeb7`; no release tag was created. The reviewed candidate is `Pi2Clock-G1-v1.0.0+61.gaccbeb7-ota11.clockota`, build `g1-accbeb708131-bt-mp3-wifi-phone-ota11-trial`, 1006668 bytes, SHA-256 `23b0a4da56dae3d860468e49acb16f4d3a6d731974067524b4edb3a70f4ad9e1`.

As an additional transition check, the original ota10 C header parser from `dfe3bd7` was compiled on the host and accepted this exact package header at current sequence 10. Its original browser header parser also accepted the package and rejected a different target. These are offline compatibility checks, not a board installation. The new receiver's tests independently reject G2 target/prefix before erase. The candidate remains uninstalled; LCD, browser About and runtime installation acceptance are pending.
