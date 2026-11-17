# FORMATS — the 10 format skills (SKILL + playbook + templates)


# FORMAT: explainer


# tcs-format-explainer

## Purpose
Turn one approved lesson into the explainer part of `<lesson_id>.storyboard.json`: an arc of title → hook → concept →
mechanism → example → warning signs → consequences → actions → quick check → recap → outro, alternating stock B-roll
(with topic chips) and template-driven motion graphics roughly every 8–20 s.

## Inputs
| File | Use |
|---|---|
| `curriculum.yaml` → lesson (`approval.status` ∈ approved/auto-approved) | objectives, `duration_min`, `formats`, `targets` |
| `sources.yaml` | facts (`F###`) + chunk ids for `claims[].source_ids` (`S01#c3`) |
| `domains/<pack>/format_defaults.yaml`, `mockups.yaml` | per-domain music bed, mock-up presets (email/sms/mfa) |
| `assets/theme_presets.yaml`, `assets/voices.yaml` | theme preset + narrator voice for the lesson language |
| scriptwriter draft (if any) | narration lines to keep; re-cut into scenes |

## Outputs
- `scenes[]` using only `enums.templates`: `title`, `section`, `bullets`, `icon_grid`, `steps`, `process_flow`, `timeline`,
  `do_dont`, `comparison`, `stat`, `definition`, `statement`, `table`, `checklist`, `quiz`, `outro`, `broll`, `broll_panel`,
  `email_mock`, `chat_mock`, `browser_mock`, `mfa_prompt`, `popup`, `code_mock`, `image`.
- `broll_shots[]` — the B-roll shot list (`id`, `query`, `provider`, `min_s`, later `path` + `license`).
- Optional `generated_images[]` (no text in prompt; see Rules).
- Top level: `formats: ["explainer"]` (or blend, max 2), `music.bed: "explainer"` (`executive` for leadership audiences).
- Fill-in helpers: `templates/script_template.md`, `templates/broll_shotlist.yaml`; reference fragment
  `templates/example.storyboard.json` + Arabic RTL `templates/example.ar-EG.storyboard.json` (both validate against
  `schemas/storyboard.schema.json`).

## Steps
1. Read the lesson's objectives; list the beats from `references/playbook.md` and drop any that serve no objective.
2. Budget time: `duration_min × 60 × wpm/60` words (default 150 wpm EN, 130 wpm AR). Scenes 5–35 s, one idea each.
3. For each beat pick the template (table in playbook). Every 2–3 graphics scenes insert a `broll` or `broll_panel` scene.
4. Write narration lines `{who:"narrator", text}`; put `^` right before the words that reveal each item. N items ⇒ N `^`.
5. Fill props — all on-screen text lives here. Bullets/steps/icon_grid ≤ 6 items, checklist ≤ 7, ≤ ~8 words per item.
6. Attach `claims[]` per scene: `source_ids` from `sources.yaml` or `general_knowledge: true` (be honest).
7. Build `broll_shots[]`: concrete, people-at-work queries (no logos, no hoodie-hacker clichés), `min_s` ≥ scene length.
8. Add the quick-check `quiz` scene (`quiz_item` → id in `quiz.json`; question line `pause: 2.2`, answer line starts `^`).
9. Validate (see Rules) and hand back to `tcs-storyboard` / orchestrator.

## Rules / QA
- Templates and props only; never invent a template or put text into imagery. Image prompts end with
  "no text, no letters, no numbers, no signage, no logos".
- Mock-ups use fictional brands/domains (`northwind.example`, look-alike `northwlnd.example`); no real logos.
- `^` count per scene ≥ highest `cue` used in props + 1; reveal nothing long before it is said.
- Stats need a source (`stat.source` + claim `source_ids`); never invent numbers.
- B-roll: review the contact sheet; reject clips with visible brands, text, screens with readable data, clichés.
  Clips loop/slow (≥ 0.6×) to fill a scene, but prefer `min_s` ≥ scene length.
- Remaking an existing video: total ≥ 90% of original duration (aim 100–120%); cover every original point.
- Validate: `.venv/bin/python -c "import json,jsonschema;jsonschema.validate(json.load(open('X.storyboard.json')),json.load(open('schemas/storyboard.schema.json')))"`.

## Blends (orchestrator composes; `formats` max 2)
- **explainer + job-aid** (most common): job-aid skill derives a one-pager from this lesson's do_dont/checklist scenes.
- **explainer + branching**: explainer teaches, then one `decision` scene + `branching` graph for a scenario check.
- **explainer + series**: cut 30–60 s nudges from the recap/flashcards (tcs-format-series).
- **explainer + cartoon**: short `cartoon` story cold-open, explainer body. Keep ≥ 60% explainer scenes.

## References (load on demand)
- `references/playbook.md` — when to use, beats + timings, template map, do/don't, worked example.
- `templates/script_template.md`, `templates/broll_shotlist.yaml`, `templates/example.storyboard.json`.
- `QUALITY.md` (plugin root) — release checklist.

# Explainer playbook

## When to use
- Concept + "how it works" + "what to do" topics (threats, policies, processes) for broad audiences.
- Source is a deck, policy or talking-head video; no strong story or characters needed.
- Prefer **doodle** for abstract cause→effect told visually, **cartoon** when behaviour change needs emotion/story,
  **screencast-sim** when the objective is a software procedure.

## Duration
| Lesson | Length | Scenes | Words @150 wpm |
|---|---|---|---|
| Micro | 1–2 min | 6–9 | 150–300 |
| Standard | 2.5–5 min | 10–18 | 375–750 |
| Deep | 5–8 min (split in parts ≥ 6 min) | 18–30 | 750–1200 |

## Beat structure (standard 3–4 min)
| # | Beat | Time | Template(s) |
|---|---|---|---|
| 1 | Title | 4–7 s | `title` |
| 2 | Hook (why it matters to *me*) | 10–15 s | `broll` + chips, or `stat` (sourced) |
| 3 | What it is | 10–15 s | `definition` |
| 4 | How it works | 15–25 s | `steps` / `process_flow` / `timeline` |
| 5 | Real-looking example | 20–35 s | `email_mock` / `chat_mock` / `browser_mock` / `mfa_prompt` / `popup` with callouts |
| 6 | Warning signs | 12–20 s | `broll_panel` / `icon_grid` / `bullets` |
| 7 | Consequences (personal → company) | 12–20 s | `bullets` (tone warn) / `comparison` |
| 8 | What to do | 15–25 s | `do_dont` / `steps` |
| 9 | Quick check | 10–15 s | `quiz` |
| 10 | Recap | 8–12 s | `checklist` |
| 11 | Outro | 4–6 s | `outro` (+ `evidence_line` if compliance) |

Rhythm: B-roll or mock-up every 8–20 s; never > 2 text boards in a row; one idea per scene; 5–35 s per scene.

## Motion graphics map
| Content | Template | Notes |
|---|---|---|
| 3–6 parallel points | `bullets` / `icon_grid` | icons from kit subset; `tone` warn/safe |
| Sequence | `steps` (≤6) / `process_flow` (branches) | |
| Before/after, wrong/right | `do_dont` / `comparison` | cues: left items then right items |
| Number | `stat` | only with `source` + claim |
| Quote / rule of thumb | `statement` | |
| Data | `table` (≤ 5 rows on screen) | |
| Over footage | `broll` (≤2 chips) / `broll_panel` (≤5 items) | |

## B-roll shot list rules
- Query = who + action + setting ("colleagues talking at office desk"). Avoid "hacker", "matrix", "code rain".
- One shot per scene; `min_s` ≥ planned scene seconds (fetch ≥ 12 s clips).
- Record `provider`, `path`, `license` (Pexels/Pixabay licence string + URL) after fetch.
- Reject: visible logos/brands, readable screens, text overlays, off-topic, low light.

## Do / Don't
| Do | Don't |
|---|---|
| Speak to "you"; concrete examples | Lecture definitions for > 20 s |
| Reveal with `^` as words are said | Show all bullets at once |
| Fictional brand `Northwind Co.`, `.example` domains | Real company logos, real people |
| Recap = the actions, not the theory | End on consequences without a "what to do" |
| Top or full subtle border on cards | One-sided thick accent borders |

## Worked example (fragment: `templates/example.storyboard.json`)
"Spot a Phishing Email" — 10 scenes, ~100 s of narration: title → broll hook → definition → steps (bait/hook/catch/damage)
→ `email_mock` with 4 callouts (look-alike domain, generic greeting, deadline, button) → `broll_panel` signs → `do_dont`
→ `quiz` (Q1) → `checklist` recap → `outro` with ISO 27001 evidence line. Extend to 3 min by adding consequences +
a second mock-up (`chat_mock` smishing) for a standard lesson.

### template: broll_shotlist.yaml
```yaml
# B-roll shot list → copied into storyboard.json `broll_shots[]` (schema: id, query, provider, path, min_s, license)
# Query = who + action + setting. No logos, no readable screens, no hoodie hackers / matrix code.
- id: hook            # referenced by scenes[].props.shot
  query: "person reading email on laptop in office"
  provider: pexels     # pexels | pixabay | local
  min_s: 12            # >= planned scene length; renderer loops/slows (>=0.6x) if shorter
  # path: filled by the renderer/fetcher
  # license: "Pexels License — https://www.pexels.com/license/ — <clip url>"
- id: inbox
  query: "hands typing on laptop keyboard close up"
  provider: pexels
  min_s: 12
- id: team
  query: "colleagues talking at office desk"
  provider: pexels
  min_s: 12
```

