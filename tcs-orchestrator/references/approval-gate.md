# Approval gate (Step 2) — always shown, even for fully specified requests

Show the skeleton + a lesson-1 storyboard preview, then wait. Nothing is scripted or rendered before approval.
Autopilot shows the same view only with `--review skeleton`.

## 1. Skeleton (from curriculum.yaml)

```
**{course.title}** — {audience.roles/level} · {languages.primary}{ + subtitles} · {total_minutes} min · {targets} · {aspects}
Sources: {n files | general knowledge (labelled)} · Domain pack: {pack}

| Module | Lesson | Objective (Bloom) | Format | Min |
|---|---|---|---|---|
| M1 {title} | M1L1 {title} | O1 Spot the warning signs of … (analyze) | cartoon + branching | 5 |
| | M1L2 {title} | O2 Decide the safest response … (evaluate) | cartoon + branching | 5 |
| M2 … | … | … | … | … |

Assessment: {knowledge checks per lesson + post-test 80 % | flashcards} · Pace {wpm} wpm · {verbosity}
Assumed (not asked): {e.g. level beginner-intermediate, 9:16 nudge cut}
```

## 2. Lesson-1 storyboard preview (lightweight — not the full storyboard.json)

```
**M1L1 {title}** — {format(s)}, ~{min} min, {n} scenes
| # | Visual (template / set) | Narration gist | On-screen text | s |
|---|---|---|---|---|
| 1 | title — {course title} | Hook: "{one-line question}" | {title text} | 6 |
| 2 | cartoon / office — {persona} gets an urgent email | Rookie almost clicks | — (speech bubble: "Urgent!") | 18 |
| 3 | email_mock with red-flag call-outs | Mentor points out 3 signs | sender · link · urgency | 20 |
| 4 | decision — "What should Sam do?" | Choice → consequence | 3 options | 25 |
| 5 | quiz — 2 questions | Check | stem + options | 30 |
| 6 | outro — key takeaway + report button | Recap | 3 bullets | 8 |
```
Rules for the preview: 5–9 scenes, every on-screen string is a template prop (no text in generated images), scene
templates ∈ `schemas/enums.json` templates, total ≈ lesson minutes.

## 3. Prompt

> Approve to start production, or tell me what to change (e.g. "M1L2 as explainer", "add a lesson on reporting",
> "Arabic only", "shorter"). Edits are applied and the gate is shown again.

Tappable options when available: "Approve" · "Approve, but change formats" · "Edit objectives" · "Start over".

## 4. Recording approval (curriculum.yaml)

```yaml
approval:
  status: approved          # draft until the user approves
  by: user                  # or the user's name if they gave it
  at: 2026-11-17T14:05:00Z
  edits: ["M1L2 format cartoon -> explainer", "added O4 report incidents"]
```
Then `run_state.py set runs/<id> plan done --note "approved"` and append a decision `{key: other, name: approval,
source: user}` to decisions.json. Any later structural change (add/remove lesson, change objective) re-opens the gate.
