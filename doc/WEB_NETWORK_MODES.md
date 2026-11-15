# Browser network modes: stage 1

Status: installed as `1.0.0+37.ga1f576b` on November 14; the user confirmed successful Direct and home transitions on November 15, 2026. Explicit cancellation, busy cancellation and four-client/resource acceptance remain separate checks. This stage adds state and HOME/Direct switching, not Wi-Fi credential editing or browser-access administration.

## Workflow

The Wi-Fi network panel shows current mode, saved home SSID, current address and the existing home join/address/retry/ready state. Connect directly and Use home network require browser confirmation and explain which phone Wi-Fi network and address to use next. The mode change is queued for five seconds later so the existing page has time to acknowledge it. Cancel switch can cancel during that interval. Repeated delivery of an accepted command does not restart the delay or switch twice.

The current page connection is expected to end when the radio changes mode. The page keeps the handoff instructions and destination link; it does not automatically navigate or change the phone's Wi-Fi. The user joins SpeakingClock for Direct and opens 192.168.4.1, or rejoins the saved home network and opens the last known home address. The home address is RAM-cached from a successful home connection and is explicitly last-known: DHCP can assign another address. Phone Control on the clock remains the address/recovery reference. Live join progress is available only while the page can reach the device; an offline source page cannot monitor the destination network.

The first Direct password must already have been created/saved by starting Direct once from the physical Phone Control menu. The browser disables Direct switching until that key exists. The existing LCD password display remains available; this stage does not publish the password over HTTP. Home switching requires saved Wi-Fi configuration. Remembered browser keys, home-trust policy, Wi-Fi credentials and the existing Direct key are retained. A browser not remembered in the destination mode may need the existing one-time physical pairing code. A changed home IP is a different browser origin and can also require remembered access setup when home trust is disabled. Reboot still starts in home mode as before.

## Admission and delayed application

Requests require idle timer/player/alarm/audio, closed physical editors and no Bluetooth inquiry. The main loop continuously rechecks the pending plan. If the clock becomes busy during the grace period, the plan is cancelled immediately and is not replayed when idle returns. An access epoch or physical mode change cancels it too. The existing main-loop `phone_web_set_direct` performs the eventual radio operation, preserving its Direct-start failure fallback to home mode. No sleeps are added to HTTP callbacks or the main loop.

Cancellation only cancels an outstanding request; it cannot undo a completed mode change after the connection has ended. A different mode request while one is pending is rejected rather than replacing another browser's plan. The same pending request/destination retains its original deadline. Failure/cancellation feedback is distinct from the current network mode. API acceptance means scheduling, not proof that a phone has joined or home Wi-Fi has obtained an address.

## Data and protocol

`network_control:true` advertises support. A separate no-store `/network.json` response, allocated within 2 KiB, carries epoch/published snapshot ID, mode/availability/configuration/key-ready flags, bounded home SSID/current/last-home address, home state/time and pending destination/countdown/result. It contains no Wi-Fi password or browser token. UTF-8 SSIDs use bounded escaping shared with device names; destination links accept only numeric IPv4 addresses. Failure of this optional response disables network actions without hiding timer/alarm controls or collapsing the page.

The authenticated same-origin `/network` commands are `home 0`, `direct 0` and `cancel 0` in the existing token/epoch/ID/nonce envelope. The main-loop plan captures the current epoch and source mode. A fresh published network snapshot is required for acknowledgement. On address/access reset the published availability and snapshot IDs are cleared until main-loop republication. Four POST contexts and existing retry/conflict rules are retained. No Flash schema, password, browser registry, timer/RTC or Bluetooth policy change is introduced. Network plan/last-home-address state is RAM-only.

## Verification and hardware acceptance

Native tests cover once-only delayed execution, preserved deadline on duplicate scheduling, opposite-request conflict, explicit cancellation, immediate busy cancellation, epoch/mode changes, 64-bit uptime and no replay. Request tests cover scopes/endpoints/value bounds and retry idempotence. Serializer tests cover maximum SSID escaping/UTF-8, response bounds and absence of secret fields. An actual-main-handler fixture covers setup prerequisites, Bluetooth/audio busy guards, delay, epoch cancellation and failed low-level switching.

Production-script tests cover confirmation, countdown, retained handoff after status loss, destination links, cancellation/busy feedback, missing key/configuration, invalid home address, optional-list failure and old/foreign-epoch metadata. Chrome fixtures at 360/412/960 CSS pixels with enlarged text verify native confirmation, instructions during simulated disconnection, no automatic document navigation, both destination links, cancellation and failure isolation. Both firmware profiles build. Radio handoff, destination pairing, resource margins and four real clients remain hardware checks.

After separately approved installation, refresh once and check the displayed SSID/address against Phone Control. First schedule Direct and cancel within five seconds; verify the home page stays reachable. Then switch to Direct, manually join SpeakingClock with the saved password and open 192.168.4.1; confirm remembered access and ordinary timer/player status. Return to the home network using the instructions/last-known link and confirm NTP recovery. Check that a pending switch is cancelled if a physical timer starts or editor opens, without interrupting that activity. Restore intended mode/settings. No radio-mode or sound command is sent during installation verification. Credential test/rollback and individual browser-access management are later stages.

## Compact UI follow-up candidate

The current candidate groups mode, saved-network setup and browser access into one Connection section. Only the applicable mode action is shown; setup/access disclosures are collapsed until needed. During a handoff the common status replaces the saved-profile editor and clears old ready/address information. Offline countdown expiration asks the user to reconnect, without inferring success or claiming endless progress. This changes presentation only; the stage-1 delayed switching, radio admission, authorization and firmware-owned recovery remain. See [Wi-Fi setup](WEB_WIFI_SETUP.md#compact-connection-interface-candidate) for exact behavior and pending hardware acceptance.

## Explicit saved-network selection candidate

Version +45 compact UI is installed. The next candidate uses explicit Connect/Edit rows for Main and Backup, available from both modes for Connect. On a supporting client, those rows replace generic Use home network in Direct so returning home has an explicit target. Connect directly remains the Home-to-AP mode action. Priority, saved credentials and Home trust are unchanged by a saved Connect. Source-aware rollback and detailed acceptance are documented in [Wi-Fi setup](WEB_WIFI_SETUP.md#explicit-saved-network-connect-candidate).