### template: script_template.md
```markdown
# Explainer script — <lesson_id> · <title>

Language: en-US | ar-EG | ar-MSA · Target: <duration_min> min · wpm: 150 (AR 130) · Word budget: <min×wpm>
Objectives: O1 <text> · O2 <text>
Music: explainer | executive · Voice: narrator (assets/voices.yaml)

| # | scene id | beat | template | narration (`^` = reveal cue) | props (on-screen text) | claims (S##/#chunk or GK) | B-roll shot | ~s |
|---|---|---|---|---|---|---|---|---|
| 1 | s01_title | title | title | Welcome… | title, sub, icon | GK | — | 5 |
| 2 | s02_hook | hook | broll | … ^ … | chips ≤2 | S01#c2 | hook | 12 |
| 3 | s03_what | what | definition | ^ term… ^ note… | term, def, note | | — | 14 |
| 4 | s04_how | how | steps | ^ one ^ two ^ three | steps[≤6] | | — | 18 |
| 5 | s05_example | example | email_mock | ^ flag 1 … ^ flag 4 | email{}, callouts[cue] | | — | 26 |
| 6 | s06_signs | signs | broll_panel | ^ … ^ … ^ … | title, items[≤5] | | inbox | 15 |
| 7 | s07_impact | consequences | bullets | ^ … | items[≤6] tone warn | | — | 15 |
| 8 | s08_do | actions | do_dont | ^ don't… ^ do… | dont[], do[] | | — | 16 |
| 9 | s09_quiz | check | quiz | question (pause 2.2) / ^ answer | quiz_item, q, options, answer | | — | 14 |
| 10 | s10_recap | recap | checklist | ^ … ×N | items[≤7] | | — | 12 |
| 11 | s11_outro | outro | outro | Thanks… | line, evidence_line | GK | — | 5 |

Coverage check (remakes): every original point → scene id ✓ · Total ≥ 90% of original duration.
```


# FORMAT: doodle


# tcs-format-doodle

## Purpose
Express one approved lesson as a whiteboard draw-on sequence: every visual element is a `whiteboard` item that is
"drawn" when its `^` cue is spoken. Ideal for cause→effect chains, mental models and simple processes.

## Inputs
- Approved lesson from `curriculum.yaml` (objectives, `duration_min`), facts from `sources.yaml`.
- Persona ids (`assets/characters/personas.yaml`, domain `personas.yaml`) — doodle draws them in ink line-art.
- Domain `format_defaults.yaml` (music `whiteboard`), theme preset `whiteboard` from `assets/theme_presets.yaml`.

## Outputs
- `scenes[]` built mainly from `whiteboard` (the draw-on spec), framed by `title`, `quiz`, `checklist`, `outro`
  (render in ink style when `theme.preset: whiteboard`). Optional `definition` / `steps` for dense recaps.
- `theme.preset: "whiteboard"`, `music.bed: "whiteboard"`, `cast[]` of personas drawn.
- The draw-on sequence spec = `props.items[]` in cue order:
  `{cue, kind: person|icon|note|arrow|circle|underline|box|cross|check, cast?, pose?, expr?, icon?, text?, x, y, w?, h?, to?, color: ink|attention|safe}`.
- Fill-ins: `templates/script_template.md`, `templates/drawon_spec.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Map objectives to 3–6 "boards" (one idea each, 10–25 s). Plan a left→right / top→bottom reading path per board.
2. Script narration per board; place `^` before the word that should trigger each drawing. Several items may share a cue.
3. Lay out items on the 1920×1080 stage (9:16: 1080×1920; 1:1: 1080×1080). Keep a 96 px safe margin;
   people feet `y` ≈ 860–900 on 16:9; notes ≤ 4 words, handwriting ≥ 40 px.
4. Use `color: attention` only for the one thing to notice per board; `safe` for correct actions; `ink` otherwise.
5. Add claims per scene, quick check (`quiz`), recap (`checklist`), `outro`.
6. Validate schema + cue counts (max `cue` + 1 ≤ number of `^`).

## Rules / QA
- ≤ 8 items per board, ≤ 3 per cue; leave ≥ 1.2 s between draw cues so strokes finish (renderer draws in ~1.2 s).
- Text only in `note`/`text` props (≥ 40 px handwriting at 1080p); never as part of drawings or generated images.
- Arrows: `x,y` → `to{x,y}` must land on the target item's bounding box — verify with QA stills.
- White ground, navy ink, one attention colour (orange) — never cream paper or terracotta.
- RTL: notes are mirrored by the kit; place reading order right→left for Arabic (`x` mirrored automatically if `direction: rtl`).

## Blends
- **doodle + job-aid**: the last board's checks become the job-aid checklist.
- **doodle + series**: each board is a 30–45 s nudge (one board + flashcard).
- **doodle + branching**: whiteboard sets up the dilemma, `decision` scene branches (keep ink style).

## References
- `references/playbook.md` — beats, timings, layout grid, do/don't, worked example.
- `templates/drawon_spec.md`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Doodle / whiteboard playbook

## When to use
- Abstract mechanisms (how an attack chain works, why a rule exists), mental models, short "rules of three".
- Low budget, fast to localize (few on-screen words), calm tone.
- Avoid for software procedures (screencast-sim) or emotional behaviour change (cartoon).

## Duration
| Lesson | Length | Boards | Draw cues per board |
|---|---|---|---|
| Micro | 45–90 s | 3–4 | 3–5 |
| Standard | 2–4 min | 6–10 | 4–8 |
| Deep | 4–6 min | 10–16 | 4–8 |

## Beat structure (2.5 min)
| # | Beat | Time | Template |
|---|---|---|---|
| 1 | Title | 4–6 s | `title` (ink style) |
| 2 | Character + problem drawn | 12–18 s | `whiteboard` (person, note, arrow) |
| 3 | How it works (chain) | 15–25 s | `whiteboard` (icons + arrows L→R) |
| 4 | Levers / signs | 12–20 s | `whiteboard` (3 icons + notes + underline) |
| 5 | Consequence | 10–15 s | `whiteboard` (cross on the bad outcome) |
| 6 | Rules (what to do) | 12–20 s | `whiteboard` (checks + notes, `safe`) |
| 7 | Quick check | 10–14 s | `quiz` |
| 8 | Recap | 8–12 s | `checklist` |
| 9 | Outro | 4–6 s | `outro` |

## Layout grid (16:9 stage 1920×1080)
| Zone | x | y | Use |
|---|---|---|---|
| Left figure | 300–480 | feet 860–900 | protagonist |
| Centre | 760–1160 | 300–700 | chain icons/notes |
| Right figure | 1440–1620 | feet 860–900 | other party |
| Title band | 96–1824 | 80–160 | `props.title` |
9:16: stack zones vertically (title 120–220, figure feet ~1100, notes 1300–1700). Keep 96 px margins.

## Draw-on timing
- Each item draws in ~1.2 s from its cue; notes write at ~12 chars/s.
- Hold ≥ 1.5 s after the last item (`hold`) so the finished board reads.
- Camera: one board per scene; the renderer may pan between consecutive boards.

## Do / Don't
| Do | Don't |
|---|---|
| 1 idea per board, ≤ 8 items | Fill the board with paragraphs |
| One attention-coloured element per board | Colour everything orange |
| Notes ≤ 4 words | Full sentences in handwriting |
| Draw the person first, then the action | Reveal items before they are said |

## Worked example (`templates/example.storyboard.json`)
"How Social Engineering Works": attacker (vex, sly) → arrow → learner on phone → note "tricks people" → key circled
(4 cues); levers board (clock/badge/heart + notes + underline); rules board (3 checks); quiz; outro. ~45 s fragment;
add consequence + example boards for a 2.5-min lesson.

### template: drawon_spec.md
```markdown
# Draw-on sequence spec — <scene id>

Board title: <≤ 5 words>   Aspect: 16:9 | 9:16 | 1:1   Duration ~<s>

| cue | kind | cast/pose/expr or icon | text (≤4 words) | x | y | w×h / to | color | spoken trigger word |
|---|---|---|---|---|---|---|---|---|
| 0 | person | vex / rub / sly | | 380 | 880 | | ink | "Meet…" |
| 1 | arrow | | | 560 | 600 | to 1180,600 | attention | "goes straight…" |
| 1 | person | learner / phone / neutral | | 1400 | 880 | | ink | |
| 2 | note | | tricks people | 760 | 520 | | ink | "tricks" |
| 3 | icon | key | | 1600 | 300 | | attention | "password" |
| 3 | circle | | | 1600 | 300 | 180×180 | attention | |

Checks: max cue + 1 ≤ number of `^` in narration · ≤ 8 items · ≤ 3 items per cue · arrows land on targets · 96 px margins.
→ Copy rows into `scenes[].props.items[]` of a `whiteboard` scene.
```

### template: script_template.md
```markdown
# Doodle script — <lesson_id> · <title>

Language · Target <min> · wpm 140 (AR 125) · Theme `whiteboard` · Music `whiteboard` · Cast: <persona ids>

| # | scene id | board idea | narration (`^` per drawing) | draw-on items (see drawon_spec.md) | claims | ~s |
|---|---|---|---|---|---|---|
| 1 | s01_title | title | Welcome… | title, sub | GK | 5 |
| 2 | s02_problem | who + problem | ^ Meet… ^ … | person, arrow, note | | 15 |
| 3 | s03_chain | how it works | ^ … ^ … ^ … | icons + arrows | | 20 |
| 4 | s04_signs | signs/levers | ^ … ×3 ^ underline | icons, notes, underline | | 15 |
| 5 | s05_cost | consequence | ^ … | cross, note | | 12 |
| 6 | s06_rules | what to do | ^ ✓ … ×3 | check + note ×3 (safe) | | 15 |
| 7 | s07_quiz | check | Q (pause 2.2) / ^ A | quiz props | | 12 |
| 8 | s08_recap | recap | ^ … ×N | checklist | | 10 |
| 9 | s09_outro | outro | … | line | GK | 5 |
```


# FORMAT: cartoon


# tcs-format-cartoon

## Purpose
Change behaviour through story: a relatable persona makes (or nearly makes) the mistake, consequences land,
a mentor shows the right move, and teaching beats (steps/quiz/recap) lock it in.

## Inputs
- Approved lesson (`curriculum.yaml`), facts (`sources.yaml`).
- Personas: `assets/characters/personas.yaml` (+ each `character_sheet.md`) and domain `personas.yaml`
  (e.g. security pack adds `vex`). Scenario premises: domain `scenarios.md`.
- Voices: `assets/voices.yaml` (one distinct voice per speaking persona, per language).

## Outputs
- `cast[]` (persona ids), `voices{}` keyed by persona id (key = `who` in lines = `people[].cast`, so mouths lip-sync).
- `scenes[]`: story beats as `cartoon` scenes —
  `{set, night?, desk?, people[≤5]{cast,x,y,s,pose,expr,flip,holding,lowerHidden}, beats[]{cue,cast,pose,expr,move_to,camera,sfx}, bubbles[]{cue,out_cue,who,text,think,tone}}`;
  UI moments as `email_mock`/`chat_mock`/`mfa_prompt`/`popup`/`browser_mock`; teaching beats as `steps`/`do_dont`/`icon_grid`;
  `quiz`, `checklist`, `outro`. `music.bed: "cartoon"`.
- Fill-ins: `templates/script_template.md`, `templates/cast_sheet.yaml`; fragment `templates/example.storyboard.json`.

## Steps
1. Pick a premise (domain `scenarios.md`) that hits the lesson objectives; choose 2–4 personas (protagonist `rookie`
   or `learner`, antagonist if any, `mentor`). Keep personas consistent across the course.
2. Outline the arc (playbook): setup → temptation → mistake/near-miss → consequence → mentor fix → rule → check.
3. Write lines: narrator frames, characters speak short lines (≤ 15 words). `^` before each acting beat or bubble.
4. Stage each `cartoon` scene: pick `set` from enums; place people (feet `y` ≈ 1060 at `s` 1.2–1.4 for 16:9);
   change pose/expression on cues; ≤ 1 camera move per scene; bubbles ≤ 10 words, `tone: villain` only for the antagonist.
5. Add teaching scenes after the story turns (not inside long dialogue). Add `quiz`, recap, outro.
6. Claims: story events are `general_knowledge` only if illustrative; every rule/sign stated must be sourced.
7. Validate schema + cues; check every `who` has a `voices` entry.

## Rules / QA
- Use only enum poses/expressions/sets; the antagonist is the only persona wearing the attention colour.
- No real people, brands or recognisable likenesses; fictional company "Northwind Co.".
- Every story scene has acting (≥ 1 pose/expr change on a cue) and the narrator/mentor ties it back to the lesson.
- Humour punches at the situation, never at a group or nationality; Egyptian-Arabic jokes reviewed by a native speaker.
- Character voices: distinct timbre + acting `instructions`; avoid two personas on the same voice in one scene.
- Generated character images (if any) use the locked prompt in `assets/characters/<id>/prompt.txt` (no text).

## Blends
- **cartoon + branching**: story stops at a `decision` scene; outcomes are short cartoon scenes (see tcs-format-branching).
- **cartoon + series**: recurring cast = the series hook; one micro-drama per episode, nudges replay the key beat.
- **cartoon + job-aid**: the mentor's steps become the job-aid.
- **cartoon + explainer**: cartoon cold-open + explainer teaching body.

## References
- `references/playbook.md`, `templates/cast_sheet.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Cartoon / micro-drama playbook

