# Pi2Clock G1 web interface redesign specification

Prepared on 2026-11-20 for design review and subsequent staged implementation. The approved layout and its implementation are described in [WEB_UI.md](WEB_UI.md).

## 1. Objective and authorization

Create a modern, clear and responsive local control interface for the existing **Pi2Clock G1** speaking clock. Optimize everyday use from a phone while retaining full tablet/desktop operation, physical controls and reliable audio. Replace the long technical control page with a coherent product interface; preserve its working device behavior and access policy.

This task currently authorizes preparation of the specification. The next implementation task must begin with a design proposal and reviewable prototype. Obtain approval of the visual direction before integrating it into firmware. Each device installation needs separate approval; after installation, report verification, release COM8 and stop for user testing.

Apply the available frontend-design workflow during design and implementation. Use the current source as the authority for commands and guards; older documentation contains historical acceptance statuses.

## 2. Baseline and fixed scope

The accepted baseline is firmware `1.0.0+61.gaccbeb7`, build `g1-accbeb708131-bt-mp3-wifi-phone-ota11-trial`, on branch `codex/phone-control`. Later commits record acceptance. Preserve this traceable baseline and recheck the checkout before starting implementation. Do not merge into main, publish releases, assign version tags or install firmware as part of the design task.

G1 uses Pico 2 W, an LCD1602, physical buttons/encoders, DFPlayer for local sound, a separate SPI FAT32 card/software MP3 decoder for Bluetooth audio, Wi-Fi/NTP and an A/B updater. The two cards require matching audio assets. The web interface is served by the clock and must work without internet, a cloud account, an external service or a router when Direct is used.

Current capacity is one countdown timer, five scheduled alarms, fifteen annual birthdays, four saved Bluetooth peers, two saved home Wi-Fi profiles and four remembered browser permissions. Four simultaneous browser clients are a separate required workload; configured limits do not prove concurrency acceptance.

Do not add G2 hardware, I2S/MAX98357A, one-card migration, folder collections/playlists, seeking, streaming services, one-time reminders, new speech recordings or new alarm/timer counts. Preserve deferred audio investigations. Automatic page recovery after OTA is deferred by the user; the redesign must provide clear manual recovery instructions without claiming to fix it.

## 3. Product and visual direction

Design a calm, legible instrument interface appropriate to a physical clock with a metal front panel and rotary controls. Give time, active timer and urgent audio actions a clear hierarchy. Avoid marketing sections, decorative dashboard statistics, oversized empty cards and unrelated imagery.

Prepare a small design system with named color tokens, type scale, spacing, component states and light/dark equivalents. Use system fonts with good Latin/Cyrillic coverage and tabular numerals for changing time values. Favor restrained surfaces, clear grouping and one purposeful accent. Use small local SVG/CSS icons where useful, with accessible names; do not require icon fonts, downloaded typefaces or images.

Recommended navigation for the prototype:

| Primary destination | Content |
| --- | --- |
| Home | Clock, important status, quick actions and urgent event controls |
| Timer | Countdown, duration and completion options |
| Player | Transport, playback mode, sleep and output/volume access |
| Events | Alarms and Birthdays as two clearly distinct subviews |
| Settings | Sound, announcements, display, Bluetooth, network/access, date/time, update and About |

Validate the five-destination structure in the prototype. On phones use thumb-accessible navigation with short labels; on larger screens adapt to a side/top arrangement without duplicating controls or network polling. Provide direct access to active timer/alarm actions from any destination. Settings subviews should avoid a second long page of expanded technical instructions.

Browser Back should navigate local views rather than accidentally submit forms. Preserve section, scroll and drafts when appropriate. Use local view changes without full page reloads. Show short contextual help beside relevant controls, with advanced details collapsed.

## 4. Functional screen requirements

### Home and urgent actions

- Show device time, date/weekday, global sound state and current activity. Time shown is the clock's Europe/Berlin time, not an unlabelled copy of phone time.
- Show the active timer, next alarm, ringing/snoozed alarm state, Bluetooth name/state, current network mode and time-sync condition. Keep detailed diagnostics in secondary views.
- Provide global sound on/off, Speak time, Speak date and Speak next alarm using existing commands. Preserve current recordings, including the imperfect next-alarm wording; do not rewrite audio behavior to match new UI copy.
- Distinguish Sound off, zero volume, quiet hours, paused automatic announcements and paused music. They are different states and must not share a misleading mute indicator.
- For a ringing alarm expose Stop and Snooze 3 min. For snoozed occurrences expose cancellation of repeats. For countdown completion expose Stop timer sound. Do not confuse these with Cancel countdown or Stop player.
- Urgent controls must follow live ownership IDs and remain reachable without navigation or page reload. Show only actions supported by the current device state; never claim that a stale action stopped a later event.

