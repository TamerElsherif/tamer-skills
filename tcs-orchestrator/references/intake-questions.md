# Intake question bank (Step 1)

Ask **only what is missing**, in **one round**. Every question has a recommended default (marked ★) so
"go with defaults" / "you decide" answers everything. Use tappable options (AskUserQuestion: ≤ 4 questions per call,
2–4 options each, header ≤ 12 chars) when available; otherwise a numbered list the user can answer like "1b 2a 3 default".

## 0. Parse first (fill what is already given)

| Parameter | Parse from | Default if absent (★) |
|---|---|---|
| topic | request | — (required; ask only if empty) |
| sources | paths, URLs, "attached", "our SOP" | ★ general knowledge, labelled; high-stakes topics (medical, legal, financial, safety-critical) → sources required |
| objectives | "so they can…", verbs | ★ 3–5 proposed by you (Bloom-matched) |
| audience / role | "new hires", "managers", "my team", "engineers" | ★ all staff, mixed level |
| level | audience + jargon | ★ beginner-intermediate |
| language | request script, "in Arabic", MENA place names | ★ request language; Arabic/MENA → Arabic primary + English subtitles |
| total length / per lesson | "10 minutes", "3 lessons" | ★ microlearning: 3–7 min/lesson, 1 objective/lesson |
| complexity / verbosity / wpm | "simple", "detailed", "fast" | ★ standard; 130–145 wpm by level (Arabic −10 %) |
| format(s) | "deck", "cartoon", "checklist"… | ★ from `format-selection.md` |
| targets + aspect | "video", "SCORM", "PDF", "reels", "9:16" | ★ from format (§5 of format-selection); 16:9 master + 9:16 nudge cut |
| domain pack | topic keywords | ★ matching `domains/<pack>` else `_template` |

If nothing is missing → skip to the gate (Step 2). Say in one line what you assumed.

## 1. The round (max 4 tappable questions + objectives in text)

Put proposed objectives in the message body (they are confirmed again at the gate):

> **Proposed objectives** — after this course, learners can: 1) Spot … (analyze) 2) Decide … (evaluate) 3) Report … (apply).
> Reply with edits, or leave as is.

Then ask the missing ones, in this priority order, merging when > 4 are missing:

**Q1 Sources** (header "Sources") — "What should the content be based on?"
- ★ "Use my files/links" (they paste paths/URLs next) · "General knowledge (labelled)" · "Both: my files + fill gaps"
- High-stakes topic: drop "General knowledge" and say why.

**Q2 Audience** (header "Audience") — "Who is it for, and in which language?"
- ★ "{inferred audience}, {inferred language}" · "New hires, English" · "All staff, Arabic + English subtitles" · "Managers/executives"
- Level follows audience (table above); ask level separately only if the user hints at expertise.

**Q3 Length** (header "Length") — "How long and how detailed?"
- ★ "Microlearning: {n} × 5 min, standard pace" · "One short video (≤ 5 min)" · "Detailed: {n} × 7 min, slower pace" · "Ultra-short nudges (≤ 90 s)"

**Q4 Format** (header "Format") — "Which format? I recommend {format} — {one-line rationale}."
- ★ "{recommended blend}" · 2–3 alternatives from the matrix with effort label (low/medium/high)

**Q5 Outputs** (merge into Q4's options or ask if a 5th is needed) — "Where will it be used?"
- ★ "{derived targets}" · "LMS (SCORM) + MP4" · "Slides (PPTX) + PDF job aid" · "Social/phone (9:16 only)"

Merging rules when > 4 are missing: fold Q5 into Q4 options ("Cartoon + branching → MP4, 9:16, SCORM"); fold language
into Q2; never ask about verbosity/wpm/complexity unless the user mentioned them — use defaults and show them at the gate.

## 2. Plain-text fallback (no tappable UI)

```
I'll build "{title}". Defaults are marked ★ — reply "defaults" to accept all, or e.g. "1b, 3a".
Proposed objectives: 1) … 2) … 3) …   (edit freely)
1. Sources: a) ★ my files (paste paths)  b) general knowledge (labelled)  c) both
2. Audience & language: a) ★ {inferred}  b) new hires, English  c) all staff, Arabic + EN subtitles  d) managers
3. Length: a) ★ {n} × 5 min  b) one ≤ 5 min video  c) {n} × 7 min detailed  d) ≤ 90 s nudges
4. Format & outputs: a) ★ {recommended} → {targets}  b) {alt 1}  c) {alt 2}
```

## 3. Interpreting answers

- "defaults" / "you decide" / "go" → take every ★.
- Free text overrides options; ambiguous answer → take ★ and note it at the gate (no second question round).
- User adds sources later → run tcs-source-ingest before the gate and re-propose objectives from them.
- Record every answer as a decision (`source: user`) in `runs/<id>/decisions.json` so the report shows what was chosen.
