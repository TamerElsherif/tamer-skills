# Approval gate — approved skeleton (golden example)

> **EXAMPLE.** The gate tcs-orchestrator showed before production (Step 2). Simulated user reply: **"Approve"** —
> recorded in `curriculum.yaml` → `approval` and in `decisions.json` (`other/approval`, source user).

**Pay Today? Verify First** — all staff incl. finance (beginner-intermediate) · en-US · 1.5 min · video + lesson + SCORM 1.2 · 16:9
Sources: 1 file (`sources/northwind-payment-verification-policy.md`, FIN-SEC-07, fictional) + general knowledge (labelled) · Domain pack: security-awareness

| Module | Lesson | Objective (Bloom) | Format | Min |
|---|---|---|---|---|
| M1 CEO fraud and fake payment requests | M1L1 The Friday Wire | O1 Spot the warning signs of a fake payment or bank-detail change request (analyze) | cartoon + branching | 1.5 |
| | | O2 Decide the safe response: call back a known number and keep two-person approval (evaluate) | | |
| | | O3 Report a suspicious payment request to IT Security (apply) | | |

Assessment: 4-item knowledge check (pass mark 80 %) + 1 scored branching decision · Pace 135 wpm (script budget) · standard
Assumed (not asked): level beginner-intermediate; 3 objectives in one lesson (user asked for one 90-second piece — curriculum
validator warns, kept on purpose); no 9:16 cut; no subtitles.

## Lesson-1 storyboard preview

Video = linear best path: title → n_intro → `n_good` (callback) → rule → quiz → outro (~90 s). The two bad-outcome scenes
(s06, s07) play only in the HTML/SCORM branching player, so the estimate below (all 11 scenes) overstates the video.

**Language** en-US (ltr) · **Formats** cartoon, branching · **Aspect** 16:9 · **Est.** 1:51 at 135 wpm · **Scenes** 11 · **Claims** 20 (3 general knowledge)
**Cast** rookie, exec, vex, mentor · **Voices** narrator=openai/marin, exec=openai/cedar, mentor=openai/echo, rookie=openai/ballad, vex=openai/verse

| # | scene | template | ~s | narration (▸ = cue) | on screen | visuals | claims |
|---|---|---|---|---|---|---|---|
| 1 | s01_title | title | 5 | One urgent email from the boss. One big decision. | A security micro-drama • The Friday Wire • CEO fraud and fake payment requests | Title card "The Friday Wire", kicker "A security micro-drama", mail i… | 1: S01#c1 |
| 2 | s02_request | cartoon | 12 | Friday, four fifty. ▸ Sam in Finance gets an email from Hana, the C E O. / rookie: ▸ Pay a supplier today, and keep it quiet? | Pay today... and keep it quiet? | set office: rookie(type/neutral); office, Sam (rookie, Finance) at th… | 1: GK |
| 3 | s03_email | email_mock | 11 | Spot the signs. ▸ It's not Hana's usual address. ▸ It says pay today. ▸ The bank details are new. ▸ And it asks for secrecy. | Hana (CEO) • hana.ceo@northwind-mail.example • sam@northwind.example • Confidential: supp… | The fake CEO email with four numbered red-flag call-outs, revealed in… | 5: S01#c1 · GK |
| 4 | s04_vex | cartoon | 5 | vex: ▸ Heh. Nobody questions the boss on a Friday afternoon. | Nobody questions the boss on a Friday. | set den: vex(cross/neutral); den, Vex rubbing his hands, sly; villain… | 1: GK |
| 5 | s05_decide | decision | 10 | What should Sam do? / Pay now, reply to the email, ▸ or call Hana back on her directory number? | What should Sam do? • Pay now. It's the CEO. • Reply to the email to check • Call Hana on… | Three choices; the video highlights the callback. | 1: S01#c1 |
| 6 | s06_paid | statement | 11 | mentor: ▸ That money went to the attacker. If money has already been sent, report it to I T Security and Finance immediately. | That money went to the attacker. • Already paid? Report to IT Security and Finance immedi… | Alert statement; mentor voice. | 1: S01#c1 |
| 7 | s07_reply | statement | 9 | mentor: ▸ Your reply went straight to the attacker. Never use a contact detail given in the request itself. | Your reply went to the attacker. • Never use contact details from the request itself. | Alert statement; mentor voice. | 1: S01#c1 |
| 8 | s08_callback | cartoon | 13 | Sam calls Hana back on her number in the company directory. / exec: ▸ I never sent that. Don't pay it! / rookie: ▸ Reporting it to I T Secu… | I never sent that. Don't pay it! • Reporting it to IT Security now. | set office: rookie(phone/neutral), exec(phone/neutral); office two-sh… | 2: S01#c1 |
| 9 | s09_rule | steps | 14 | mentor: The rule: ▸ call back a number you already have. ▸ Bank changes, and payments of ten thousand dollars or more, need two approvers. … | Every payment request • Call back a known number • Never one from the request • Two peopl… | Three steps: call back, two-person approval, report. | 4: S01#c1 |
| 10 | s10_quiz | quiz | 13 | Quick check. The email lists a new number to confirm. Call it? / ▸ No. Only call a number that's already on file. |  | Quiz Q3 (new number in the email). | 1: S01#c1 |
| 11 | s11_outro | outro | 8 | ▸ Pressure is the red flag. Verify first, and report. No one is blamed for reporting. | Pressure is the red flag. Verify first. • The Friday Wire • Call back a known number • Tw… | Outro line + three tips. | 2: S01#c1 |

Approve, or reply with edits (scene id + change).
