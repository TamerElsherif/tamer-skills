---
name: tcs-curriculum
description: Plans a course outline only — measurable Bloom-level objectives, learning path, modules, lessons, durations and pace — into curriculum.yaml, and prioritizes a long topic list or course catalogue (spreadsheet) with the impact × frequency × gap × urgency × compliance method, audience quotas, subject dedupe and tiers. Use when someone asks to "plan / outline / structure a curriculum", "write learning objectives", "which courses should we build first", "prioritize this catalogue" or "rank these topics". Not for producing lessons, scripts or videos (tcs-orchestrator or tcs-autopilot) and not for ingesting source documents (tcs-source-ingest).
---

# tcs-curriculum — outline, objectives and prioritization

## Purpose
Turn a topic (and optional sources) or a catalogue of candidates into a validated `curriculum.yaml`: what learners will be
able to do, in which order, in which lessons, how long, in which format — with a recorded reason for every choice.
It is the planning step that tcs-orchestrator (interactive) and tcs-autopilot (Stage 3) call; it can also be used alone.

## Inputs
- Topic / request text; audience (roles, level), languages; total length if given.
- Optional `sources.yaml` (from tcs-source-ingest) — headings, procedures, policies seed the objectives.
- Optional candidate list: `.xlsx` / `.csv` catalogue (read-only) or `candidates.yaml`.
- Optional domain pack name (`domains/<pack>/`) for prioritization weights, quotas, clusters, glossary.

## Outputs
- `curriculum.yaml` — validates against `schemas/curriculum.schema.json` (course, objectives, modules → lessons,
  optional `prioritization`, `approval`).
- Optional `prioritization.md` — ranked table for the approval gate.

## Steps

### A. Course outline (single course)
1. **Frame**: one sentence — *who* must be able to *do what* *by when / to what standard*. Pick the domain pack
   (`domains/<pack>`; none → `_template`).
2. **Objectives (3–5)**: measurable verb + object + condition, Bloom level matched to the need
   (know → remember/understand · do → apply · decide → analyze/evaluate). Tag each with `type`
   (concept, structure, procedure, behavior, policy, recall, adoption) and `source_ids` when sourced.
   Verb table + Arabic verbs: `references/objectives-and-paths.md`.
3. **Path**: order objectives (why → how, simple → complex, normal → exceptions, prerequisites first).
4. **Lessons**: 1 objective per lesson; 3–7 min each; ≤ 6 lessons per module; ids `M<n>L<n>`.
5. **Format per lesson**: from objective type × audience × effort — matrix in
   `skills/tcs-orchestrator/references/format-selection.md` (max 2 formats/lesson, 3/course). Put the reason in `rationale`.
6. **Course fields**: level, languages (Arabic → also `title_ar`), `wpm` (beginner 130 … advanced 155, Arabic −10 %),
   verbosity, complexity, targets, aspects, renderer, compliance.
7. **Approval**: leave `approval.status: draft`. The orchestrator gate sets `approved` (+ by/at/edits); autopilot sets
   `auto-approved`.
8. **Validate**: `.venv/bin/python skills/tcs-curriculum/scripts/validate_curriculum.py curriculum.yaml [--sources sources.yaml]`.
   Fix every ERROR; read every WARN.

Fill-in starting point: `templates/curriculum.template.yaml`.

### B. Prioritize a catalogue / long topic list
1. Choose a profile: the domain pack's (`--pack security-awareness`) or `templates/prioritization.default.yaml`; copy and
   edit for a new organisation (weights, quotas per audience, filters, keywords, already-built list).
2. Run:
   ```
   .venv/bin/python skills/tcs-curriculum/scripts/prioritize.py catalogue.xlsx --pack <pack> \
       [--weights impact=.3,frequency=.25,gap=.2,urgency=.15,compliance=.1] [--quotas standard=10,it=5,executives=5] \
       [--existing "Course A;Course B"] --out curriculum.yaml --md prioritization.md
   ```
   Without the script: build the same table by hand — filter → score 0–5 → P = Σ w·s → dedupe by subject → fill quotas
   → tier 2 (next 15) / tier 3 — steps and signals in `references/prioritization.md`.
3. Review the top table: cross-segment duplicates, "story" originals worth keeping, source files that don't match their
   title (swap with a cluster sibling). Edit `prioritization.items[].decision/reason` rather than deleting rows.
4. Rewrite the DRAFT objective of each included lesson (step A2), split modules > 6 lessons, then validate (A8).

## Rules / QA
- Every objective is measurable and taught by ≥ 1 lesson; every lesson has ≥ 1 objective (validator errors otherwise).
- ≤ 2 formats per lesson, ≤ 3 distinct formats per course; lesson lengths 3–7 min (warn outside).
- `total_minutes` within ±15 % of the lesson sum.
- Every prioritized row keeps a reason, including skipped duplicates and out-of-scope rows.
- Weights sum to 1 (the script normalises and says so).
- No sources → state "general knowledge" in the course notes; never invent `source_ids`.
- Arabic primary: `title_ar` on course/modules/lessons (or hand to tcs-localize); RTL is handled downstream.
- Catalogue files are opened read-only; never write back to the user's spreadsheet.

## References (load on demand)
- `references/objectives-and-paths.md` — Bloom verbs (EN/AR), sequencing, durations, wpm, level-from-audience.
- `references/prioritization.md` — the 8-step method, scoring signals, config keys, validation against the worked example.
- `templates/prioritization.default.yaml`, `templates/prioritization.security-awareness.yaml` — profiles.
- `templates/curriculum.template.yaml` — fill-in example.
- Scripts: `scripts/prioritize.py`, `scripts/validate_curriculum.py` (both `--help`).