## When to use
- Behaviour under pressure (urgency, authority, fatigue, kindness exploited), culture, soft skills.
- Audience is broad and fatigued by "slides"; you need recall through story.
- Avoid for dense reference content (narrated-deck / job-aid) or exact UI procedures (screencast-sim).

## Duration
| Variant | Length | Story scenes | Teaching scenes |
|---|---|---|---|
| Micro-drama | 60–120 s | 3–5 | 1–2 + quiz |
| Standard | 2.5–5 min | 8–14 | 3–5 + quiz |
| Two-part | 2 × 3–5 min | part 1 story + cliff-hanger, part 2 mentor fix | |

## Beat structure (3 min)
| # | Beat | Time | Template | Acting |
|---|---|---|---|---|
| 1 | Title | 4–6 s | `title` | |
| 2 | Setup (normal day) | 10–15 s | `cartoon` | protagonist idle → happy |
| 3 | Inciting moment | 10–15 s | `cartoon` + `chat_mock`/`email_mock`/`mfa_prompt` | phone pose, worried |
| 4 | Temptation / pressure | 10–20 s | `cartoon` (antagonist bubble `villain`) | sly, rub |
| 5 | Mistake or near-miss | 8–12 s | `cartoon` + `popup` | facepalm / shocked, camera zoom |
| 6 | Consequence | 10–15 s | `cartoon` / `bullets` warn | sad |
| 7 | Mentor turn | 12–20 s | `cartoon` (mentor present/stop) | |
| 8 | The rule | 12–20 s | `steps` / `do_dont` | |
| 9 | Replay done right | 10–15 s | `cartoon` | cheer |
| 10 | Quick check | 10–14 s | `quiz` | |
| 11 | Recap + outro | 10–15 s | `checklist`, `outro` | |

## Staging cheat-sheet (16:9, 1920×1080)
- Two-shot: x 700 / 1250, `s` 1.2, second person `flip: true` to face the first.
- Single close: x 960, `s` 1.3–1.5, camera `{zoom:1.35–1.5, x:960, y:520}` on the punchline cue.
- Desk scenes: `desk: true`, `lowerHidden: true` for seated persons.
- 9:16: one person per frame, `s` 1.6, feet y ≈ 1700; bubbles above head.
- Night/home for "after hours" pressure (MFA fatigue, smishing); `den` for the antagonist.

## Voices
One voice per persona (assets/voices.yaml), instructions describe acting ("flustered, fast, comic").
Narrator ≠ any character voice. Arabic: Egyptian colloquial for characters, narrator may be MSA or Egyptian per brief.

## Do / Don't
| Do | Don't |
|---|---|
| Short lines, big reactions | Monologues > 20 s in a bubble |
| Show the mistake *and* the redo | End on the failure |
| Mentor explains the why in one line | Mock the protagonist |
| Antagonist playful, not scary | Gore, threats, hoodie hacker clichés |

## Worked example (`templates/example.storyboard.json`)
"Midnight Push Notifications" (MFA fatigue): rookie at home at night → `mfa_prompt` counting to 12 → vex in den
("Everyone taps Approve eventually") → mentor in office (deny + report + reset) → `steps` → `quiz` → `outro`.
~50 s fragment; add consequence + replay beats for a 2.5-min lesson.

### template: cast_sheet.yaml
```yaml
# Per-course cast sheet (cartoon/comic/branching). Persona ids come from assets/characters/personas.yaml
# (+ domain pack personas). Keep the same persona in the same role for the whole course/series.
course_id: <course-id>
cast:
  - id: rookie          # protagonist who makes the mistake
    display_name: Sam   # on-screen/bubble name; localize (ar-EG: سام)
    role_in_story: "busy employee, too trusting"
    voice: {provider: openai, voice: ballad, instructions: "Good-natured office worker in a comic cartoon; quick to panic."}
  - id: mentor
    display_name: Omar
    role_in_story: "security expert who shows the right move"
    voice: {provider: openai, voice: echo, instructions: "Calm, friendly expert; warm, clear, dry humour."}
  - id: vex             # domain pack persona (security-awareness): the attacker, only one wearing the attention colour
    display_name: Vex
    role_in_story: "con artist"
    voice: {provider: openai, voice: verse, instructions: "Smug, theatrical cartoon con-artist, playful not scary."}
sets_used: [office, home, den]
running_gags: ["rookie's coffee cup appears in every office scene"]
```

### template: script_template.md
```markdown
# Cartoon script — <lesson_id> · <title>

Premise (from domain scenarios.md): <one line> · Cast: <ids> · Music `cartoon` · Target <min>

| # | scene id | beat | template | set | lines (who: text, `^` = acting/bubble cue) | staging (people, beats, camera, bubbles) | claims | ~s |
|---|---|---|---|---|---|---|---|---|
| 1 | s01_title | title | title | — | narrator: … | | GK | 5 |
| 2 | s02_setup | setup | cartoon | office | narrator: ^ … | rookie x960 s1.3 idle→happy@0 | GK | 12 |
| 3 | s03_incite | inciting | cartoon / chat_mock | home | rookie: ^ … | phone pose, worried@0, zoom@1 | S##/#c | 12 |
| 4 | s04_pressure | pressure | cartoon | den | vex: ^ … | vex sly, bubble tone villain | | 8 |
| 5 | s05_mistake | mistake | cartoon / popup | office | narrator: ^ No… | facepalm@0, sfx womp | | 10 |
| 6 | s06_cost | consequence | cartoon / bullets | | | | | 12 |
| 7 | s07_mentor | mentor | cartoon | office | mentor: ^ … | mentor present → stop | | 15 |
| 8 | s08_rule | rule | steps / do_dont | — | mentor: ^ ×N | | | 15 |
| 9 | s09_redo | done right | cartoon | | | cheer | | 12 |
| 10 | s10_quiz | check | quiz | — | Q (pause 2.2) / ^ A | | | 12 |
| 11 | s11_outro | outro | outro | — | … | | GK | 5 |
```


# FORMAT: comic


# tcs-format-comic

## Purpose
Tell a short scenario in 3–12 panels that work both as a readable page (lesson/job-aid/HTML/PDF targets) and as a
motion comic (video: panels reveal on `^` cues with narration and character voices).

## Inputs
- Approved lesson (`curriculum.yaml`), facts (`sources.yaml`), domain `scenarios.md` premises.
- Personas (`assets/characters/personas.yaml`, domain `personas.yaml`), voices (`assets/voices.yaml`).

## Outputs
- `scenes[]` of `comic` pages: `{layout: "1"|"2"|"3"|"2x2"|"1+2"|"3-row", panels[≤4]{cue, set, people[]{cast,x,y,s,pose,expr,flip,holding}, caption, bubbles[]{who,text,think}, sfx_word}}`,
  framed by `title`, a teaching scene (`do_dont`/`steps`/`checklist`), `quiz`, `outro`.
- Panel layout plan (fill-in `templates/panel_layout.md`) and dialogue script (`templates/script_template.md`).
- `aspect`: `9:16` + `3-row`/`1+2` for webtoon/mobile; `16:9` + `2x2`/`3`/`2` for desktop strips; `1:1` + `2x2` for social.
- Fragment `templates/example.storyboard.json`.

## Steps
1. Choose premise + 2–3 personas; outline 3 acts: situation → wrong move/pressure → right move.
2. Split into pages of ≤ 4 panels (layout picks), 1 action per panel; plan "camera" (wide → medium → close).
3. Write captions (≤ 12 words, narrator voice) and balloons (≤ 12 words, max 2 per panel).
4. Stage people in panel coordinates (panel = 1280×1000 virtual stage; feet y ≈ 1000; `s` 0.9–1.1).
5. Narration for motion comic: one `^` per panel reveal (panel `cue`), characters' lines read with their voices.
6. Add the teaching scene, quiz and outro; claims per scene; validate.

## Rules / QA
- Text only in `caption`, `bubbles[].text`, `sfx_word` props — never in generated art.
- ≤ 4 panels per scene (schema max), ≤ 2 balloons per panel, ≥ 28 px balloon text at 1080p.
- Reading order: LTR → left-to-right/top-down; RTL (`direction: rtl`) → panels and balloon tails mirror (kit handles);
  write Arabic balloons in Egyptian colloquial for dialogue, MSA for captions only if the brief asks.
