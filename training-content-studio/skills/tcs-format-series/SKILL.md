---
name: tcs-format-series
description: Plans and builds an episodic training series with gamification and spaced reinforcement — series plan (episodes, recurring cast, points, streaks, badges), 30–60 s vertical nudge storyboards, flashcard decks and a nudge calendar. Use when the chosen or requested format is "series", "episodes", "campaign", "drip", "microlearning", "nudges", "spaced repetition", "gamification", "streaks" or "flashcards". Not for a single standalone lesson (pick that lesson's format skill) or for the course outline itself (tcs-curriculum).
---

# tcs-format-series

## Purpose
Turn a course (several approved lessons) into a season: weekly episodes in any base format, plus short nudges that
re-surface key behaviours (spacing + retrieval), with light gamification to keep completion high.

## Inputs
- Approved `curriculum.yaml` (all lessons with `formats` containing `series`, or the whole course on request).
- Each episode's main storyboard (built by its format skill) and `quiz.json` items (tcs-assessment).
- Personas (recurring cast), domain `scenarios.md`, `assets/voices.yaml`.

## Outputs
- `series_plan.yaml` (fill-in `templates/series_plan.yaml`; validate with `templates/series_plan.schema.json`):
  season meta, episodes → lesson ids, recurring cast, gamification (points, streaks, badges, leaderboard policy),
  nudge types, flashcard decks (refs to `quiz.json` `flashcard` items).
- `nudge_calendar.yaml` (`templates/nudge_calendar.yaml`, same schema file `$defs.calendar`): dated sends per channel.
- Episode storyboards: `formats: ["series", <base>]` (base = explainer/cartoon/doodle/comic/…).
- Nudge storyboards `<lesson_id>N<n>.storyboard.json`: `aspect: "9:16"`, `formats: ["series"]`, 30–60 s, templates
  `chat_mock`/`email_mock`/`mfa_prompt`/`cartoon` (hook) → `flashcard` → `quiz` → `outro` (streak/points line).
- Fragment `templates/example.storyboard.json` (a nudge).

## Steps
1. Season shape: 4–8 episodes, one per week (or fortnight); order by curriculum priority; episode 1 = highest-impact topic.
2. Recurring cast: 2–3 personas fixed for the season (+ antagonist if the domain has one); a running situation (same office).
3. For each episode: base format storyboard (delegate to its format skill) ≤ 3–4 min, ending with a teaser for the next.
4. Nudges per episode: 2 (day +2 and day +7 after the episode) — 30–60 s, one behaviour, one retrieval question.
5. Flashcards: 5–10 per episode from objectives (front = cue/situation, back = action); reuse quiz `flashcard` items.
6. Gamification: points per completion/correct answer, streak = consecutive weeks with ≥ 1 activity, 3–5 badges tied
   to behaviours (e.g. "Reported a simulated phish"), opt-in team leaderboard only (no individual shaming).
7. Calendar: dates, channel (email/Teams/Slack/LMS/SMS), asset path, fallback text; respect working days and locale
   (e.g. Egypt weekend Fri–Sat), avoid public holidays (client-provided list).
8. Validate plan + calendar against the schema; validate every storyboard.

## Rules / QA
- Nudge = 30–60 s, one idea, 9:16, captions burned in (silent autoplay), ≥ 1 retrieval question or flashcard.
- Points/badges reward learning behaviours, never punish; leaderboard opt-in and team-level by default.
- Spacing: first nudge 1–3 days after the episode, second 5–10 days; final season recap quiz.
- Calendar text is on-screen/outbound copy → localize; no personal data in nudge payloads.
- Every nudge links back to its episode and job-aid.

## Blends
- **series + any base format** (episode look). **series + job-aid**: one card per episode.
- **series + branching**: "What would you do?" weekly decision nudge.
- **series + mindmap**: season map revealing one branch per episode.

## References
- `references/playbook.md`, `templates/series_plan.yaml`, `templates/nudge_calendar.yaml`,
  `templates/series_plan.schema.json`, `templates/example.storyboard.json`.
