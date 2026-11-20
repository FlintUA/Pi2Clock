# Current roadmap

This is the authoritative roadmap for the C firmware. It distinguishes the v1.0.0 release baseline from later G1 development, which was carried out on `codex/phone-control` and merged into `main` on 2026-11-20. Status reviewed on 2026-11-15: browser player mode/sleep is installed as `1.0.0+31.g798da44` and generally user-accepted on November 14; browser automatic announcements/quiet hours is installed as `1.0.0+32.g08b93c5` and generally user-accepted; browser date/time/NTP is installed as `1.0.0+33.gc2dbec4`, with functional user acceptance pending. Browser Bluetooth management is installed as `1.0.0+35.g5c09045`; the reported reload-like layout failure is fixed and user-accepted in `1.0.0+36.ge21b139` ([details](WEB_RECONNECT.md)). Browser network state/mode switching is installed as `1.0.0+37.ga1f576b`; the user accepted Direct and home transitions on November 15. Normal-screen LCD audio status is installed as `1.0.0+38.g2c8d5bc` and user-accepted on November 15. The SPK refinement is installed as `1.0.0+39.g42cc495` and user-accepted. Browser permission listing/selective removal is installed as `1.0.0+40.g9b20f8b`; general function is user-reported, with open-picker flicker. The +42 background-render hold resolved Android flicker in user testing. Single-network browser setup was installed as 1.0.0+43.g378a692 and generally user-accepted. Main/Backup profiles and search are installed in +44 and generally user-reported as working, including Direct discovery. The compact Connection UI is installed in +45; both Wi-Fi profiles survived the update. Explicit saved-network Connect/Edit is the current uninstalled candidate; see WEB_WIFI_SETUP.md for acceptance and Flash v18 rollback limits. Earlier MicroPython plans and migration logs are historical; unchecked boxes in those files are not the current task list.

## Release baseline

Version 1.0.0 is the stable C firmware baseline. See the [release notes](releases/v1.0.0.md).

Implemented for the first release candidate:
- One combined Bluetooth device list per MAC, with known devices first.
- Preserve saved speaker names when discovery returns an unknown-name fallback.
- The original release candidate resumed the preferred connection after browsing; current main replaces this with persistent manual OFF/scan behavior until explicit Connect.
- Asynchronous Wi-Fi join and NTP time reference, hourly resynchronization and offline RTC operation.
- Europe/Berlin CET/CEST conversion, including the last-Sunday March/October transitions.
- Flash v8 Wi-Fi provisioning with v1-v7 read compatibility and unchanged sector boundaries.
- Dynamic alarm music selection using detected folder 08 count, supporting tracks 1..255.
- Firmware version/build identity and updater verification of that identity when a sidecar is present.
- Native tests and GitHub CI for time/DST, NTP validation, Bluetooth catalog behavior, alarm scheduling and Flash migration.
- Current English controls, network setup, release notes and hardware acceptance instructions.

Hardware acceptance and remaining coverage:
- Initial NTP synchronization and Bluetooth playback with Wi-Fi enabled are confirmed on build 7964939. A periodic RTC refresh was observed on build 7378aa1 before Portable connected. Extend coverage to an overnight run and check refresh during Bluetooth playback.
- The v11-capable firmware loaded the existing v10 settings and synchronized NTP. The user confirmed that brightness, alarms, birthdays, the selected speaker and audio settings survived a save and restart. Host tests cover the v10 -> v11 record migration and v1-v10 reads.
- Test unavailable NTP server and later recovery.
- Manual connection/disconnection, OFF across a power cycle, no automatic return after a subsequent scan and automatic recovery after a Portable power cycle are user-confirmed on build 7378aa1. Remaining detailed checks: scan cancel/timeout, late callbacks and speaker-initiated reconnect; retain list deduplication/name retention.
- Verify alarm selection above track 45 using files present on both cards.
- The Windows updater verified the installed build ID for ab06727 against the selected UF2 sidecar.
- Daytime acceptance covers timer completion and priority at 17:00, idle hourly speech at 18:00, and the scheduled Daily alarm at 18:02. Overnight operation remains unverified.
- Boot with Nest selected is user-confirmed on build 7378aa1. Confirm that a forgotten device remains deleted after power loss.

Wi-Fi access-point loss and recovery on the assembled clock is deferred at the user's request. The available router controls did not provide a way to disconnect only the Pico for this test.

## Next functional milestones