- Antagonist balloons may use `think` for asides; keep humour kind.
- Static targets (PDF/HTML/job-aid) must read without audio: captions carry the narration's key point.

## Blends
- **comic + job-aid**: last page = the job-aid card; good for printable posters.
- **comic + series**: one page per week (webtoon episode) + flashcard nudge.
- **comic + branching**: final panel is a `decision` scene; outcomes are one-page comics.
- **comic + quiz** (via tcs-assessment): "spot the red flag in panel 2" scenario items.

## References
- `references/playbook.md`, `templates/panel_layout.md`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Comic / webtoon playbook

## When to use
- Short scenarios that must work **without audio** (intranet, posters, mobile reading, printed handouts).
- Physical-security and etiquette topics (tailgating, clear desk, visitor handling) and quick "spot the mistake" stories.
- Avoid for multi-step procedures (screencast-sim) or abstract mechanisms (doodle).

## Duration / size
| Variant | Panels | Read time | Motion comic |
|---|---|---|---|
| Strip | 3–4 | 20–40 s | 30–60 s |
| Page set | 6–8 | 1–2 min | 1.5–2.5 min |
| Webtoon episode (9:16) | 9–12 | 2–3 min | 2–3 min |

## Beat structure (6–8 panels)
| # | Beat | Panels | Layout |
|---|---|---|---|
| 1 | Title card | — | `title` scene |
| 2 | Situation (wide) | 1 | `1+2` first panel or `3-row` row 1 |
| 3 | Pressure / temptation | 1–2 | |
| 4 | Wrong move + consequence | 1–2 | |
| 5 | Rewind: right move | 2–3 | new page, same set |
| 6 | Rule | — | `do_dont` / `checklist` |
| 7 | Check | — | `quiz` |

## Layout picks
| Layout | Aspect | Use |
|---|---|---|
| `3-row` | 9:16 | webtoon scroll, one beat per row |
| `1+2` | 9:16 / 16:9 | establishing shot + two reactions |
| `2x2` | 16:9 / 1:1 | classic 4-panel gag |
| `3` / `2` | 16:9 | horizontal strip |
| `1` | any | splash / reveal |

## Panel craft
- Vary shot size: wide (s 0.8, people small) → medium (s 1.0) → close (s 1.3, one person).
- Balloon text ≤ 12 words; caption box top-left (top-right in RTL).
- `sfx_word` for one onomatopoeia per page max ("CLICK", "BUZZ") — it is on-screen text; translate it.
- Keep the same set across a rewind so the contrast is obvious.

## Do / Don't
| Do | Don't |
|---|---|
| One action per panel | Two events in one panel |
| Show consequence, then rewind | Moralise in long captions |
| Diverse, neutral personas | Real people, brands, uniforms of real firms |
| Translate captions, balloons, sfx words | Leave English sfx in Arabic pages |

## Worked example (`templates/example.storyboard.json`)
"The Friendly Tailgater" (9:16): page 1 `3-row` (courier with boxes → "hold the door?" → inside, "Too easy." + CLICK);
page 2 `1+2` rewind (learner points to reception → manager confirms → cheer); `do_dont`; `outro`.

### template: panel_layout.md
```markdown
# Panel layout — <lesson_id> · <title>

Aspect: 9:16 (webtoon) | 16:9 | 1:1 · Reading direction: LTR | RTL · Cast: <ids>

## Page <n> — scene id `s0n_page<n>` — layout `3-row | 1+2 | 2x2 | 3 | 2 | 1`
| panel | cue | set | shot | people (cast, x, pose, expr, holding, flip) | caption (≤12 w) | balloons (who: text ≤12 w, think?) | sfx_word |
|---|---|---|---|---|---|---|---|
| 1 | 0 | reception | wide | vex 640 hold happy paper | 8:58 a.m. Arms full of boxes. | — | — |
| 2 | 1 | reception | medium | learner 420 idle card; vex 760 hold | — | vex: Could you hold the door? | — |
| 3 | 2 | openOffice | close | vex 600 rub sly | — | vex (think): Too easy. | CLICK |

Panel virtual stage 1280×1000, feet y ≈ 1000. Max 4 panels per scene; split longer pages into several `comic` scenes.
```

### template: script_template.md
```markdown
# Comic script (motion comic narration) — <lesson_id>

| scene id | panel cue | who | line (`^` opens the panel) | read-only fallback (caption carries this point) |
|---|---|---|---|---|
| s02_page1 | 0 | narrator | ^ Nine o'clock. A courier waits by the secure door. | caption panel 1 |
| s02_page1 | 1 | vex | ^ Could you hold the door? | balloon |
| s02_page1 | 2 | narrator | ^ One polite gesture, and a stranger is inside. | caption needed in static version |
| s03_page2 | 0–2 | … | rewind: right move | |
| s04_rule | — | narrator | ^ don't… ^ do… | do_dont |
| s05_quiz | — | narrator | Q (pause 2.2) / ^ A | quiz |
```


# FORMAT: narrated-deck


# tcs-format-narrated-deck

## Purpose
Produce a clean, accessible deck that a trainer can present live (speaker notes) or that plays as a narrated
video/HTML lesson (VO = narration). Best for policy, onboarding, compliance and reference-heavy lessons.

## Inputs
- Approved lesson (`curriculum.yaml`; `targets` usually include `deck`, often `lesson`/`video`/`scorm`).
- Facts from `sources.yaml` (decks/policies are the typical source — keep their structure where it is good).
- Theme preset + layout preset (`assets/theme_presets.yaml`, `assets/layout_presets.yaml`), voice (`assets/voices.yaml`).

## Outputs
- `scenes[]` = slides, each a template: `title`, `section`, `bullets`, `icon_grid`, `steps`, `process_flow`, `timeline`,
  `comparison`, `do_dont`, `table`, `stat`, `definition`, `statement`, `checklist`, `quiz`, `image`, `outro`
  (+ mock-ups when demonstrating a screen).
- `narration[]` = voice-over **and** speaker notes (renderer writes narration text into PPTX notes).
- `scenes[].notes` = presenter-only notes (facilitation tips, questions to ask, timing) — not voiced.
- `on_screen_text[]` optional (derived if omitted) for alt text / translation.
- Fill-ins `templates/script_template.md`, `templates/speaker_notes.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Outline: title → agenda (`section`) → 1 slide per key point → practice/check → summary → next steps.
2. One message per slide; slide title = the message as a short sentence or label.
3. Choose the template that fits the content (playbook map). ≤ 6 bullets, ≤ 8 words each; tables ≤ 5 rows × 4 cols.
4. Write VO: 30–90 s per slide; `^` per bullet/row/node reveal (one click per `^` in PPTX animations).
5. Add `notes` for live presenters (questions, examples from the client, timing).
6. Insert a `quiz` slide every 5–8 slides for long decks; final `checklist` summary; `outro` with next lesson.
7. Claims per slide; validate.

## Rules / QA
- No text-heavy slides: if VO and slide say the same 30 words, cut the slide text to keywords.
- Contrast ≥ 4.5:1, text ≥ 24 px at 1080p (≈ 18 pt on a 13.33 in slide), slide numbers on, alt text for images.
- Arabic deck: `direction: rtl`, Arabic font from theme, mirrored layouts, Western or Arabic-Indic digits consistently (per brief).
- Logo slot empty unless the brief supplies one. No stock photos with text/brands.
- Keep source deck order only if it serves the objectives; record reorderings in claims/notes.

## Blends
- **narrated-deck + job-aid**: summary slide → printable one-pager.
- **narrated-deck + screencast-sim**: deck explains the policy, sim practises the tool.
- **narrated-deck + branching**: a scenario slide with `decision` choices for live discussion or SCORM.
- **narrated-deck + series**: each section becomes a short episode for spaced delivery.

## References
- `references/playbook.md`, `templates/speaker_notes.md`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Narrated-deck playbook

## When to use
- Policies, onboarding, compliance refreshers, processes with rules and limits; instructor-led sessions.
- Client needs an editable PPTX as well as video/HTML/SCORM.
- Avoid for emotional behaviour change (cartoon) or "how to use the tool" (screencast-sim).

## Duration
| Variant | Slides | VO | Notes |
|---|---|---|---|
| Micro | 5–8 | 3–6 min | 1 objective |
| Standard | 10–20 | 8–15 min | quiz every 5–8 slides |
| Live session | 15–30 | 30–60 min live | VO optional, notes required |

Per slide: 30–90 s VO (≈ 75–225 words at 150 wpm). Over 90 s → split the slide.

## Beat structure (standard)
| # | Slide | Template |
|---|---|---|
| 1 | Title | `title` |
| 2 | Why this matters | `statement` / `stat` (sourced) |
| 3 | Agenda / objectives | `section` + `bullets` |
| 4–n | One key point each | `bullets` / `steps` / `table` / `process_flow` / `comparison` / `definition` |
| … | Example or demo | mock-up / `image` |
| … | Practice | `quiz` / `decision` |
| n-1 | Summary | `checklist` |
| n | Next steps / contacts | `outro` (+ `evidence_line`) |

## Template map
| Content | Template |
|---|---|
| Rules, conditions | `bullets` (icons), `do_dont` |
| Limits, matrices | `table` |
| Approval path | `process_flow` |
| Chronology / deadlines | `timeline` |
| Options compared | `comparison` |
| Key term | `definition` |

## Speaker notes pattern
VO = what the narrator says (also exported as notes). `notes` = presenter extras:
`Ask: … · Example: … · If asked about X: … · Time: 2 min`.

## Do / Don't
| Do | Don't |
|---|---|
| Message title per slide | "Overview" titles |
| ≤ 6 bullets, keywords | Paragraphs on slides |
| Reveal one point per click (`^`) | Read the slide verbatim |
| Tables ≤ 5 rows | Screenshot of a spreadsheet |
| Consistent digits and RTL mirroring | Mixed LTR layout in an Arabic deck |

## Worked example (`templates/example.storyboard.json`)
"Submitting Expense Claims" (fictional Northwind policy): title → four rules (`bullets`) → limits (`table`) →
approval path (`process_flow` with decision) → pre-submit `checklist` → `quiz` → `outro`. Speaker `notes` on slides 1–3.

### template: script_template.md
```markdown
# Narrated deck — <lesson_id> · <title>

Targets: deck + (lesson | video | scorm) · Language · Slides <n> · VO <min>

