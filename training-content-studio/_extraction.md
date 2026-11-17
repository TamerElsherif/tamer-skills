# Extraction: what the uSecure remake session actually did

Source run: `OpenMontage/projects/usecure-series` (2026-09-30 → 10-01) and the earlier bilingual
`projects/security-awareness-sw`. This is the worked example; the plugin generalizes it.

## 1. Artifacts produced

| Artifact | What it is | Generic? |
|---|---|---|
| `artifacts/tracker.json` + "Production Tracker" xlsx sheet | Course inventory with tier, rank, audience, formats, durations, status, rationale | Generic → `curriculum.yaml` + tracker export |
| `artifacts/decision_log.json` | Provider/runtime/format/approval decisions with rejected options | Generic → `decisions.md` |
| `refs/<slug>/*.txt` + `*_frames/` | Whisper transcripts + 6 s frame samples of each source video | Generic → `tcs-source-ingest` (video sources) |
| `AUTHORING.md` | Contract for parallel production agents (rules, API, QA loop) | Generic → per-format playbooks + render skill refs |
| `courses/<id>/script.json` | Lines per scene, `who` per line, `^` cue markers, lead/hold/pause, sfx | Generic → `storyboard.json` narration model |
| `courses/<id>/broll.json` | Stock-footage queries per beat | Generic → `broll_shots[]` in storyboard |
| `engine/kit/*` (Info, UI, Person, Sets, Stage, Icons, cast) | Template React/Remotion components: title, bullets, icon grid, steps, do/don't, stat, definition, quiz, checklist, b-roll panel, email/SMS/browser/MFA mock-ups, call-outs, cartoon cast + sets, whiteboard ink mode | Generic → shared render kit; text always from templates |
| `engine/courses/<id>/scenes.tsx` | Hand-authored per-course scenes | **Not generic** — replaced by a data-driven template dispatcher |
| `tools/build.py` | TTS per line (hash-cached) → whisper word times → cue times, amplitude for lip-flap, WPM sanity retry | Generic |
| `tools/broll.py`, `still.py`, `render.py`, `deliver.py` | Pexels fetch + contact sheet, QA stills, locked render + loudnorm, delivery + tracker | Generic |
| `public/music/*` | 4 Lyria beds (explainer, cartoon, whiteboard, executive) | Asset kit slot |

## 2. Implicit prioritization method (made explicit)

What I actually did to pick 20 of 216 courses:
1. **Filter** out non-security / out-of-remit rows (H&S, HR conduct, regional laws for other markets, retired, blog-only).
2. **Dedupe by subject**: keep one per subject cluster (e.g. 6 phishing variants → 1 + specialised ones); prefer the version with the
   richest original (video > blog, longer, cartoon/story when available).
3. **Score** remaining items, implicitly on:
   - *impact* — severity if staff get it wrong (BEC, ransomware, help-desk SE high);
   - *frequency* — how often the threat reaches the audience (phishing, passwords, MFA fatigue);
   - *gap* — not already covered by existing training (Phish Tank and the ISO 27001 course → deprioritised);
   - *urgency* — emerging threats (deepfakes, AI tools, ClickFix);
   - *compliance* — "Core (annual)" flag, ISO 27001 A.6.3 evidence.
4. **Allocate by audience quota** (10 standard / 5 IT / 5 executives) then rank within quota.
5. **Tier** the rest (Tier 2 = next 15, Tier 3 = remaining relevant), record *why* for each, and list skipped duplicates with reasons.
6. **Validate sources** (caught 2 folders whose video didn't match the title and substituted siblings).

Generalized formula (configurable per domain pack):
`priority = Σ w_i · score_i` over {impact, frequency, gap, urgency, compliance}, each 0–5, then audience quotas, subject dedupe,
and tiering. Defaults: impact .30, frequency .25, gap .20, urgency .15, compliance .10.

## 3. Generic vs domain-specific

| Generic (core skills) | Security-specific (→ `domains/security-awareness/`) |
|---|---|
| Intake, objectives, durations, format choice by original/objective | Threat taxonomy, subject clusters, audience quotas 10/5/5 |
| Prioritization formula, dedupe, tiering, tracker | Weights favouring impact/frequency; "Core annual" = compliance |
| Script with cue markers, storyboard, TTS + alignment | Glossary (phishing, MFA fatigue, BEC…), red-flag call-out patterns |
| Template-only on-screen text, kit components | Email/SMS/MFA mock-up presets, villain persona |
| QA: stills, frame grid, duration ≥ 90–100%, no text in generated imagery | ISO 27001 A.6.3 / SOC 2 CC2.2 evidence line + tracker columns |
| Delivery: rename original, tracker sheet, Drive upload | uSecure catalog columns |

## 4. Gaps found (the plugin must fix these)

- **Not data-driven**: every course needed hand-written `scenes.tsx`. → Template dispatcher renders `storyboard.json` directly.
- **No formal grounding**: coverage checklists were prose; no `source_id` per claim. → `sources.yaml` + grounding report.
- **Quizzes only inside video**: no exportable assessment. → `quiz.json`, SCORM 1.2 export.
- **No job aids, decks, HTML lessons, branching, comics, mindmaps, series/nudges.**
- **Arabic skipped** in this run (it worked in `security-awareness-sw` with RTL + mirrored SVG). → `tcs-localize` + RTL kit.
- **No approval gate** (user pre-authorized) and no autopilot decision record per lesson. → orchestrator gate + autopilot `decisions.md`.
- **Lessons learned to encode as QA rules**: one-sided thick accent borders read as AI UI; stock clips must loop/slow; Remotion ids no `_`;
  TTS clips occasionally truncated (WPM check); cue timing from whisper; 8 parallel agents hit session limits (5 OK); fades look like blanks in frame grids;
  catalog folders can contain the wrong video.
- **Model knowledge vs sources** was unlabeled (e.g. GDPR fine correction). → `general_knowledge: true` flag.

## 5. Contradictions / decisions to note (none blocking)

1. "Renders in OpenMontage with no edits" requires a template-driven renderer; the session's kit is generalized into a shared
   `kit/` used by both the OpenMontage adapter (via `video_compose` atelier render) and the standalone Remotion adapter.
2. Remotion needs a company license above 3 employees (memory: Tandrik). Kept as an open decision; HTML/deck/SCORM targets don't need it.
3. Brand slot "logo" is optional — Si-Ware runs must leave it empty (standing user rule).
4. OpenMontage is AGPLv3: the plugin calls it as an external tool/service and copies no OpenMontage source.
