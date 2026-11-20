# Bluetooth music interruption and continuation

Status: installed with separate approval as sequence 12 on 2026-11-20; startup/settings checks passed, music interruption hardware acceptance is pending. The user requested interruption for both hourly time speech and scheduled alarms, then explicitly limited this stage to Bluetooth music. Local DFPlayer music retains its existing behavior; no ADVERT folder or card modification is required by this stage.

## Behavior

When ordinary music is playing through Bluetooth, an eligible hourly **VOICE** announcement or due alarm suspends that track, plays the existing event plan, and restores the music context. The track number, playlist/history, resampler phase, decoder state and queued PCM are retained. This is not a seek approximation or a restart from the beginning. Output preferences remain independent: the event can use Bluetooth or its configured local/fallback route while the Bluetooth music is suspended.

Hourly auto-enable, sound, quiet-hours, RTC boundary deduplication, the five-second late window, timer priority and editor guards remain authoritative. Hourly chimes and half-hour beeps still do not interrupt the player. Alarm speech, signal/fixed/random track choice, due time, collisions, snooze and safety timeout remain unchanged. A queued alarm prevents a brief music restart between two events. Alarm audition is not treated as resumable ordinary music.

After an alarm finishes or is stopped, music resumes if its context is still valid. Snooze allows music to continue during the three-minute wait; a later ringing occurrence interrupts it again. A manually paused track returns paused. Pressing the physical player pause control during an announcement requests that it stay paused afterward. Player Stop/exit, global Sound off and sleep expiry discard the held music context. Player Stop/exit and sleep expiry leave the event audio to its owner; Sound off retains its global suppression behavior. Sleep retains its original wall-clock deadline throughout the interruption.

If the Bluetooth link/rate is unavailable at restoration, or the source file cannot be reopened/searched, the snapshot is discarded and the player stays paused/stopped for explicit user action. Do not automatically restart that track on the local speaker. If snapshot allocation fails, hourly speech is skipped with a diagnostic and music continues. An alarm retains priority: the existing stop/preemption path remains its fallback when music cannot be protected.

The browser keeps the player visible as Paused and publishes `player_interrupted=true`. It explains the interruption, disables conflicting transport/mode/sleep edits and retains Player Stop. Alarm Stop/Snooze remain independent controls. LCD shows Hourly speech / Music paused BT during hourly speech and the existing ringing-alarm screen during an alarm. UI redesign work must preserve this state and distinguish cancelling music continuation from stopping the event.

## Ownership and resources

One temporary checkpoint owns the suspended decoder's allocated buffers. Notification playback uses a separate decoder; the same stable read callbacks are used sequentially. The source file is reopened and its read cursor restored before music decoding continues, retaining decoder read-ahead and partially decoded frames. The original PCM ring and sample counters are restored after the event. No second checkpoint is taken for a nested/queued event.

The ring checkpoint is a bounded heap allocation (32844 bytes in host tests), not a large stack temporary or permanent BSS buffer. Additional notification decoder allocations coexist with the retained music decoder for Bluetooth event audio. Actual peak heap and radio/audio continuity require hardware measurements. On allocation/read failure the code takes the defined fallback rather than promising continuation. No SD reads, decoder work, allocation or snapshot copy is performed inside the A2DP consumer callback; sample copying occurs with its ring paused and short metadata changes protected by IRQ critical sections.

All continuation state is RAM-only. No settings schema, Flash sector, saved volume, output preference, audio file or persistent playlist is changed. A restart does not restore a music session.

## Software checks

`mp3_interrupt_test` exercises the production playback/checkpoint and PCM-ring code with a deterministic decoder/file fixture. At both 44100 and 48000 Hz it compares the resumed PCM stream with uninterrupted output, including resampling phase and buffered frames. It also checks allocation failure without disturbing music, a track paused before interruption, a new keep-paused request, reopen failure, cancellation while the notification decoder remains active, and an EOF tail whose decoder was already closed. This fixture validates ownership/continuity logic, not the Helix codec's physical playback or live radio timing. Browser regression checks cover interruption feedback and guarded player options.

