# Decision rules (autopilot Stage 2)

Machine version: `decision-rules.yaml` (tune keywords, weights, thresholds there). Engine: `scripts/decide.py`.
Precedence: **explicit flags > request wording > sources > rules > defaults**. Every decision is written to
`decisions.json` with `value`, `signal` (what triggered it), `confidence` 0–1, `source`
(flag|request|sources|rule|default|user) and `alternative_rejected`.

## Defaults applied when not specified

| Decision | Rule | Confidence (typical) |
|---|---|---|
| **language** | Arabic script ≥ 30 % of letters → Arabic primary + English subtitles; Egyptian cues (مصر, Cairo, dialect words) → `ar-EG`, else `ar-MSA`. English request with a MENA place/cue (Riyadh, Dubai, Egypt, GCC…) → Arabic primary + English subtitles. UK cues → `en-GB`, else `en-US`. `--lang both` → request language primary + the other as secondary + subtitles | 0.9 script · 0.65 MENA cue · 0.85 English |
| **audience** | first cue wins: executives → managers → new hires → technical → customer-facing → "my team" → all staff; none → general staff | cue 0.55–0.8 · none 0.4 (critical) |
| **level** | new hires → beginner; mixed/my team/all staff → beginner-intermediate; technical audience + jargon-dense topic (≥ 8 % technical terms) → intermediate, else beginner-intermediate; "advanced/experts" → advanced | 0.7–0.95 |
| **objective type** | keyword votes (+ sources fact kinds): policy > procedure > behavior > adoption > recall > structure > concept on ties; none → concept | 0.4–0.95 |
| **objectives** | 3–5, Bloom-matched (know → remember/understand, do → apply, decide → analyze/evaluate); count = "N lessons" wording, else source sections clamped 3–5, else 3; seeded from source chunk summaries when available | 0.55 default · 0.75 sources (critical) |
| **length** | microlearning: 1 objective/lesson, 3–7 min (procedure/behavior/policy 5, concept/structure 4, recall/adoption 3), ≤ 6 lessons/module; "N minutes" wording → divide, trim objectives if < 3 min each | 0.75 |
| **wpm** | beginner 130 · beginner-intermediate 140 · intermediate 145 · advanced 155; Arabic × 0.9 | 0.8 |
| **verbosity** | executives/managers concise; advanced concise; else standard | 0.7 |
| **formats** | concept → explainer (+ B-roll if visual subject) · structure → mindmap · procedure + software → screencast-sim + job-aid (non-software → explainer + job-aid) · behavior/judgment → cartoon micro-drama + branching (+ knowledge check) · policy/compliance → cartoon micro-drama + post-test + evidence · recall → series (flashcards + nudges) · adoption → series · executive/manager audience → narrated-deck primary (+ job-aid for policy/procedure, + branching for judgment). Request wording pins formats ("deck", "cartoon", "checklist"…) | 0.75 rule · 0.95 wording |
| **blend** | max 2 formats/lesson, 3/course | 0.8 |
| **targets** | video formats → MP4 16:9 + 9:16 nudge cut; narrated-deck → PPTX + narrated MP4; branching/comic → HTML lesson; job-aid → PDF job aid; ≥ 2 lessons or compliance evidence → + SCORM | 0.8 |
| **aspect** | 16:9 master (+ 9:16 when a nudge cut is produced); `--aspect` sets the master | 0.8 |
| **domain / domain_pack** | best keyword match over `decision-rules.yaml domain_packs` + `domains/*/pack.yaml` (`match.keywords`); none → domain inferred from type, pack `_template` | 0.7–0.95 match · 0.45–0.6 inferred (critical) |
| **renderer** | `--renderer`; else `openmontage` if `OPENMONTAGE_ROOT` is set; else `remotion` (kit); no video/deck target → `none` | 0.6 |
| **assessment** | concept/structure/behavior/adoption → knowledge-check; procedure → scenario (try-it); policy → post-test (80 %) + evidence; recall → flashcards | 0.8 |

## Guardrails

| Situation | Action |
|---|---|
| Critical decision (domain, audience, objectives) confidence < 0.5 and `--review none` | proceed; add to `flagged_top` (top of REPORT.md "Needs attention") and mark the decision `flagged: true` |
| No sources | `grounding: general_knowledge` decision + warning; every claim labelled `general_knowledge: true`; listed in REPORT.md |
| No sources + high-stakes topic (medical, legal, financial, safety-critical) | `scope: plan-only`, pause after Plan, ask for sources in REPORT.md; produce nothing else |
| Conflicting sources (`sources.yaml conflicts[]`) | choose the most recent fact (date), then the most authoritative source (authority 1–5); log `conflict-resolution` with the rejected fact ids |
| Budget (`--budget 5$` or `200k` tokens) | estimate after Plan; if over: drop secondary formats → drop 9:16 cut → drop secondary language → drop last lessons (and SCORM if 1 lesson left); log `budget-tradeoff`; still over at 1 lesson → flag |
| Explicit flags / wording | always override rules; logged with `source: flag` or `request`, confidence 0.9–1.0 |

## Confidence scale

0.9–1.0 explicit (flag/wording) · 0.7–0.89 strong signal · 0.5–0.69 inferred · < 0.5 guess (flag if critical).

## Tuning

- Add organisation vocabulary to `audience.cues`, `software_cues`, `domain_packs` in the YAML; keep regexes simple.
- Arabic patterns are substrings (they match with ب/ال prefixes); English patterns get word boundaries automatically.
- After any change run `.venv/bin/python skills/tcs-autopilot/scripts/test_decisions.py` — the golden runs must pass.
- Keep `skills/tcs-orchestrator/references/format-selection.md` in sync with `formats_by_type`.