### Countdown timer

- One shared device timer, from `00:00:01` through `23:59:59`. Reject zero and `24:00:00`; no per-browser timer instances.
- Retain three hours/minutes/seconds wheels with touch, mouse and keyboard operation, readable selected digits and accessible bounds. Provide an equally usable keyboard/input fallback where needed. Browser animation must not cause radio traffic.
- Separate an edited duration, the applied setting and the running remaining time. Preserve Set/Start/Cancel semantics. Do not implement a combined set-and-start transaction by silently sending two independent commands.
- Present completion message as an independent switch and additional sound as None / Signal / Music. Music supports fixed track 1..255 or Random. Allow message only, sound only and silent completion; disable irrelevant fixed-track controls without discarding the remembered track.
- Include optional last-five-second beeps, default behavior unchanged. Preserve busy/late-tick skips and completion priority. Audio-file replacement and loudness diagnosis are separate work.
- Keep timer output preference visible or directly reachable. Sound off continues to override audio. The missing German completion recording must not be presented as available speech.

### Music player

- Previous / combined Play-Pause-Resume / Next in one row, with Stop clearly separated below. Ordinary buttons are required; no wheel gesture or track seeking.
- Show actual selected track number/count, playback state, effective output and selected Bluetooth name when supplied. Do not invent track titles, artwork, duration or progress where the API has none.
- Preserve Normal / Shuffle / Repeat one, actual navigation history and current-track continuity when switching modes.
- Sleep choices are Off / 15 / 30 / 60 / 90 minutes. Show remaining time and explicit Off. The existing timer continues through pause/mute; Stop closes the player and clears sleep. Mode/sleep are runtime options and are not saved across closing/restart.
- Reflect changes from physical controls and other clients. Keep alarm-track audition distinguishable from ordinary music; do not expose invalid player options during audition.
- Preserve the subsequent [Bluetooth interruption state](BT_MUSIC_INTERRUPTION.md): `player_interrupted` keeps music paused for hourly speech/alarms; Player Stop cancels its continuation without stopping the event. Local DFPlayer continuation is excluded from that stage.

### Alarms and birthdays

- Present a compact overview of five alarms, then edit a selected record. Include enabled state, time, Daily / Mon-Fri / Sat-Sun / custom weekday selection, Signal / specific Music / random Music and fixed track when applicable.
- Keep Test/Stop beside fixed-track selection. It auditions one track without saving the draft; its state follows actual audition ownership. No audition is offered for an unspecified random track.
- Fifteen birthday records support enabled state, annual date, announcement time and optional birth year. Accept `DD.MM` and `DD.MM.YYYY` without forcing a fake year. Both recur annually; February 29 occurs in leap years. Birthday names, ages and custom recordings are not current device fields and must not be invented.
- Use one explicit Save per complete alarm/birthday draft, with clear discard/reload behavior. Changing slot, section, language or theme must not silently save or lose an edited record.
- Preserve record revision/conflict checks. If another browser or physical editor changes the record, explain the conflict and offer reload/review; never overwrite silently.

### Sound, display and announcements

- Keep independent local/SPK and Bluetooth volumes, each in 0..30 steps. Use responsive sliders and a visible value; any percent presentation must map consistently to those 31 values. Do not couple the two levels.
- Global mute is separate from volume. Maintain four independent output preferences: manual speech, hourly speech, timer and alarm. Their choices are SPK and Bluetooth preferred; show actual SPK fallback when Bluetooth is unavailable. Connection selection is separate from routing.
- Show manual output as SPK in user-facing copy, while retaining existing LOCAL values in the API. Use BT without JBL branding. Do not imply that local volume controls an external speaker or that every speaker supports Bluetooth absolute volume.
- Display light has Off / On / Auto and separate 0..100% day/night brightness sliders. Preserve the fixed Auto night period 22:00-07:00 and independence from audio quiet hours. Do not add a custom schedule.
- Automatic announcements include the temporary until-restart enable switch, hourly speech/chime mode, half-hour double beep and exact-hour wording. Label the temporary switch accurately; do not turn it into a persistent setting.
- Quiet hours use existing whole-hour start/end values, support overnight ranges and label equal start/end as all day. Quiet hours suppress automatic announcements and defer birthday delivery for its existing maximum 30 minutes; they do not suppress manual speech, music, timers or scheduled alarms.
- Scalar options apply automatically through the existing guarded queue. Sliders update during interaction with bounded/coalesced requests, and finish with the final value. Remove per-field Apply buttons here, while retaining explicit Save for multi-field records and confirmation for disruptive actions.
- Distinguish command pending, applied in RAM, waiting for Flash save, saved and failed. The normal five-second autosave delay and up-to-60-second write cooldown are not a hung interface. Do not write Flash on every slider step.