New priority before presentation work: [Bluetooth music interruption/continuation](BT_MUSIC_INTERRUPTION.md) for hourly VOICE and scheduled alarms. The user explicitly deferred the DFPlayer/ADVERT extension. Sequence 12 is installed as `g1-4d2fcef70d40-bt-mp3-wifi-phone-ota12-trial`; accepted A, unchanged settings, Home/NTP and restored Nest connection were verified. Real sound continuity, snapshot allocation and live heap margin remain hardware acceptance checks.

Follow-up: the user confirmed hourly speech interruption/continuation; the supplied trace preserves the exact counters across two interruptions. Sequence 13 added 32 kHz playback and retained BT when a file cannot decode. The trace identifies failed file 076 as the previous LOCAL fallback trigger. The single-track audition guard is now separately installed as sequence 14, version `1.0.0+71.g8a8f7a6`, accepted A with unchanged settings and restored Nest. Bad-file skipping/32 kHz, audition failure handling and alarm continuation remain user checks. Seventeen cumulative music underruns in the supplied trace remain unexplained; live resource/performance acceptance remains open.

Phone control was developed on `codex/phone-control` and is part of `main` since 2026-11-20. Standalone direct and home Wi-Fi prototypes, integrated live status and browser timer control have passed user testing. The user also confirmed home access without repeated pairing, direct Wi-Fi reconnection without re-entering the password, and the LCD connection-progress screen. These experimental results are separate from the stable main release. See the [phone control instructions and evidence](../experiments/phone_control_ap/README.md).

Implemented and broadly user-accepted web functionality:

- Player Play/Pause/Resume/Stop/Next/Previous, accepted on build `44ca0814caac-bt-mp3-wifi-phone`.
- Independent LOCAL/BT volume, four audio output preferences, language and display-light mode/levels, accepted on build `aa20a9cc4962-bt-mp3-wifi-phone`.
- Five alarm and five birthday editors, accepted on build `3d87e9900de5-bt-mp3-wifi-phone`.
- Single birthday date field, optional birth year and mobile form alignment on build `d51dd7adf5b8-bt-mp3-wifi-phone`; the user reported the revised interface generally satisfactory before requesting sliders. This is broad acceptance, not explicit v13 save/restart coverage.
- Immediate volume and brightness sliders on build `499e78c94a0c-bt-mp3-wifi-phone`; the user reported that everything worked after installation. Sixteen host checks passed with Node.js available, including the production slider-script regression. COM8 verified the build, unchanged alarm/birthday records, valid Flash slots and synchronized NTP; read-only HTTP checks found all four sliders. These checks do not replace the remaining hardware scenarios.

### Current expansion status (2026-11-13)