| slide | scene id | message title | template | on-slide text (props) | VO (`^` = click) | presenter notes | claims | ~s |
|---|---|---|---|---|---|---|---|---|
| 1 | s01_title | <course> | title | kicker, title, sub | Welcome… | Ask who… | GK | 10 |
| 2 | s02_why | <why it matters> | statement / stat | | | | S## | 40 |
| 3 | s03_agenda | Today | section | | | | GK | 20 |
| 4 | s04_point1 | <message> | bullets | ≤6 items | ^ ×N | | | 60 |
| 5 | s05_point2 | <message> | table | columns, rows ≤5 | ^ | | | 60 |
| 6 | s06_flow | <message> | process_flow | nodes, edges | ^ per node | | | 50 |
| 7 | s07_check | Quick check | quiz | q, options, answer | Q (pause 2.2) / ^ A | | | 25 |
| 8 | s08_summary | Remember | checklist | ≤7 | ^ ×N | | | 30 |
| 9 | s09_outro | Next steps | outro | line, tips, evidence_line | | | GK | 10 |
```

### template: speaker_notes.md
```markdown
# Speaker notes — slide <n> `<scene id>`

**On slide (props):** <title> · <≤6 keyword bullets>
**Voice-over / notes (narration):** <30–90 s; `^` before each point = one click>
**Presenter only (`notes`):**
- Ask: <question to the room>
- Example: <client-specific example to add live>
- If asked: <likely question → short answer + source id>
- Time: <minutes>
**Sources:** <S01#p3, …> · **Alt text (images):** <one sentence>
```


# FORMAT: mindmap


# tcs-format-mindmap

## Purpose
Show how a topic is structured — categories, sub-types, relationships — by growing a tree node by node.
Great for overviews, taxonomies (types of malware, data classes), module intros and recaps.

## Inputs
- Approved lesson (`curriculum.yaml`), facts/glossary from `sources.yaml`, domain `glossary.yaml` for consistent labels.

## Outputs
- `mindmap` scenes: `{root, nodes[]{id, label, parent ("root" or node id), cue, icon?, tone?}, focus[]{cue, node}}`.
  The **node tree** is `nodes[]` (parent links); the **reveal timeline** is the `cue` on each node + `focus[]`.
- Supporting scenes: `title`, `definition` (zoom into one node), `comparison`, `quiz`, `checklist`, `outro`.
- Fill-ins `templates/node_tree.yaml`, `templates/script_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Build the tree first (`templates/node_tree.yaml`): root = lesson topic, 3–5 branches, ≤ 3 leaves per branch, depth ≤ 3.
2. Order the reveal: branch → its leaves → next branch (depth-first) unless comparing branches (breadth-first).
3. Script narration with one `^` per node reveal; `focus` cues when the narrator dwells on a branch.
4. If one map exceeds 12 nodes, split: overview map (branches only) + one map per branch.
5. Follow with a `definition`/`comparison` zoom for the most important branch, then `quiz` + recap.
6. Claims per scene; validate (every `parent` exists; cues ascending; max cue + 1 ≤ `^` count).

## Rules / QA
- ≤ 12 nodes per scene, labels ≤ 4 words, icons from the kit subset; `tone: warn` for the risky branch only.
- Node `cue` ascending in reading order; children never appear before their parent.
- RTL: tree mirrors (root right-to-left growth) — handled by kit when `direction: rtl`; keep labels short for Arabic width.
- A mindmap scene should last 15–40 s; hold ≥ 2 s on the complete map.

## Blends
- **mindmap + explainer**: map as the module intro/recap, explainer scenes in between.
- **mindmap + job-aid**: the completed map is printed as the job-aid (static target renders final state).
- **mindmap + series**: one branch per nudge; flashcards per leaf.
- **mindmap + narrated-deck**: map slide as agenda; each branch becomes a section.

## References
- `references/playbook.md`, `templates/node_tree.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Mindmap / progressive-reveal playbook

## When to use
- Taxonomies and overviews: "types of X", "levels of Y", "who does what", module intros/recaps.
- Learners need the big picture before details; or a recap that links many items.
- Avoid for sequences (use `steps`/`process_flow`) or stories (cartoon/comic).

## Duration
| Variant | Nodes | Length |
|---|---|---|
| Single map | 6–12 | 20–40 s scene; 1–2 min lesson with zoom-ins |
| Overview + branch maps | 4 + 3×(4–8) | 2–4 min |

## Beat structure (2 min)
| # | Beat | Time | Template |
|---|---|---|---|
| 1 | Title | 4–6 s | `title` |
| 2 | Overview map (branches) | 15–25 s | `mindmap` |
| 3 | Branch A expanded | 15–30 s | `mindmap` (focus A) |
| 4 | Zoom: key term | 10–15 s | `definition` |
| 5 | Branch B / C | 15–30 s each | `mindmap` |
| 6 | Contrast branches | 10–20 s | `comparison` |
| 7 | Check | 10–14 s | `quiz` |
| 8 | Recap (full map held) | 8–12 s | `mindmap` (all cues 0) or `checklist` |
| 9 | Outro | 4–6 s | `outro` |

## Reveal timeline rules
- Depth-first for explanation, breadth-first for comparison.
- `focus` on the branch being discussed (camera eases to it); release focus on the recap.
- ≥ 1.0 s between consecutive node cues; leaves of one branch may share a cue if listed quickly.

## Tree hygiene
- Parallel labels (all nouns or all verbs per level).
- Same term as in the domain glossary (and its Arabic equivalent from `glossary.yaml`).
- No orphan nodes; no single-child branches (merge them).

## Do / Don't
| Do | Don't |
|---|---|
| ≤ 12 nodes, depth ≤ 3 | 30-node "everything" map |
| Labels ≤ 4 words | Sentences in nodes |
| One warn-toned branch | Colour-code every branch differently without meaning |

## Worked example (`templates/example.storyboard.json`)
"Data Classification at a Glance": root "Northwind data" → Public (+ website) → Internal (+ org chart) →
Confidential (+ contracts, + customer personal data) with focus on Confidential; `definition` zoom; `quiz`; `outro`.

### template: node_tree.yaml
```yaml
# Node tree + reveal timeline → copied into a `mindmap` scene's props (root, nodes[], focus[])
root: "Northwind data"           # lesson topic, ≤ 4 words
order: depth-first               # depth-first | breadth-first
nodes:                           # parent: "root" or a node id; cue = reveal order (= i-th ^ in narration)
  - {id: pub,  label: "Public",                 parent: root, cue: 0, icon: globe,    tone: safe}
  - {id: pub1, label: "Website, brochures",     parent: pub,  cue: 1}
  - {id: int,  label: "Internal",               parent: root, cue: 2, icon: building, tone: info}
  - {id: int1, label: "Org chart, policies",    parent: int,  cue: 3}
  - {id: con,  label: "Confidential",           parent: root, cue: 4, icon: lock,     tone: warn}
  - {id: con1, label: "Contracts, salaries",    parent: con,  cue: 5}
  - {id: con2, label: "Customer personal data", parent: con,  cue: 6}
focus:
  - {cue: 4, node: con}
# Limits: ≤ 12 nodes, depth ≤ 3, labels ≤ 4 words, no single-child branches.
```

### template: script_template.md
```markdown
# Mindmap script — <lesson_id> · <title>

| # | scene id | beat | template | narration (one `^` per node / focus) | props | claims | ~s |
|---|---|---|---|---|---|---|---|
| 1 | s01_title | title | title | … | title | GK | 5 |
| 2 | s02_overview | overview | mindmap | Three levels: ^ A ^ B ^ C | root + 3 branches | | 20 |
| 3 | s03_branch_a | branch A | mindmap | ^ leaf ^ leaf | branch A + leaves, focus A | | 25 |
| 4 | s04_zoom | key term | definition | ^ … | term, def | | 12 |
| 5 | s05_check | check | quiz | Q (pause 2.2) / ^ A | | | 12 |
| 6 | s06_recap | recap | mindmap / checklist | ^ … | full tree | | 10 |
| 7 | s07_outro | outro | outro | … | line | GK | 5 |
```


# FORMAT: branching


# tcs-format-branching

## Purpose
Let learners practise judgement: they face realistic pressure, choose, see consequences, and get feedback.
Skins: cartoon (default), comic, doodle or explainer mock-ups — the graph is independent of the look.

## Inputs
- Approved lesson (`curriculum.yaml`) — objectives at Bloom `apply`/`analyze`/`evaluate`.
- Facts (`sources.yaml`), scenario premises + red flags (domain `scenarios.md`), personas, voices.

## Outputs
- `decision` scenes: `{prompt, choices[≤4]{id, label, next (branching node id), correct?}, video_choice?}`.
- Outcome/feedback scenes in any template (usually `cartoon`, `statement`, `popup`, `email_mock`, `chat_mock`).
- `storyboard.branching = {start, nodes[]{id, scenes[] (scene ids in play order), outcome: continue|good|bad|neutral, feedback, score}}`.
- `formats`: `["branching", <skin>]` e.g. `["branching","cartoon"]`.
- Linear video cut: renderer plays `start` → the `correct: true` path, then optional "what if" recap of bad outcomes;
  `video_choice` names the choice id to follow in video targets (default: the correct one).
- Fill-ins `templates/decision_graph.yaml`, `templates/script_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Pick one realistic dilemma (domain `scenarios.md`) per objective; define the ideal behaviour and 1–2 tempting wrong ones.
2. Draw the graph (`templates/decision_graph.yaml`): 2–4 decision points, depth ≤ 3, ≤ 8 nodes; every path ends in an
   outcome node (`good`/`bad`/`neutral`). Prefer "recoverable" mistakes (bad choice → feedback → second chance).
3. Write scenes per node: setup scenes, one `decision` scene per decision node (last scene of the node), outcome scenes.
4. Feedback: say *why* (link to the red flag / rule), 1–2 sentences, never shaming. Put it in node `feedback`
   and voice it in the outcome scene.
5. Scores: good path max (e.g. 10), partial (2–5), bad 0. `pass_mark` lives in quiz.json (tcs-assessment adds a
   `scenario` item per decision, mapped to the objective).
6. Validate: every `choices[].next` is a node id; every node scene id exists; every node reachable from `start`;
   every non-outcome node ends with a `decision` scene.