### Bluetooth

- List known and discovered devices by friendly name, with connected/connecting/off states. MAC addresses stay internal or in optional diagnostics, not primary labels.
- Provide scan/cancel, direct connection to a known peer, connection to a discovery result, disconnect and confirmed forget. Four saved peers is the limit; require deliberate Forget before adding another from the browser when full.
- Connect must actually connect; selecting a row must not merely change an invisible edit target. Keep selection and action visually clear.
- Scanning disconnects the current peer. Finishing/cancelling scan does not reconnect automatically. Disconnect preserves pairing and persistent manual OFF until explicit Connect. Forget deletes the selected peer/key.
- Respect existing playback/timer/alarm/editor guards and reconnect policy. Explain a disabled action by the actual reported reason. Do not optimize speaker switching or change pairing security as part of presentation work.

### Network and browser access

- Clearly distinguish Home via router and Direct via SpeakingClock at `192.168.4.1`. Internet is unnecessary for local control; NTP may be unavailable offline.
- Main and Backup each show saved SSID and current status. **Connect** switches now; **Edit** changes credentials. Selecting/editing Main must not silently change connection or priority. Main remains first at startup, Backup fallback; no automatic roaming based on signal.
- Preserve Direct-only credential editing, discovery, manual SSID input, typed-password Show/Hide and open-network handling. Never retrieve/display saved passwords; Show reveals only text being entered. Hide it when appropriate after leaving the editor/backgrounding.
- New credentials use the existing five-second cancellation window and up-to-45-second join/IP test. Retain old profiles on failure and show how to return to SpeakingClock. Saved-profile connection and editing are separate flows.
- Show transition progress, destination address and the next user action. The phone may switch to home Wi-Fi when Direct disappears; the web page cannot control the phone's Wi-Fi selection. An old Home address may change and must not be presented as guaranteed.
- Preserve remembered browser admission, pairing-code flow, trust rules and exact request-origin validation. Wi-Fi password and browser pairing code are different credentials. Do not introduce daily passwords or a new login/session timeout.
- List up to four saved browser permissions, with scope/current-entry identification, confirmed revocation and the existing trusted-Home explanation. They are not four online phones. Global trust changes and forget-all remain physical controls where currently required; do not invent browser endpoints.
- Changed network credentials disable Home trust according to the current backend. Signing out or forgetting one permission does not necessarily block access through a trusted Home network; UI wording must reflect this.

### Date/time, firmware update and About

- Retain manual date/time review and confirmation, Use clock time, Use phone time converted to Berlin, and NTP synchronization. Manual settings may later be corrected by NTP. Do not add arbitrary time zones or drift calibration.
- Keep firmware file selection, reading/preparing, upload, verification, ready, explicit Install and restart, restart/reconnection, cancellation and error states distinct. Show immediate feedback before the first network acknowledgement; use indeterminate progress when the amount of work is unknown.
- Never interpret upload completion as installation success. Prevent duplicate Upload/Install and never replay them automatically after reconnection. Retain session ownership, 120-second receiving/ready timeout and newer-sequence enforcement.
- Display current model, version, build, OTA sequence and selected-file identity. Preserve G1 target/prefix checks and refusal of incompatible generations. Do not add G2 packages or change the package format.
- Explain that normal power-on/restart uses Home, whereas supported OTA restores the originating mode once. In Direct explain manual phone reconnection and page refresh if needed; automatic page recovery remains deferred.
- Explain that ordinary controls/scheduled sounds pause during active update and power must remain connected. Respect all backend prerequisites, including stopped audio, disconnected Bluetooth and saved settings. Show actionable reasons instead of unexplained disabled buttons.
- About includes Pi2Clock G1, Pico 2 W, actual Git-derived version, build, OTA sequence and FlintUA. Keep system detail here rather than scattering build strings throughout routine controls.

## 5. Themes, language and accessibility

Provide Light / Dark / System appearance and EN / RU / DE interface language. Store these preferences in the browser, independently per browser, without adding device Flash writes. If browser storage is unavailable, keep a working session/default and continue rendering. System theme follows browser preference only while System is selected.

