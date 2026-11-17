# Objectives, learning path, modules, durations

## Measurable objectives (3–5 per course; 1 per lesson in microlearning)

Pattern: **[measurable verb] + [what] + [condition/standard]** — "Submit an expense claim in NetSuite with receipts
attached, without rejection." Never "understand / know / learn / be aware of" (validate_curriculum warns).

| Learner must… | Bloom level | Verbs (EN) | أفعال (AR) | Typical objective `type` |
|---|---|---|---|---|
| know | remember | identify, list, name, recall, recognise, locate | حدّد، عدّد، سمِّ، تذكّر | recall |
| know | understand | explain, describe, summarise, classify, compare | اشرح، صف، لخّص، صنّف، قارن | concept, structure, policy |
| do | apply | complete, submit, configure, use, follow, report | نفّذ، طبّق، استخدم، أبلغ | procedure, policy |
| decide | analyze | spot, detect, check, troubleshoot, differentiate | اكتشف، راجع، ميّز، حلّل | behavior |
| decide | evaluate | decide, judge, choose, assess, justify, verify | قرّر، قيّم، اختر، برّر | behavior, policy |
| make | create | design, plan, draft, build | صمّم، خطّط، أنشئ | (advanced only) |

Objective `type` drives format choice (see `skills/tcs-orchestrator/references/format-selection.md`):
concept · structure · procedure · behavior · policy · recall · adoption.

Sources: when `sources.yaml` exists, seed objectives from its chunk summaries, procedures (`kind: procedure/step`) and
policies; put `source_ids` on the objective. With no sources, mark the course `general_knowledge` and keep objectives generic.

## Learning path (sequencing)

1. **Why before how**: a short concept/stakes lesson first only if the audience lacks motivation or context.
2. **Simple → complex**, **frequent → rare**, **normal path → exceptions**.
3. **Prerequisites first** (catalogue "Dependency" column; procedure inputs before steps).
4. **Practise then assess**: every objective has a knowledge check or scenario (tcs-assessment); the last lesson can
   carry the course post-test.
5. Spaced reinforcement for recall/adoption: a `series` of nudges after the core lessons (tcs-format-series).

## Durations and size

| Rule | Value |
|---|---|
| Lesson length (microlearning) | 3–7 min; procedure/behavior/policy 5, concept/structure 4, recall/adoption 3 |
| Objectives per lesson | 1 (max 2) |
| Lessons per module | ≤ 6 (schema hard max 12) |
| Narration pace | beginner 130 wpm · beginner-intermediate 140 · intermediate 145 · advanced 150–160 · Arabic −10 % |
| Words per lesson | minutes × wpm × 0.85 (leave room for pauses, quiz and on-screen beats) |
| Complexity | low: 1 idea per scene, ≤ 4 bullets · medium: ≤ 6 bullets · high: allow tables/process flows |
| Verbosity | concise (executives, advanced) · standard · detailed (low-literacy or safety) |

If the user gives a total length, divide by lessons; if that drops below 3 min/lesson, cut objectives instead.

## Level from audience

| Signal | Level |
|---|---|
| new hires, beginners, "no experience" | beginner |
| "my team", all staff, mixed roles | beginner-intermediate |
| engineers/developers **and** a technical topic (jargon-dense) | intermediate |
| engineers on a non-technical topic | beginner-intermediate |
| "advanced", experts, specialists | advanced |
| executives | intermediate, concise, decision-focused (risk, cost, ownership) |

## Course-level fields (curriculum.yaml `course`)

`id` (kebab), `title` (+ `title_ar`), `domain`, `domain_pack`, `audience{level, roles, segments}`,
`languages{primary, secondary, subtitles}`, `total_minutes` (= sum of lessons ±15 %), `verbosity`, `wpm`, `complexity`,
`targets`, `aspects`, `renderer`, `compliance` (e.g. "ISO 27001 A.6.3 evidence"). Lessons: `id` `M<n>L<n>`, `title`,
`objective_ids`, `formats` (1–2, ≤ 3 distinct per course), `duration_min`, `targets`, `status: planned`, `rationale`, `source_ids`.