## Rules / QA
- Choices are plausible, similar length, no joke options; ≤ 4 choices, labels ≤ 10 words.
- Exactly one best choice per decision (`correct: true`); others `false`.
- Bad outcomes realistic, not catastrophic for laughs; always show the recovery action (report, call IT).
- Accessibility: choices keyboard-selectable in HTML/SCORM; video version announces choices in narration.
- Arabic: choice labels and feedback translated; branches mirror nothing (graph is logical).

## Blends
- **branching + cartoon** (default), **branching + comic** (static pages), **branching + doodle**.
- **explainer + branching**: teach first, one scenario at the end (formats `["explainer","branching"]`).
- **branching + quiz**: tcs-assessment turns each decision into a `scenario` item for SCORM scoring.
- **series + branching**: weekly "what would you do?" nudge with one decision.

## References
- `references/playbook.md`, `templates/decision_graph.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Branching scenario playbook

## When to use
- Judgement under pressure: verify-or-comply calls, payment-change requests, data-sharing dilemmas, manager conversations.
- Objectives at Bloom apply/analyze/evaluate; audiences who "know the rule" but fail in the moment.
- Avoid for pure knowledge (quiz) or exact UI procedure (screencast-sim).

## Duration / size
| Variant | Decisions | Nodes | Path length |
|---|---|---|---|
| Micro scenario | 1 | 3 | 45–90 s |
| Standard | 2–3 | 5–8 | 2–4 min per path |
| Rich | 3–4 | 8–12 | 4–8 min (split by chapter) |

## Graph patterns
| Pattern | Shape | Use |
|---|---|---|
| Gauntlet | linear spine; wrong choices → short bad outcome → retry | beginners, compliance |
| Funnel | choices diverge, rejoin at next decision | standard; keeps production small |
| Tree | full divergence | rich scenarios only (expensive) |
Default: **funnel with recoverable mistakes**.

## Beat structure (standard funnel)
| # | Node | Scenes | Template |
|---|---|---|---|
| 1 | `n_intro` | setup (15–25 s) + decision 1 | `cartoon`/mock-up + `decision` |
| 2 | wrong-1 | consequence (8–15 s) | `statement`/`cartoon`, outcome `bad`, feedback |
| 3 | right-1 | escalation (10–20 s) + decision 2 | `cartoon` + `decision` |
| 4 | wrong-2 | partial consequence | outcome `bad`, score 2 |
| 5 | right-2 | resolution + rule | `cartoon` + `steps`, outcome `good`, score 10 |
| 6 | debrief | recap of the red flags | `checklist` (shared by all endings, optional) |

## Writing choices
- All choices start with a verb; similar length; one best, one tempting, optionally one "half-right".
- The tempting choice mirrors the attacker's lever (urgency, authority, kindness).
- Feedback formula: *what happened* + *the red flag you missed* + *what to do instead*.

## Do / Don't
| Do | Don't |
|---|---|
| Recoverable mistakes | Dead ends with no learning |
| Same consequences length for every branch | Long bad branches (rewarding failure with content) |
| Score + feedback per node | Silent outcomes |
| Narrate the choices in the linear video | Rely on clickable UI in video |

## Worked example (`templates/example.storyboard.json`)
"The Urgent Reset Call" (help-desk SE, formats `branching`+`cartoon`): `n_intro` (call + decision) →
`n_reset` (bad, 0) | `n_verify` (callback, second decision) → `n_cave` (bad, 2) | `n_good` (good, 10).

### template: decision_graph.yaml
```yaml
# Decision graph → storyboard.json `branching` (+ one `decision` scene per decision node)
start: n_intro
nodes:
  - id: n_intro
    scenes: [b01_call, b02_choice1]      # last scene of a decision node is a `decision` scene
    outcome: continue
  - id: n_reset                          # wrong choice at decision 1
    scenes: [b03_reset]
    outcome: bad
    score: 0
    feedback: "You reset an account on an unverified call. Verify via a known number first."
  - id: n_verify                         # right choice at decision 1
    scenes: [b04_verify, b05_choice2]
    outcome: continue
    score: 5
  - id: n_cave
    scenes: [b06_cave]
    outcome: bad
    score: 2
    feedback: "Pressure is the attack. Escalate instead of making exceptions."
  - id: n_good
    scenes: [b07_good]
    outcome: good
    score: 10
    feedback: "Verified and escalated. Attack stopped."
# decision scene props (b02_choice1):
#   prompt: "What do you do?"
#   choices:
#     - {id: a, label: "Reset it now. It's the CFO.", next: n_reset, correct: false}
#     - {id: b, label: "Call back on the directory number", next: n_verify, correct: true}
# Checks: every next ∈ node ids · every scene id exists · all nodes reachable · every path ends good|bad|neutral.
```

### template: script_template.md
```markdown
# Branching script — <lesson_id> · <title>

Dilemma: <one line> · Ideal behaviour: <rule + source id> · Skin: cartoon | comic | doodle | explainer

| node | scene id | template | lines (who: text, `^` cues) | choices (id → next, correct) | outcome / score | feedback (what happened + red flag + do instead) |
|---|---|---|---|---|---|---|
| n_intro | b01_setup | cartoon | narrator: …; caller: ^ … | | continue | |
| n_intro | b02_choice1 | decision | narrator: What do you do? | a → n_bad1 ✗ · b → n_mid ✓ | | |
| n_bad1 | b03_bad1 | statement | mentor: ^ … | | bad / 0 | |
| n_mid | b04_mid | cartoon | … | | continue / 5 | |
| n_mid | b05_choice2 | decision | … | a → n_bad2 ✗ · b → n_good ✓ | | |
| n_bad2 | b06_bad2 | statement | | | bad / 2 | |
| n_good | b07_good | cartoon | | | good / 10 | |
```


# FORMAT: screencast-sim


# tcs-format-screencast-sim

## Purpose
Teach a software procedure with the watch → try → do pattern, without recording real screens (screens are drawn by
the kit from `screencast.app` fields, or from a supplied, scrubbed screenshot).

## Inputs
- Approved lesson (`curriculum.yaml`) — procedure objectives (`type: procedure`).
- Procedure facts with `procedure_order` from `sources.yaml` (SOPs, user guides, recorded demos ingested by tcs-source-ingest).
- Optional screenshots (must be scrubbed of real personal data; record license/owner in `assets[]`).

## Outputs
- `screencast` scenes: `{app{kind: form|table|list|settings|dashboard|screenshot, title, screenshot?, fields[]{id,label,value?,kind}}, actions[]{cue, do: move|click|type|select|highlight|callout|toast|zoom, target (field id), value?, label?}}`.
- **Step script** = ordered `actions[]` (one `^` per action) — the "watch" demo.
- **Interactive sim spec** = optional `props.sim` (extension, allowed by `additionalProperties`):
  `{mode: demo|guided|practice|assess, task, expect[]{target, value? ("*" = any)}, hints{target: text}, max_attempts, on_fail: replay_demo|show_hint|continue}`.
  Video targets render `guided`/`practice` as an overlay walkthrough; lesson/SCORM targets make it clickable.
- Supporting: `title`, `steps` (overview), `checklist`, `quiz`, `outro`; mock-ups (`browser_mock`, `popup`) where useful.
- Fill-ins `templates/sim_spec.yaml`, `templates/script_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Extract the procedure (ordered facts). Group into tasks of ≤ 7 steps; one task per screencast scene.
2. Define the screen: fields with stable ids (`date`, `amount`, `submit`), labels exactly as in the real UI (or neutral
   if the UI is not to be shown), fictional values only.
3. Demo scene (`sim.mode: demo`): one action per `^`; narrate the *why* for non-obvious steps.
4. Practice scene (`guided` then `practice`): task statement, `expect[]` in order, hints for common errors, attempts.
5. Optional `assess` scene (no hints) mapped to a quiz item (tcs-assessment adds a `scenario`/`ordering` item).
6. Overview `steps` before, `checklist` after; claims per scene (procedure facts); validate.

## Rules / QA
- Never show real personal data, real customer names, real URLs of internal systems, or real brand logos.
- Pointer actions ≥ 1.0 s apart; `zoom` on fields < 24 px; callouts ≤ 6 words.
- Field labels on screen are template text → translated for Arabic; RTL forms mirror (labels right).
- Keyboard path documented for accessibility (Tab order = `fields[]` order) for interactive targets.
- If the real UI changes often, prefer `kind` generic screens + labels over screenshots.

## Blends
- **screencast-sim + job-aid** (strongly recommended): the step script becomes a quick-reference card.
- **narrated-deck + screencast-sim**: policy in slides, practice in sim.
- **screencast-sim + series**: one task per nudge ("60-second how-to").
- **screencast-sim + branching**: error-handling decisions (e.g. "the system rejects your claim — what next?").

## References
- `references/playbook.md`, `templates/sim_spec.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.

# Screencast + simulation playbook

## When to use
- "How do I do X in system Y": portals, forms, settings, reporting a phishing email, enabling MFA, filing a claim.
- Learners must perform, not just recognise. Pairs naturally with a job-aid.
- Avoid for judgement calls (branching) or concepts (explainer).

## Duration
| Variant | Tasks | Length |
|---|---|---|
| Micro how-to | 1 task, ≤ 5 steps | 45–90 s |
| Standard | 2–3 tasks | 3–6 min incl. practice |
| System course | 4–8 tasks | split into lessons (one task each) |

## Beat structure (watch → try → do)
| # | Beat | Time | Template / sim.mode |
|---|---|---|---|
| 1 | Title + goal | 5 s | `title` |
| 2 | Overview of steps | 10–15 s | `steps` |
| 3 | Watch (demo) | 15–40 s | `screencast` · `demo` |
| 4 | Try (guided) | 20–60 s | `screencast` · `guided` (highlights + hints) |
| 5 | Do (practice) | 20–60 s | `screencast` · `practice` (no highlights, hints on error) |
| 6 | Errors to avoid | 10–15 s | `popup` / `do_dont` |
| 7 | Check | 10–15 s | `quiz` or `screencast` · `assess` |
| 8 | Recap | 8–12 s | `checklist` |

## Action vocabulary
| do | Effect | Narration cue |
|---|---|---|
| `move` | pointer glides to target | "go to…" |
| `click` | pointer + ripple | "click…" |
| `type` | text types into field (`value`) | "type…" |
| `select` | dropdown opens, `value` picked | "choose…" |
| `highlight` | field glows | "notice…" |
| `callout` | label + arrow to field | "don't forget…" |
| `toast` | system message (`label`) | "you'll see…" |
| `zoom` | camera eases to field | small UI |

## Sim spec modes
| mode | Interactive targets | Video targets |
|---|---|---|
| demo | autoplay | autoplay |
| guided | learner clicks highlighted target | overlay shows pointer doing it |
| practice | learner does task; hints on wrong input | narrated walkthrough |
| assess | scored, no hints | skipped or shown as answer replay |

## Do / Don't
| Do | Don't |
|---|---|
| Fictional data ("23.50 taxi") | Real names, emails, IDs |
| One task per scene | 15-step marathons |
| Explain *why* on tricky steps | Narrate every pixel |
| Pair with a job-aid | Expect recall of long procedures from video alone |

## Worked example (`templates/example.storyboard.json`)
"File an Expense Claim" (fictional Northwind Expenses): demo with 6 actions (date → category → amount → receipt →
submit → toast); practice with `expect` [Taxi, 23.50, receipt, submit], hint on receipt, 3 attempts; recap checklist.

### template: script_template.md
```markdown
# Screencast step script — <lesson_id> · task: <task>