Interface language must not change the device's RU/DE speech language or recordings. EN speech is not implemented. Translate labels, validation, empty/error/busy states, confirmations, accessibility text and dynamic messages. Keep machine enums, command names, ownership IDs and protocol values unchanged. Preserve names/SSIDs as supplied. Use text-safe DOM updates for remote strings; do not insert them as HTML.

Use semantic HTML, labelled controls, keyboard navigation, visible focus, non-color state indicators, sufficient contrast and screen-reader-friendly status announcements. Target 44-48 CSS px touch areas with clear separation. Support 320/360/393/768/1280 px widths, landscape and 200% zoom without losing essential controls or horizontal page scrolling. Long German labels, Cyrillic names, SSIDs and build strings must wrap sensibly. Respect reduced-motion preference; do not announce every ticking second to screen readers.

## 6. Live state and command integrity

The device is authoritative. Distinguish requested, acknowledged and persisted values. Local clock/timer interpolation may improve visual smoothness but must be labelled stale and reconciled to device snapshots; it must never create alarms or audio locally.

Preserve authentication, boot epoch, command IDs/nonces, idempotent retries, per-record revisions, occurrence IDs, input bounds, conflict results and backend guards. Preserve pending scalar reconciliation and blocking of dependent commands while settings are unresolved. Do not weaken a safety guard to make a button appear usable. Explain why an action is unavailable and how to resolve it.

Use one shared network coordinator across views, with bounded requests, no overlapping status loops and no per-widget polling. Reopening a view must not attach duplicate handlers or start another timer. Out-of-order/pre-reboot responses must not overwrite newer state. Disconnect and visibility changes must not replay destructive or uncertain actions.

Patch only changed DOM values. Do not rebuild focused native selects, permission/speaker lists, timer wheels or edited forms on each poll. Preserve the accepted Android picker anti-flicker behavior, focus, caret, scroll, local drafts and dragged slider values. Update unrelated state without tearing down an open editor. State changes from encoders and other clients must reconcile correctly after editing ends.

Use a persistent connection/status area: connecting, live, command pending, network switch, reconnect required and unavailable. Avoid transient errors that immediately disappear on the next poll. No full page reload on ordinary controls, speaker/profile selection or settings changes.

## 7. Optimization and resource constraints

Current source measurements/configuration, not guaranteed live free memory:

| Item | Baseline or constraint |
| --- | --- |
| Current HTML/CSS/JS source | 126585 bytes, about 123.6 KiB, before redesign |
| Clock Flash / application slot | 4 MiB board Flash; each OTA application slot is 1536 KiB |
| Reviewed ota11 payload | 1006540 bytes, excluding its 128-byte package header |
| Network heap | 49152 bytes in the phone-web configuration |
| TCP PCB configuration | 10 |
| POST contexts | 4 bounded contexts; not four independent command engines |
| Dynamic HTTP response allocation | 4096 bytes normally, 2048 network/Wi-Fi, 1024 browser/self, including header/body as implemented |
| Main stack configuration | 4096 bytes |

Use plain HTML/CSS/JavaScript with no runtime framework, CDN, external font, analytics, cloud API or mandatory service worker. A local build-time bundler/minifier is optional; the firmware must serve the generated static assets directly from Flash. Keep editable source readable and generation reproducible. Do not allocate the UI in MCU RAM per client. Do not move settings or assets onto SD as an unreviewed storage redesign.

Proposed engineering targets for review: combined uncompressed production web assets at most 160 KiB, with the existing 123.6 KiB as the optimization baseline; additional firmware static RAM no more than 8 KiB for this presentation change. These are targets, not measured results or permission to consume all available slot space. Report a justified exception before adopting a larger design. Measure final linked firmware, generated assets and actual peak/low-water resources; free RAM cannot be inferred from BSS alone.

Do not silently increase the network heap, stack, TCP or POST limits. Avoid changing response schemas; if a field is necessary, document the addition, test maximum serialized responses and account for all simultaneous allocations/TCP copies. Keep the existing bounded command body limits and OTA chunk transport; never buffer an entire firmware image in device RAM.

Current polling uses about one second normally, 250 ms for imminent/active timer or ringing events, and short acknowledgement polling while a command is pending. Optimize around these needs rather than assigning each view its own timer. Poll small status needed for live controls; refresh Wi-Fi scans, browser registries and full device catalogs on relevant views/actions/revision changes instead of on every tick where safe. Never hide urgent alarm/timer state by suspending all updates to a nonselected view. Use bounded backoff on failures/backgrounding, quick resynchronization on return and correct treatment of uncertain commands.

Do not replace polling with WebSockets/SSE or add push infrastructure without separate resource analysis and approval. Compression/caching is optional only after verifying actual server support; do not assume gzip/Brotli or add stale service-worker caching. Version static assets if caching is introduced, and keep status/commands fresh after OTA.

