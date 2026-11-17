# Security-awareness scenarios

Red-flag scenarios and micro-drama premises. Red flags and safe actions below are widely published security-awareness
guidance (**general knowledge** — cite client policy/sources for anything procedural such as report channels, extensions,
approval thresholds). Fictional company: Northwind Co. (`northwind.example`); look-alikes use `.example` domains.
Mock-up presets referenced by id live in `mockups.yaml`. Cast ids: core personas + `vex`.

| # | Threat | Micro-drama premise (cast) | Red flags | Safe action | Templates / preset |
|---|---|---|---|---|---|
| 1 | Phishing (credential) | Friday 4:55 p.m.: rookie gets "mailbox closing in 2 hours" from IT Service Desk; nearly clicks; learner hovers the button (rookie, learner, vex) | look-alike sender domain, generic greeting, deadline, link text ≠ URL, request to log in | don't click; Report Phishing; open the service via a bookmark | `email_mock` → `phish-mailbox` |
| 2 | BEC / invoice fraud | Supplier "Dana" emails finance: "new bank details, pay today" from a near-identical domain (customer, manager, rookie, vex) | changed bank details, urgency, reply-to differs, slight domain change, secrecy | call the supplier on the number already on file; dual approval; report | `email_mock` → `bec-bank-change`, `do_dont` |
| 3 | CEO fraud | "Hana" (exec) emails from a personal address: "confidential acquisition, buy gift cards / wire now" (exec, rookie, vex) | authority + secrecy, unusual payment method, personal address, bypassing process | verify via known channel; follow payment process; report | `email_mock`, `chat_mock` → `ceo-giftcards` |
| 4 | MFA fatigue | Midnight push storm; rookie denies, then is tempted to approve "to make it stop"; vex gloats (rookie, vex, mentor) | prompts you didn't start, repeated prompts, odd location/time | never approve; deny; report; change password | `mfa_prompt` → `mfa-storm`, `cartoon` |
| 5 | Deepfake voice | Manager gets a call in the exec's voice asking for an urgent transfer; audio slightly flat (manager, voice_clone, mentor) | urgency, unusual request, call from new number, voice quirks, refusal to call back | hang up; call back on a known number; use a pre-agreed verification phrase/process | `cartoon` (glitch overlay), `steps` |
| 6 | Tailgating | Courier with boxes asks learner to hold the secure door (learner, vex, manager) | no visible badge, hands full, time pressure, friendliness | send to reception; don't hold secure doors; report unbadged people | `comic` / `cartoon` set `reception` |
| 7 | USB drop | Rookie finds a USB stick labelled (in the story, not on screen) "Salaries" in the car park (rookie, mentor) | unknown device, curiosity bait | don't plug it in; hand it to IT | `cartoon` set `street`, `popup` |
| 8 | Smishing | Parcel "on hold, pay a small fee" SMS with a short link (learner, vex) | unexpected delivery, small fee, short/odd link, urgency | don't tap; check in the courier's official app/site; report/delete | `chat_mock` → `smish-parcel` |
| 9 | Quishing | QR sticker on the office car-park sign "pay parking here" leads to a payment page (rookie, learner) | sticker over original QR, URL preview mismatch, card request | inspect the URL preview; use the official app; report the sticker | `browser_mock` → `quish-parking` |
| 10 | Help-desk SE | Caller claims to be the CFO, locked out before a board meeting; demands password + MFA reset (support, vex, mentor) | urgency, authority, refusal of callback, new device enrolment | verify via callback to directory number / manager approval; escalate | `branching` + `cartoon` (see tcs-format-branching example) |
| 11 | AI data leakage | Learner pastes a customer contract into a free AI chatbot to "summarise quickly" (learner, mentor) | confidential data, unapproved tool, personal account | use approved AI tools only; remove personal/confidential data; check policy | `browser_mock` → `ai-paste`, `do_dont` |
| 12 | Infostealer download | "Free AI productivity tool" pop-up offers a download (rookie, vex, mentor) | unofficial site, too-good offer, executable download | official app stores/IT portal only; report | `popup` → `fake-download`, `browser_mock` |

## Premise rules
- The mistake is relatable and recoverable; end with the right action modelled.
- Never use real brands, real people, real phone numbers or live URLs; use `.example` domains and fictional names.
- Show red flags with `callouts` on mock-ups (`cue` per flag) and say them in narration in the same order.
- One premise per lesson objective; reuse the same cast across a series.

## Reusable red-flag call-out vocabulary (on-screen ≤ 6 words)
"Look-alike domain" · "Generic greeting" · "Pressure and a deadline" · "Hover before you click" · "Unexpected attachment" ·
"Asks for your password" · "New bank details" · "Keep it secret" · "Prompt you didn't start" · "Short, odd link" ·
"Sticker over the original" · "Confidential data, public tool".