System: <fictional or generic name> · Screen kind: form | table | list | settings | dashboard | screenshot

| step | cue | do | target (field id) | value / label | narration (`^` before the verb) | why (only if non-obvious) | source |
|---|---|---|---|---|---|---|---|
| 1 | 0 | click | date | | ^ Pick the date. | | S08#c1 |
| 2 | 1 | select | cat | Taxi | ^ Choose the category. | | |
| 3 | 2 | type | amount | 23.50 | ^ Type the amount. | | |
| 4 | 3 | click | receipt | Attach the photo | ^ Attach the receipt. | mandatory → hint | S01#p3 |
| 5 | 4 | click | submit | | ^ Press submit… | | |
| 6 | 5 | toast | | Claim sent to your manager | ^ …and it goes to your manager. | | |

Practice: task "<…>" · expect [<target=value>…] · hints {…} · max_attempts 3 · on_fail replay_demo
```

### template: sim_spec.yaml
```yaml
# Interactive sim spec → `scenes[].props.sim` of a `screencast` scene (extension prop; renderers that do not
# support interactivity play it as a narrated overlay). Screen = props.app; step script = props.actions[].
app:
  kind: form                      # form | table | list | settings | dashboard | screenshot
  title: "Northwind Expenses · New claim"
  fields:                         # stable ids; Tab order = list order
    - {id: date,    label: "Date",     kind: date}
    - {id: cat,     label: "Category", kind: select}
    - {id: amount,  label: "Amount",   kind: amount}
    - {id: receipt, label: "Receipt",  kind: file}
    - {id: submit,  label: "Submit",   kind: button}
sim:
  mode: practice                  # demo | guided | practice | assess
  task: "File a 23.50 taxi claim for today"
  expect:                         # in order; value "*" = any non-empty input
    - {target: cat, value: "Taxi"}
    - {target: amount, value: "23.50"}
    - {target: receipt, value: "*"}
    - {target: submit}
  hints:
    receipt: "Itemised receipts are mandatory."
  max_attempts: 3
  on_fail: replay_demo            # replay_demo | show_hint | continue
  quiz_item: Q5                   # optional: scored in quiz.json when mode = assess
```


# FORMAT: job-aid


# tcs-format-job-aid

## Purpose
Give learners the thing they use *at the moment of need*: short, scannable, actionable. It summarises; it does not teach.
Usually derived from a sibling lesson (same objectives) — formats `["<main>", "job-aid"]` on the main storyboard, or a
separate `<lesson_id>-jobaid.storyboard.json` with `formats: ["job-aid"]` and target `jobaid`.

## Inputs
- Approved lesson (`curriculum.yaml`, objectives of type procedure/behavior/policy) and its storyboard if it exists
  (reuse its `do_dont`, `steps`, `checklist`, `table` props verbatim for consistency).
- Facts (`sources.yaml`) — contacts, thresholds, steps; domain `glossary.yaml` for terms.

## Outputs
- Page sections as scenes (order = top-to-bottom on the page): `title` (header), `checklist`, `do_dont`, `steps`
  (`danger: true` for "if it goes wrong"), `table` (contacts/limits), `definition` (key term), `icon_grid` (signs),
  `statement` (golden rule), optional `flashcard` deck for the series/nudge pairing.
- `narration` may be `[]` (static page) or 30–60 s walkthrough lines if a video version is wanted.
- `scenes[].notes` for placeholders the client must fill (phone numbers, URLs).
- Fill-ins `templates/onepager_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Decide the job-aid type: **checklist** (do in order / verify), **cheat sheet** (lookup), **decision card**
   (if-then), **one-pager** (mix, max 5 sections).
2. Pull content from the lesson; cut every word that isn't an action, a sign, a threshold or a contact.
3. Lay out ≤ 5 sections for A4/Letter portrait (≤ 3 for a desk card / 1:1 social tile; 9:16 for a phone wallpaper).
4. Mark client-specific placeholders in `notes` (fictional values in examples; never invent real contacts).
5. Claims per section; validate. Renderer: target `jobaid` → PDF/HTML/PNG (aspect ignored for A4; used for tiles).

## Rules / QA
- ≤ 7 items per checklist, ≤ 8 words per item, verbs first; ≥ 11 pt print / ≥ 24 px screen; contrast ≥ 4.5:1.
- One page. If it doesn't fit, make two job aids, not a smaller font.
- No generated imagery with text; icons from the kit only; logo slot empty unless supplied.
- Arabic: separate RTL page (not side-by-side) unless the brief asks for a bilingual card; digits consistent.
- Accessible PDF/HTML: real text (not images of text), heading order, alt text on icons that carry meaning.

## Blends (pairs with any format)
- **explainer + job-aid**: reuse `do_dont` + recap `checklist`.
- **screencast-sim + job-aid**: step script → numbered `steps` card.
- **cartoon/comic + job-aid**: mentor's rule → golden-rule `statement` + checklist.
- **branching + job-aid**: decision card of the red flags behind each choice.
- **series + job-aid**: one card per episode; nudges link to it.

## References
- `references/playbook.md`, `templates/onepager_template.md`, `templates/example.storyboard.json`.

# Job-aid playbook

## When to use
- Infrequent or high-stakes tasks (report an incident, approve a payment change), long checklists, lookup data.
- After any lesson as the takeaway. Not a substitute for teaching new skills.

## Types and sizes
| Type | Sections | Size | Best for |
|---|---|---|---|
| Checklist | 1–2 | half page / desk card | verify before acting |
| Cheat sheet | 3–5 | A4/Letter | lookups, shortcuts, terms |
| Decision card | 2–3 | desk card / 1:1 | if-then rules |
| One-pager | 4–5 | A4/Letter | mixed takeaway after a lesson |
| Poster | 2–3 | A3 / 9:16 screen | awareness at the point of risk |
Optional narrated walkthrough: 30–60 s.

## Section order (one-pager)
| # | Section | Template |
|---|---|---|
| 1 | Header: what this card is for | `title` (kicker "Job aid") |
| 2 | Spot it / before you start | `checklist` or `icon_grid` |
| 3 | Do / don't | `do_dont` |
| 4 | If it goes wrong | `steps` (`danger: true`) |
| 5 | Who to contact / limits | `table` |

## Writing rules
- Verb-first, ≤ 8 words: "Check the sender's domain".
- Numbers and contacts exact and sourced; placeholders flagged in `notes`.
- Same wording as the lesson (learners recognise it).
- One golden rule max (`statement`).

## Do / Don't
| Do | Don't |
|---|---|
| One page, white space | Shrink fonts to fit |
| Icons that aid scanning | Decorative clip-art |
| Real text in PDF/HTML | Exported image of text |
| Version + date in footer (renderer) | Undated cards that go stale |

## Worked example (`templates/example.storyboard.json`)
"Phishing Red-Flag Card": header → 6 red flags (`checklist`) → `do_dont` → "Clicked already?" `steps` (danger) →
contacts `table` (fictional extension flagged in `notes`). No narration.

### template: onepager_template.md
```markdown
# Job aid — <title> (pairs with <lesson_id>)

Type: checklist | cheat sheet | decision card | one-pager | poster · Size: A4 | Letter | desk card | 1:1 | 9:16
Language: <one per page> · Version/date: <filled by renderer>

| order | scene id | section | template | content (≤ 8 words per item, verb-first) | claims | placeholders for client (`notes`) |
|---|---|---|---|---|---|---|
| 1 | j01_header | header | title | kicker "Job aid", title, icon | GK | |
| 2 | j02_spot | spot it | checklist | ≤ 7 items | S## | |
| 3 | j03_dodont | do / don't | do_dont | dont[], do[] | S## | |
| 4 | j04_wrong | if it goes wrong | steps (danger) | ≤ 5 steps | S## | |
| 5 | j05_contacts | contacts / limits | table | columns, rows ≤ 5 | S## | phone, email, URL |
```


# FORMAT: series


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

# Series + gamification + nudges playbook

## When to use
- Annual/ongoing programmes (security awareness, compliance refreshers, onboarding over weeks).
- Behaviour change that decays without reinforcement; audiences with low attention budgets.
- Avoid for one-off must-complete-today content (single lesson) or long certification courses (narrated-deck + SCORM).

## Season sizes
| Variant | Episodes | Episode length | Nudges | Cadence |
|---|---|---|---|---|
| Sprint | 4 | 2–3 min | 2 per episode | weekly |
| Season | 6–8 | 2–4 min | 2 per episode | weekly / fortnightly |
| Always-on | 12 | 2–3 min | 1–2 per episode | monthly |
Nudges: 30–60 s, 9:16, one behaviour.

## Episode beat structure (any base format)
| # | Beat | Time |
|---|---|---|
| 1 | Cold open with the recurring cast | 10–20 s |
| 2 | Lesson body (base format playbook) | 1.5–3 min |
| 3 | Quick check (points) | 10–15 s |
| 4 | Recap + teaser for next episode | 10–15 s |

## Nudge beat structure (30–60 s)
| # | Beat | Time | Template |
|---|---|---|---|
| 1 | Hook: the risky moment | 8–15 s | `chat_mock` / `email_mock` / `mfa_prompt` / `cartoon` |
| 2 | The move | 6–12 s | `flashcard` (front = situation, back = action) |
| 3 | Retrieval | 8–12 s | `quiz` (2–3 options) |
| 4 | Reward + next | 4–6 s | `outro` ("Streak +1 · Episode 4 Monday") |