Measure HTTP request rate, simultaneous connections, response sizes, load time, browser DOM/listener growth and audio behavior. New themes/languages must not create additional device polling or per-client server rendering. Audio decoding, timer/alarm priorities, radio stability and OTA correctness take precedence over decorative animation.

## 8. Implementation stages and deliverables

1. **Inventory and baseline:** map every current visible control to its endpoint/status field, guards, persistence and tests. Measure resource/request baselines and identify obsolete documentation. Produce the mapping alongside the design, without changing behavior.
2. **Design review:** deliver tokens, navigation, component/state rules and a local interactive prototype using real G1 content. Show Home, Timer, Player, an event editor and Connection/OTA states in both themes, including a narrow phone and long German text. Mock state must be explicitly labelled. Obtain user approval before firmware integration.
3. **Shell and preferences:** integrate navigation, themes and UI translation while retaining the shared transport/state layer. Test drafts, keyboard access, physical changes, reconnects and native picker stability.
4. **Daily controls and events:** migrate Home, Timer, Player, Alarms and Birthdays in reviewable groups. Keep urgent controls globally accessible and all existing behavior intact.
5. **Settings and system:** integrate sound/announcements/light, Bluetooth, Main/Backup/Direct, browser access, date/time, OTA and About. Preserve all existing handoff/access constraints.
6. **Optimization and acceptance:** remove redundant polls/DOM work/assets, measure resource deltas and run regression/concurrency tests. Document results, unresolved checks and exact candidate build. Prepare a versioned G1 package; installation remains separately approved.

Deliver readable source and any reproducible asset-generation command, the control/API map, updated English documentation, focused regression tests, representative screenshots and a concise before/after resource report. Keep changes on a suitable `codex/` branch based on the accepted development branch. Do not create a parallel competing backend or rewrite audio/settings engines for UI convenience.

## 9. Acceptance criteria

- Every current function listed above remains reachable, with no invented capabilities. Everyday actions are understandable without reading technical paragraphs.
- Phone layout, both themes and all three UI languages pass screenshot and interaction review. Labels and controls do not overlap; active native selectors do not flicker; section changes preserve the correct drafts and scroll.
- Volume/brightness apply smoothly without request storms or excessive Flash writes. Saved feedback distinguishes runtime application from durable save, including write cooldowns.
- Actual countdown completion can be stopped and actual alarms can be stopped/snoozed from any view without a reload. Stale ownership/revision requests cannot affect a newer event or overwrite another client's changes.
- Four real clients are tested with overlapping commands, active Bluetooth music and physical input. Record device resources, defined conflict/busy behavior and absence of duplicate commands, lost admission, response corruption, audible degradation or resets. Repeat relevant scenarios in Home and Direct; stored permissions are not concurrency evidence.
- Test network loss, background/foreground, rejected changes, invalid dates/ranges, missing assets/status fields, full Bluetooth/browser registries, wrong-generation/old OTA files and uncertain update results. Keep user-deferred hardware fault tests marked deferred; do not claim they passed.
- Existing host tests remain valid and pass; add meaningful coverage for translations, themes/storage fallback, navigation lifecycle, picker/draft preservation and changed request coordination. Build both ordinary and OTA profiles. Do not accept checks that only search for CSS strings as proof of functioning controls.
- No release or resource-margin claim without the supporting measurements. Each approved hardware installation ends with exact identity/settings/startup verification, COM8 release and a pause for user acceptance.

## 10. Source map

Start with `firmware/pico2w_c/services/phone_web/index.html`, `phone_web.c`, `phone_access.c`, `phone_control.c`, `phone_bluetooth.c`, `phone_network.c`, `phone_wifi.c`, `lwipopts.h` and `main.c`. Tests are under `firmware/pico2w_c/tests`.

Use [control specification](WEB_CONTROL_SPEC.md), [controls and modes](CONTROLS_AND_MODES.md), [player options](WEB_PLAYER_OPTIONS.md), [scalar settings](WEB_SCALAR_SETTINGS.md), [announcements](WEB_ANNOUNCEMENTS.md), [Bluetooth](WEB_BLUETOOTH.md), [Wi-Fi setup](WEB_WIFI_SETUP.md), [browser access](WEB_BROWSER_ACCESS.md), [OTA](OTA_WEB_UPDATE.md), [firmware identity](FIRMWARE_IDENTITY.md) and [roadmap](ROADMAP.md) as supporting references. Reconcile historical pending/installed notes against current source and acceptance evidence before turning them into new tasks.