Both ordinary and A/B OTA firmware builds must pass before a candidate is offered for separately approved installation. The latest reviewed package/build and test totals belong in the installation evidence after preparation.

### Prepared candidate on 2026-11-20

All 34 registered host tests passed; the expanded browser transport-state fixture also passed after its final update. Ordinary MP3/Bluetooth/Wi-Fi/phone-web and A/B OTA SDK builds completed without reported compiler warnings/errors. The reviewed, uninstalled package is `Pi2Clock-G1-v1.0.0+66.g4d2fcef-ota12.clockota`, build `g1-4d2fcef70d40-bt-mp3-wifi-phone-ota12-trial`, sequence 12, 1009804 bytes, SHA-256 `f70adb6ef89d85f6930bdad3008247fe8068c55ca42fe563608a6e0ecd993c57`.

Against the reviewed ota11 ELF, linked text increased by 3136 bytes and BSS by 164 bytes (185200 to 185364). This small static delta does not include the temporary 32844-byte ring checkpoint and simultaneous decoder heap allocations. Peak live memory remains a device acceptance check; no heap/TCP/stack limits were enlarged. Host PCM comparisons use a deterministic decoder fixture and do not establish audible continuity on Portable/Nest.

### Approved Home installation on 2026-11-20

The reviewed ota12 package above was uploaded from Home at 192.168.2.116 after player stop and temporary Nest disconnection. Transfer and verification reached ready in 64.9 seconds; explicit apply restarted into Home. Serial/HTTP confirmed version `1.0.0+66.g4d2fcef`, build `g1-4d2fcef70d40-bt-mp3-wifi-phone-ota12-trial`, active A, trial=NO, accepted=YES, Flash guard=OK and idle sequence 12. NTP synchronized. Nest was explicitly reconnected with an active A2DP stream and completed settings autosave.

Before/after snapshots matched all exposed persistent setting values, five alarms, fifteen birthdays, display light, four known speakers and the restored Nest target. Volumes remained LOCAL 16/30 and BT 15/30; light remained ON, day 93%, night 94%. HTTP confirmed `player_interrupted=false` at idle and the installed interruption feedback text. COM8 was released, music remained stopped, and no actual hourly/alarm interruption test was triggered by the installer. Decoder snapshot allocation, audible continuation and peak live memory remain user/device checks.

## Device acceptance after installation approval

1. Check G1 build identity, valid accepted partition/settings and unchanged volumes, routes, alarms and birthdays. Release COM8 after any capture.
2. Start a long Bluetooth music track on Portable or Nest. Test a scheduled hourly VOICE boundary with no colliding alarm, or use `auto-voice-play HH`: this new USB command plays actual audio through the same normal guards/routing, without changing the RTC or scheduler boundary history. It requires VOICE mode, auto-enable, Sound on and a non-quiet supplied hour. Existing `auto-test HH MM` remains a silent simulation.
3. Verify the announcement and continuation of the same track near the interruption point, without restart or unintended Next. Repeat with hourly output configured local while the music is Bluetooth.
4. Test a real due alarm, or the existing `alarm-pending-test N` command. Verify the configured alarm plan, Stop and three-minute Snooze, music continuation, and a second interruption when snooze becomes due. Preserve saved schedules; tests must not rewrite the RTC merely to make an event occur.
5. Repeat with music manually paused first; it must remain paused after the event. During an announcement use physical Pause, then verify no automatic playback. Test Player Stop/exit and Sound off during an event: the saved track must not resurrect. Event Stop and Player Stop have different meanings.
6. Test sleep expiry during a longer event, multiple queued alarms, Bluetooth loss/recovery and failure to reopen the source. Confirm defined failure behavior, responsive controls and no reset/leaked context. Measure live peak resource margin under the web/radio workload; do not infer it from linked BSS.
7. Repeat representative cases with Portable and Nest and inspect PCM diagnostics for ownership faults/underruns. Speaker latency and any already queued Bluetooth frames are hardware observations, not proof of a different source-track position.
