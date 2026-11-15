# Browser access management

Status: implemented candidate, software-verified; installation and physical acceptance pending. This stage follows user-accepted HOME/Direct mode switching in 1.0.0+37.ga1f576b.

## What the list means

Browser access lists the existing four saved permission slots, their Home/Direct scope, and this browser when its remembered key is valid for the current mode. Entries are permissions, not connected phones. Device names, browser names and online/last-seen state have never been stored and are not inferred. One physical phone or browser can occupy separate Home and Direct entries; an origin/IP change can also require another permission. Slot numbers may be reused after deletion.

Select an entry and press Forget selected browser. Confirmation names the slot and scope and identifies the current browser when known. Removal affects that permission only, retains other permissions, and uses the normal deferred Flash autosave. Keep power connected until Settings saved appears. A full registry can be freed this way before physically pairing a new browser.

Forgetting a browser does not disconnect its Wi-Fi, stop audio, change mode, alter the Direct password or erase its other-scoped permission. Commands using the removed key are immediately denied. A page with a removed current-mode key detects the registry revision change on its next successful poll, rechecks authorization and removes its local key without reloading the document. If both POST responses are lost, the page reports uncertainty and refreshes the list rather than sending another new command automatically.

## Trusted home access

When home trust is ON, any peer admitted by the existing same-subnet/home-interface policy can control the clock without a remembered key. Forgetting a saved Home permission therefore does not block that trusted network access. The page and confirmation explicitly explain this. Direct still requires a remembered Direct permission, and home trust is not accepted from the Direct interface.

When trust is OFF, the removed scoped permission needs physical pairing again. A client that has lost its last applicable permission cannot administer the list. All authorized control clients have the existing equal privileges; no separate administrator role is introduced. Home trust changes, Forget all browsers, pairing codes and Direct password rotation remain in the physical Phone Control menu. Saved permission removal is not a network-device block list or a general Wi-Fi client disconnection feature.

## Protocol, consistency and storage

`browser_control:true` advertises the optional public `/browsers.json` metadata response. It contains epoch, RAM-only registry revision, capacity, home-trust state and occupied slot/scope entries, without keys, password, fingerprints or device names. It has a separate 1 KiB allocation. Optional metadata failure disables list actions without disabling unrelated controls; connection loss retains the authorized page layout with controls disabled.

The existing authenticated `/access` response identifies the current slot through an internal `/browser-self-N.json` response route. That route contains only public slot/epoch/revision metadata; it is not an authentication credential. The browser still requires successful key verification and matching revision/epoch for its current-browser label. No key is put in a URL, log, metadata list or public fingerprint.

`/browsers` accepts `forget <slot 1..4> <expected registry revision>` in the existing credential/epoch/command-ID/nonce envelope, same-origin header policy, shared command queue and retry rules. The main loop rechecks the revision before removal. Pairing, logout, selective/all revocation and Direct-key rotation invalidate the RAM revision. A stale request cannot remove a different permission after slot reuse. Retries with the same command ID/nonce return the existing result without another deletion while their authorization remains valid; self-revocation can make a retry denied because its own key is gone. A successful browser removal also cancels a pending network-mode plan rather than allowing a previously authorized switch to proceed after access changes.

The four-entry Flash layout, settings version and saved key values are unchanged. The normal A/B autosave persists the smaller registry. Runtime revocation does not guarantee persistence through an immediate power loss before that save. No labels or timestamps are added. Four stored entries and four HTTP POST contexts still do not establish four-client runtime/audio/resource acceptance.

## Verification and acceptance

Native checks cover scoped authorization, trusted-home admission, current-slot lookup, valid/invalid slot and revision bounds, self/other removal, retained permissions, stale slot reuse, cached retry, logout invalidation, revision wrap and bounded serialization without secrets. Production JavaScript checks cover cancellation, stale-list refusal, lost responses without duplicate deletion, list refresh, current-browser marking, self-revocation without document reload, empty/old-firmware lists and optional metadata failure isolation. Real Chrome fixtures at 360/412/960 pixels with enlarged text cover native confirmation, current-browser identification, selective/self removal, no page navigation and failure isolation. Full HTTP response bounds and both firmware profiles are checked separately.

After separately approved installation, refresh once and compare the list against known Home/Direct pairings. Cancel a Forget confirmation first. Use a disposable second browser permission to verify removal, retained access from another browser, re-pairing and reboot persistence after Settings saved. Test self-removal last with home trust OFF only when physical Phone Control recovery is available; with trust ON, verify the explicit warning and continued trusted Home access. Do not remove the user's actual permissions as part of installation verification. Four real browsers, radio coexistence and save/power-cycle cases remain hardware checks.
