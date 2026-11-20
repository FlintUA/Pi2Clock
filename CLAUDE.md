# Pi2Clock — instructions for Claude Code
@AGENTS.md

- Single working copy: C:\Users\Flint123\projects\Pi2Clock, synced with https://github.com/FlintUA/Pi2Clock. Start with `git pull --ff-only`, finish with commit and push.
- Current generation is G1 (firmware/pico2w_c). G0 in generations/g0-micropython is archived and read-only. G2 is planned only. See doc/generations/.
- Build with build-clock-bt.ps1 into short ASCII paths under C:\pico_clock_compile\. Helix decoder: third_party\Helix-MP3-Decoder (gitignored, pinned commit e4f5ada).
- Never flash the clock (USB or OTA) without explicit approval for that specific build. After installing: verify version/build ID and settings over COM8, release COM8 and stop for user testing.
- Host tests: cmake -S firmware/pico2w_c/tests -B build/host-tests; cmake --build build/host-tests --config Debug; ctest --test-dir build/host-tests -C Debug.