## Gamification defaults
| Element | Default |
|---|---|
| Points | episode 50 · correct quiz answer 10 · nudge watched 5 · reported simulated phish 25 |
| Streak | consecutive weeks with ≥ 1 activity; freeze 1 week per season |
| Badges | 3–5, behaviour-based (e.g. "Verifier", "Reporter", "Streak 4") |
| Leaderboard | opt-in, team-level, top 5 shown, no bottom ranks |
| Certificate | season completion ≥ 80% quiz average (evidence record) |

## Spacing schedule
Episode on day 0 → nudge A day +2 (retrieval) → nudge B day +7 (scenario/decision) → season recap quiz at the end.
Shift to working days per locale (Egypt: Sun–Thu; most of Europe/US: Mon–Fri).

## Do / Don't
| Do | Don't |
|---|---|
| Same cast, same world | New characters each week |
| One behaviour per nudge | Mini-lectures as nudges |
| Reward learning actions | Public shaming / bottom ranks |
| Captions on (silent autoplay) | Audio-only messages |

## Worked example
`templates/example.storyboard.json` — nudge E03N1 "Smishing in 45 seconds": `chat_mock` parcel-fee lure with callout →
`flashcard` → `quiz` (+10 points) → `outro` streak line. Plan + calendar examples in `templates/`.

### template: nudge_calendar.yaml
```yaml
# Nudge calendar — validate with series_plan.schema.json ($defs.calendar). Dates = working days for the locale.
schema_version: "1.0"
series_id: northwind-security-season-1
timezone: "Africa/Cairo"
working_days: [sun, mon, tue, wed, thu]   # Egypt; use [mon, tue, wed, thu, fri] for most EU/US clients
blackout_dates: []                        # client-provided public holidays
sends:
  - {date: "2027-01-10", time: "10:00", type: episode, ref: 1,     channel: lms,   asset: renders/M1L1.mp4,      text: "Episode 1 is live: spot a phishing email in 3 minutes."}
  - {date: "2027-01-12", time: "10:00", type: nudge,   ref: E01N1, channel: teams, asset: renders/E01N1.mp4,     text: "45 seconds: one red flag you can check today."}
  - {date: "2027-01-17", time: "10:00", type: episode, ref: 2,     channel: lms,   asset: renders/M1L2.mp4,      text: "Episode 2: the login page that wasn't."}
  - {date: "2027-01-17", time: "10:05", type: nudge,   ref: E01N2, channel: email, asset: renders/E01N2.mp4,     text: "What would you do? One question, 10 points."}
  - {date: "2027-01-26", time: "10:00", type: nudge,   ref: E03N1, channel: sms,   asset: renders/E03N1.mp4,     text: "Parcel fee text? Watch this first (45 s)."}
  - {date: "2027-02-07", time: "10:00", type: recap,   ref: season, channel: lms,  asset: M9L1.quiz.json,        text: "Season recap quiz — keep your streak."}
```

### template: nudge_script_template.md
```markdown
# Nudge script — <nudge id> (episode <n>) · 30–60 s · 9:16 · captions burned in

Behaviour: <one action> · Objective: <O#> · Quiz/flashcard item: <Q#> · Points: +<n>

| # | scene id | beat | template | narration (`^` cues) | props (on-screen text, ≤ 10 words per line) | claims | ~s |
|---|---|---|---|---|---|---|---|
| 1 | n01_hook | risky moment | chat_mock / email_mock / mfa_prompt / cartoon | ^ … ^ … | messages/callouts | S## | 12 |
| 2 | n02_card | the move | flashcard | ^ Flip it: … | front, back, icon | S## | 10 |
| 3 | n03_quiz | retrieval | quiz | Q (pause 2.0) / ^ A + points | q, options (2–3), answer | S## | 10 |
| 4 | n04_outro | reward + next | outro | Streak plus one… | line | GK | 5 |

Calendar row: date (working day) · channel · asset · text (+ text_ar)
```

### template: series_plan.schema.json
```json
{
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "$id": "https://tamer-skills/training-content-studio/skills/tcs-format-series/series_plan.schema.json",
 "title": "series_plan.yaml / nudge_calendar.yaml (local to tcs-format-series; proposed for schemas/)",
 "oneOf": [{"$ref": "#/$defs/plan"}, {"$ref": "#/$defs/calendar"}],
 "$defs": {
  "lang": {"enum": ["en-US", "en-GB", "ar-EG", "ar-MSA"]},
  "plan": {
   "type": "object",
   "required": ["schema_version", "series_id", "course_id", "title", "cadence", "episodes", "nudges", "gamification"],
   "properties": {
    "schema_version": {"const": "1.0"},
    "series_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "course_id": {"type": "string"},
    "title": {"type": "string"},
    "languages": {"type": "array", "items": {"$ref": "#/$defs/lang"}},
    "cadence": {"enum": ["weekly", "fortnightly", "monthly"]},
    "start_date": {"type": "string", "format": "date"},
    "recurring_cast": {"type": "array", "items": {"type": "string"}},
    "setting": {"type": "string"},
    "episodes": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["n", "lesson_id", "title", "base_format"],
     "properties": {"n": {"type": "integer", "minimum": 1}, "lesson_id": {"type": "string"}, "title": {"type": "string"},
      "base_format": {"enum": ["explainer", "doodle", "cartoon", "comic", "narrated-deck", "mindmap", "branching", "screencast-sim", "job-aid"]},
      "minutes": {"type": "number", "minimum": 0.5, "maximum": 10}, "teaser": {"type": "string"}}}},
    "nudges": {"type": "array", "items": {"type": "object", "required": ["id", "episode", "day_offset", "kind"],
     "properties": {"id": {"type": "string"}, "episode": {"type": "integer"}, "day_offset": {"type": "integer", "minimum": 0, "maximum": 30},
      "kind": {"enum": ["flashcard", "quiz", "decision", "tip", "replay"]}, "storyboard": {"type": "string"}}}},
    "flashcard_decks": {"type": "array", "items": {"type": "object", "required": ["episode", "quiz_file", "item_ids"],
     "properties": {"episode": {"type": "integer"}, "quiz_file": {"type": "string"}, "item_ids": {"type": "array", "items": {"type": "string"}}}}},
    "gamification": {"type": "object", "required": ["points"], "properties": {
     "points": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
     "streak": {"type": "object", "properties": {"unit": {"enum": ["day", "week"]}, "min_activities": {"type": "integer"}, "freezes_per_season": {"type": "integer"}}},
     "badges": {"type": "array", "items": {"type": "object", "required": ["id", "label", "rule"], "properties": {"id": {"type": "string"}, "label": {"type": "string"}, "rule": {"type": "string"}}}},
     "leaderboard": {"type": "object", "properties": {"enabled": {"type": "boolean"}, "scope": {"enum": ["team", "individual", "department"]}, "opt_in": {"type": "boolean"}, "show_top": {"type": "integer"}}},
     "completion": {"type": "object", "properties": {"quiz_average_min": {"type": "number"}, "certificate": {"type": "boolean"}}}}},
    "evidence": {"type": "object"}
   }
  },
  "calendar": {
   "type": "object",
   "required": ["schema_version", "series_id", "timezone", "sends"],
   "properties": {
    "schema_version": {"const": "1.0"},
    "series_id": {"type": "string"},
    "timezone": {"type": "string"},
    "working_days": {"type": "array", "items": {"enum": ["sat", "sun", "mon", "tue", "wed", "thu", "fri"]}},
    "blackout_dates": {"type": "array", "items": {"type": "string"}},
    "sends": {"type": "array", "items": {"type": "object", "required": ["date", "type", "ref", "channel"],
     "properties": {"date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}, "time": {"type": "string", "pattern": "^\\d{2}:\\d{2}$"},
      "type": {"enum": ["episode", "nudge", "recap", "reminder"]}, "ref": {"type": ["string", "integer"]},
      "channel": {"enum": ["lms", "email", "teams", "slack", "sms", "intranet", "whatsapp"]},
      "asset": {"type": "string"}, "text": {"type": "string"}, "text_ar": {"type": "string"}}}}
   }
  }
 }
}
```

### template: series_plan.yaml
```yaml
# Series plan — validate: .venv/bin/python -c "import yaml,json,jsonschema;jsonschema.validate(yaml.safe_load(open('series_plan.yaml')),json.load(open('skills/tcs-format-series/templates/series_plan.schema.json')))"
schema_version: "1.0"
series_id: northwind-security-season-1
course_id: northwind-security-series
title: "Northwind Security Season 1"
languages: [en-US, ar-EG]
cadence: weekly                  # weekly | fortnightly | monthly
start_date: "2027-01-10"
recurring_cast: [rookie, mentor, vex]
setting: "Northwind Co. open office"
episodes:
  - {n: 1, lesson_id: M1L1, title: "Spot a Phishing Email", base_format: explainer, minutes: 3, teaser: "Next: a text that isn't from your courier."}
  - {n: 2, lesson_id: M1L2, title: "Fake Login Pages",     base_format: cartoon,   minutes: 3}
  - {n: 3, lesson_id: M1L3, title: "Smishing",             base_format: cartoon,   minutes: 2.5}
  - {n: 4, lesson_id: M2L1, title: "MFA Fatigue",          base_format: cartoon,   minutes: 3}
nudges:
  - {id: E01N1, episode: 1, day_offset: 2, kind: flashcard, storyboard: E01N1.storyboard.json}
  - {id: E01N2, episode: 1, day_offset: 7, kind: decision,  storyboard: E01N2.storyboard.json}
  - {id: E03N1, episode: 3, day_offset: 2, kind: flashcard, storyboard: E03N1.storyboard.json}
flashcard_decks:
  - {episode: 1, quiz_file: M1L1.quiz.json, item_ids: [QF1, QF2, QF3, QF4, QF5]}
gamification:
  points: {episode_complete: 50, quiz_correct: 10, nudge_watched: 5, reported_simulation: 25}
  streak: {unit: week, min_activities: 1, freezes_per_season: 1}
  badges:
    - {id: verifier, label: "Verifier", rule: "Correct on 3 verify-first questions"}
    - {id: reporter, label: "Reporter", rule: "Reported a simulated phishing email"}
    - {id: streak4,  label: "Four in a row", rule: "4-week streak"}
  leaderboard: {enabled: true, scope: team, opt_in: true, show_top: 5}
  completion: {quiz_average_min: 80, certificate: true}
evidence:                         # feeds compliance records (see domain compliance.yaml)
  record: [completion, score, date, content_version, language]
```