The user reported that the latest changes were tested and worked correctly. Record this as broad functional acceptance, not proof that every migration, output/network combination or four-client scenario was exercised. See [hardware evidence](HARDWARE_TEST_EVIDENCE.md#november-13-expansion-user-report).

| Item | Current source and acceptance |
| --- | --- |
| Fifteen birthdays | Physical, USB and browser paths use 15 slots; pending/claim masks are 16-bit. v14 stores nondefault slots 6-15. General acceptance reported; slot 15 save/restart and timed delivery remain individually unconfirmed. |
| Single countdown through 23:59:59 | Shared 86,399-second limit, physical editor, USB validation and browser wheels are implemented. Zero and 24:00:00 are rejected. A full-length physical run was not reported. |
| Timer wheels | Hours/minutes/seconds, touch/mouse/keyboard operation and continuous digit scaling/fading are implemented. General interface acceptance reported. |
| Player layout | Previous / combined Play-Pause / Next, with Stop below. The latest recorded layout supersedes the earlier circular proposal; rotation and seeking are absent. |
| Alarm track audition | Test/Stop plays one selected track using alarm routing without saving the draft; `player_test` synchronizes the audition state, and `test_stop` affects audition only. General acceptance reported; exact output/priority combinations remain separate checks. |
| Four web clients | Four POST contexts, 48 KiB lwIP heap and ten configured TCP PCBs support the target; four stored browser authorizations remain a distinct limit. Real four-client/audio concurrency is not confirmed by the general report. |
| Browser About | Installed with separate approval on November 13. USB/HTTP metadata and preserved settings verified; the user subsequently accepted About on the phone. |
| Extended overview, substage 1 | Installed with separate approval. Eighteen tests, both builds, startup/HTTP and settings-preservation checks pass. The user subsequently accepted the general overview; individual ringing/snooze and network/output combinations remain focused checks. |
| Live alarm controls, substage 3 | User confirmed the three-minute repeat and cancellation on November 13; other focused cases remain separate. Stop, three-minute snooze and cancellation of snoozed repeats are implemented. Occurrence IDs and snooze-set revisions guard stale pages; existing command IDs/nonces guard retries. Nineteen tests and both builds pass; approved installation and startup/settings verification passed on November 13; user acceptance pending. |
| Quick controls, substage 2 | Explicit global sound on/off and time/date/nearest-alarm speech are implemented through the shared guarded application path. Nineteen checks and both builds pass; approved installation and startup/settings checks passed on November 13; the user confirmed general operation. Next-alarm wording is deferred for the audio refresh. |

Seventeen registered checks passed after the earlier clean local Debug rebuild on 2026-11-13. The later extended overview adds a native calendar/JSON test and passes eighteen checks, including production-script slider/overview and timer-wheel checks. This is software evidence; it does not establish real HTTP concurrency or radio/audio timing.

Remaining work, in recommended order:

1. Preserve an identified source revision and reviewed UF2 for each next build; installation always requires separate approval. Complete focused expanded-slot save/restart, four-client and audio-priority checks when the user is available; router outage testing remains deferred.
2. Quick controls (substage 2) are generally user-accepted. Preserve the separate focused test cases; defer next-alarm phrase replacement until functional development is complete and the audio assets are refreshed.
3. Countdown completion-audio Stop is generally user-accepted on `1.0.0+26.g3717033`; scheduled-alarm three-minute repeat and cancellation are also user-confirmed. Preserve separate focused cases for the installed alarm stop/three-minute snooze/cancel-repeat commands with stale-occurrence protection. The existing physical handlers remain the source of behavior.
4. Complete acceptance of the installed [scalar autosave/mobile fixes](WEB_SCALAR_SETTINGS.md); the user selected a temporary 4.1 kHz single cue from the working half-hour beep. Its repository asset is ready; installation on both cards and audibility remain pending. Wider audio investigation/redesign is deferred. Browser player mode/sleep is installed and generally user-accepted ([details](WEB_PLAYER_OPTIONS.md)). Automatic announcement/quiet-hour controls are installed and generally user-accepted ([details](WEB_ANNOUNCEMENTS.md)). Date/time and NTP requests are installed as `1.0.0+33.gc2dbec4`, with functional user acceptance pending ([details](WEB_CLOCK.md)). Browser Bluetooth management is installed; the user reported selection working with an apparent reload. The [reconnect layout fix](WEB_RECONNECT.md) is installed and accepted ([Bluetooth details](WEB_BLUETOOTH.md)). Preserve focused output/persistence checks for timer sound choices, random music and pre-warning.
5. Complete focused acceptance of installed [browser Bluetooth management](WEB_BLUETOOTH.md) with the accepted [reconnect layout fix](WEB_RECONNECT.md): saved/discovered speakers, scan/cancel, connect, disconnect and confirmed Forget. Audio preferences remain separate from connection.
6. Network stage 1 is installed as `1.0.0+37.ga1f576b`; the user accepted Direct and home transitions on November 15 ([details](WEB_NETWORK_MODES.md)). Browser permission listing and selective revocation are installed as `1.0.0+40.g9b20f8b`, with the +42 background-render hold accepted for Android picker stability ([scope](WEB_BROWSER_ACCESS.md)). Home Wi-Fi setup is installed in +43 and Main/Backup profiles with search in +44. Direct discovery is user-evidenced; the compact Connection UI is installed in +45; explicit saved-network Connect/Edit is installed in +46 and user-accepted for manual Main/Backup switching ([scope](WEB_WIFI_SETUP.md)); hardware transitions/save/recovery and resource acceptance remain separate.
7. OTA is the next approved development direction before presentation work. Feasibility is confirmed and the [A/B foundation](OTA_FOUNDATION.md) passed separately approved migration, rejection rollback, B acceptance and the user-reported power-cycle check on November 16. Settings preservation and active B were verified over serial/HTTP. The authenticated [browser uploader](OTA_WEB_UPDATE.md) passed 33 host checks, a separately approved sequence-4 USB receiver install/power-restart gate and the first Home HTTP transfer/validation/apply to accepted B sequence 5. The user confirmed web access recovery and normal operation after the requested sequence-5 power restart; serial/HTTP verified accepted B and an idle uploader. On November 19 the user completed a phone-browser Direct selection/upload/install to accepted A sequence 6, independently verified over serial/HTTP. The user confirmed its requested restart/sound/timer checks. Installed OTA restarts always return Home; the new sequence-7 sender adds one-shot origin-mode restoration and is now installed/accepted in B through Home. Its user functional/power-restart gate passed and accepted B was verified afterward. The user installed sequence 8 through Direct and then power-cycled; accepted A and Home were verified afterward. Immediate Direct return before power cycling remains unconfirmed. A new sequence-9 upload-feedback/duplicate-action candidate is uninstalled; next separately approve it and observe Direct restoration before any power cycle, then cover failure cases. Detailed progress rendering, concurrency, failure recovery and peak live memory remain unverified.
8. Implement final navigation/presentation, light/dark/system themes and EN/RU/DE interface localization. Keep speech language separate and all assets local. The [G1 interface redesign specification](WEB_UI_REDESIGN_SPEC.md) defines the complete control inventory, review gate, optimization targets and acceptance scenarios; design preparation does not authorize firmware installation. Automatic page recovery after OTA is deferred at the user's request.
9. Finish release evidence, resource/four-client measurements and English instructions, then prepare a separate web-control release. No merge into main or stable web release is implied by functional acceptance.

The [expansion specification](WEB_CONTROL_SPEC.md) records the implemented capacity/UI stage and links the broader follow-up scope. One-time reminders, track seeking and new display/audio hardware remain excluded from current implementation.

<a id="browser-bluetooth-management-planned"></a>

### Browser Bluetooth management

Installed as `1.0.0+35.g5c09045`; selection is generally working per user report, with the reload-like page failure resolved by the accepted [reconnect layout fix](WEB_RECONNECT.md). Focused real-device acceptance remains pending. See [commands, workflow and acceptance](WEB_BLUETOOTH.md). The checklist below is the stage scope; it is not evidence of hardware acceptance.

- Show up to four known devices and new discovery results by name; use a stable internal address for actions, not a changing row index. MAC addresses remain in internal identities and USB diagnostics.
- Scan with visible progress/completion and cancellation. Preserve the existing intentional disconnect/manual-OFF behavior when discovery starts; ending/cancelling discovery must not silently restore a speaker.
- Connect a known device directly without scanning, or select a discovered device for pairing/connection. Persist a newly selected peer only after its stream becomes active. Preserve known names and address deduplication.
- Disconnect while retaining the known entry and pairing key; keep OFF through autosave/restart until explicit Connect. Forget is a separate confirmed deletion of an entry/key.
- Reuse existing audio/timer/alarm guards, shared authorization, command serialization and retry protection. Audio-output preferences and separate volumes remain independent of speaker connection.
- When all four saved slots are full, require confirmed Forget of a named entry before browser connection to a new device. Physical/USB replacement policy remains unchanged. Keep current retry behavior; switch-latency optimization remains in the deferred tail.
- Use bounded responses for the device list, preferably separate from the already populated 4 KiB status response. Recheck peak memory and four-client contention.
- Accept with real saved/discovered Portable/Nest connections, cancellation, manual OFF, forget/save/restart, LOCAL fallback and status changes from physical controls. Do not claim support for BLE-only or legacy PIN-only audio devices.

Control restoration stage 1 is implemented. Hardware logs confirm accelerated selection, LOCAL timer start/finish/cancel and GP28 entry/back; remaining precise-field and player-mute checks are in TESTING.md. The user also confirmed timer routing to the selected Bluetooth speaker after changing its independent output preference.

Stage 2 playback/navigation was accepted by the user. Pause and sleep selection were subsequently reported working; full timed expiry and explicit output-specific coverage remain unconfirmed. Implemented controls include brand-neutral BT labels, normal/shuffle/repeat-one, immediate Next/Previous with bounded history, consistent physical controls and mode/count display. Position-preserving pause is now implemented for LOCAL/Bluetooth; the old MicroPython pause restarted the track.

1. Alarm snooze and weekday schedules are implemented and user-tested: Daily/Mon-Fri/Sat-Sun/custom days, GP28 three-minute snooze, explicit cancellation and Flash v9 migration. See TESTING.md.
2. Music sleep timer and position-preserving pause on LOCAL/Bluetooth are implemented. The user accepted pause, time selection and the explicit OFF field; full expiry and separate LOCAL/BT coverage remain acceptance checks. GP28 cycles OFF/15/30/60/90 minutes; TIMER pauses/resumes. Existing playlist modes and audio priorities are retained. See TESTING.md for checks on both outputs.
3. Spoken date, nearest scheduled/snoozed alarm and a nonblocking LCD startup/version splash are implemented and broadly user-accepted in build 02b4a51. Idle-clock MINUS short/hold and USB say-date/next-alarm expose date/forecast. Available year recordings cover 2023..2029; German alarm-slot phrases are absent. No new startup sound is queued. The two-page LCD About screen remains available.
4. Five annual birthday dates are implemented and broadly user-accepted in build 7964939; COM8 confirms configured dates saved in v10 and prior settings retained: menu/USB editing, persistent dates/handled years (Flash v10), existing 07/000.mp3 melody via Manual routing, idle/non-quiet delivery with 30-minute expiry. The user explicitly excluded one-time reminders because suitable spoken recordings are absent. February 29 matches only in leap years.
5. Offline RTC drift calibration remains conditional on measured need. The assembled board now has confirmed NTP synchronization and user-verified Bluetooth playback with Wi-Fi enabled. Next verify sustained operation/recovery, then compare a trustworthy reference over several days before choosing a drift rate. A fixed initial clock offset alone is not a rate measurement; the historical MicroPython calibration required at least five days between trusted references. No C drift correction has been added or enabled.
6. Complete the electrical schematic for the installed Pico 2 W wiring and power modules.
7. External LCD illumination on GP6 is implemented. The user confirmed ON/OFF, brightness adjustment, no audible interference and persistence after restart on build ab06727. AUTO time transitions are deferred at the user's request.

Each milestone requires focused tests and a hardware acceptance step. The statuses above distinguish implemented follow-up work from remaining plans; the first release candidate predates these follow-up changes.

## Deferred tail, in approved order

1. Investigate initial Bluetooth switch status 0x56 and optimize switching latency. Existing five-second retry is retained.
2. German spoken timer-completion phrase, last. The recording is currently absent. Keep the existing signal behavior until the correct recording is supplied and verified.

The intermittent double Bluetooth sound is deferred until the planned feature work is finished, at the user's request. The completed passive-capture findings remain in HARDWARE_TEST_EVIDENCE.md; the cause is unresolved.

## Existing behavior retained

Separate DFPlayer/Bluetooth volume levels remain intentional. MAC addresses remain internal identifiers and USB diagnostics; the LCD displays names. SD access remains read-only. SSP confirmation remains automatic, and legacy PIN-only speakers are unsupported.

## Future device hardware

Generation naming is installed as **Pi2Clock G1**, build `g1-accbeb708131-bt-mp3-wifi-phone-ota11-trial`; **Pi2Clock G2** is reserved for the successor. Model, Git-derived version and OTA sequence remain separate. G1 receivers validate the embedded target/prefix, while retaining the ota10 transition layout. Home installation, accepted B, settings preservation and restored Nest connection were verified on November 20. See [identity and release conventions](FIRMWARE_IDENTITY.md); the user confirmed the requested LCD/browser displays and normal playback on November 20.

On 2026-11-11, the user selected I2S audio through a MAX98357A amplifier as a logical direction for a likely new device with updated hardware. This is a future hardware milestone. Current web-control development continues on the assembled DFPlayer-based clock.

The proposed audio path is the Pico-connected SPI SD card, the existing software MP3 decoder, a PCM buffer, PIO/DMA I2S output and the MAX98357A speaker amplifier. A shared decode path could serve local audio and Bluetooth and consolidate audio assets onto one SD card. A separate hardware prototype should first verify available GPIO/PIO/DMA resources, amplifier power, speaker compatibility, memory use and sound continuity with Wi-Fi active. Exact wiring, resource allocation and performance remain to be measured.

### Generation 2: one-card audio and folder collections (2026-11-20)

The user explicitly deferred folder-based music collections to the second-generation device. Generation 2 is planned to replace DFPlayer with I2S/MAX98357A local output and use one shared SD card for local and Bluetooth audio, eliminating the current need to maintain two matching cards. This is a future implementation requirement, not a change to the assembled clock.

- Organize music into named folders/collections, for example Disco, Classical and Russian music. Allow selection and playback of one collection independently.
- Provide an All music selection that combines the music collections and supports shuffled playback across their tracks. Exclude speech assets, beeps and other system audio from this selection.
- Keep collection selection separate from playback order (sequential, shuffle and repeat-one); preserve useful Previous/Next history. Prefer a shuffled pass without repeats until the selected catalog is exhausted.
- Use the same catalog for local I2S output and Bluetooth. Numeric folder restrictions imposed by the current DFPlayer must not dictate the generation-2 folder layout.
- Define supported filenames/encodings, catalog limits, missing-file behavior, persistence and resource budgets during generation-2 design. Selection of arbitrary subsets of collections and editable playlists remain optional follow-up ideas, not committed scope.

Do not implement folder collections or migrate the current two-card audio layout as part of the present web-control/OTA work.
