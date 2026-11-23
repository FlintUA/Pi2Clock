# Stable layout while reconnecting

> **Release `g1-v1.1.0` (2026-11-23):** this feature is part of the release. This note records its design, implementation and installation history; "pending" or "candidate" below refers to the date it was written. Current behaviour: [controls and modes](CONTROLS_AND_MODES.md) and [phone interface](WEB_UI.md); acceptance: [feature status](FEATURE_STATUS.md).

Status: installed with separate approval as `1.0.0+36.ge21b139` on November 14. Startup/settings/page checks passed, and the user confirmed speaker changes no longer refreshed the page. The reported page-jump workflow is accepted.

## Report and reproduction

After installing Bluetooth controls as `1.0.0+35.g5c09045`, the user reported that device selection worked but the browser appeared to reload the entire page. No location/reload command or automatic form submission exists in the current speaker actions. A Chrome fixture reproduced a specific reload-like failure: one failed ordinary status request hid all authorized control panels, reducing document height from 8,474 to 786 CSS pixels and clamping scroll from 5,380 to zero. Navigation timeOrigin and document request count remained unchanged. This proves the layout-collapse defect; it does not prove whether the user's phone also performed an actual navigation or why its network request failed.

## Corrected behavior

A failed status poll after an authorized page was shown preserves panel visibility, the last received display values, selected speaker and unsaved drafts. It disables inputs/buttons and timer-wheel interaction, marks the displayed values as stale and continues the existing background status recovery. No command may use stale state. Fresh successful status rechecks authorization, device state, command acknowledgement and all normal guards before re-enabling controls. A current response that removes authorization, or explicit local authorization removal, still hides panels. Failed initial connection before authorization does not reveal control panels.

This keeps viewport context rather than forcing scroll back to the collapsed top. Last received time/status must not be mistaken for a live reading; the connection message explicitly identifies it. Bluetooth-list-only failures retain their existing isolation from timer/alarm controls. No firmware Bluetooth policy, credentials, API, Flash format, audio behavior or retry identifiers are changed.

## Verification and acceptance

The production-script tests now verify persistent visible panels with disabled actions during a failed poll, no command sent from those controls, preserved speaker/clock drafts, successful recovery and genuine authorization removal. Historical tests expecting hidden panels/unavailable metadata during an ordinary connection failure are updated to the new stale-but-visible behavior; absent metadata in a successful older-firmware response still appears unavailable.

Real Chrome with enlarged text at a phone width checks the Bluetooth workflow, forced single-poll failure, unchanged navigation identity/document request count, visible panel with disabled actions and preserved viewport anchor. Both firmware profiles compile; standard host tests remain required. These fixtures establish behavior under simulated failure and do not replace the user's phone acceptance.

After separately approved installation, refresh once to load the updated page. Connect/switch saved speakers, disconnect, scan/cancel and observe whether the page retains its position and selection. A brief connection loss should display the stale-values/reconnecting message with disabled controls, then recover in place. If an actual document reload still occurs, treat it as a separate unresolved browser/network case rather than claiming this fixture proved its cause. Existing date/time feature acceptance, four-client/heap testing and pending audio-card replacement remain separate work.
