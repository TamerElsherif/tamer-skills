# Quality checklist

Run before marking a lesson `qa-pass` (curriculum `status`) and before any delivery. **Auto** = script/skill checks it;
**Review** = a human or the agent inspects QA stills/frames. A lesson ships only when every *blocking* item passes or a
waiver is recorded in `decisions.json` (`key: other`, `flagged: true`).

| # | Item | Pass criteria | How it is checked | Blocking |
|---|---|---|---|---|
| 1 | Schema-valid | storyboard/quiz/curriculum/sources validate (Draft 2020-12); YAML after `yaml.safe_load` | jsonschema with `schemas/*.schema.json` — `tcs-storyboard`, `tcs-assessment`, `tcs-curriculum` validators; `portable/build_portable.py --check` for examples/packs | yes |
| 2 | Grounded | every scene claim has `source_ids` that resolve in `sources.yaml`, or `general_knowledge: true`; 0 `unsupported`, 0 `conflicting`; `outdated` reviewed | `tcs-grounding-check` → `grounding_report.json` summary | yes |
| 3 | General knowledge honest | GK only for widely accepted facts; no numbers, thresholds, contacts or policy rules as GK | `tcs-grounding-check` flags GK claims containing digits/policy verbs; Review | yes |
| 4 | Objective-aligned | every lesson objective covered by ≥ 1 scene (`scenes[].objective_ids` / report `coverage`) **and** assessed by ≥ 1 quiz item (`quiz.items[].objective_id`) | `tcs-grounding-check` coverage map + `tcs-assessment` objective map | yes |
| 5 | Audience-appropriate | reading level and jargon fit `audience.level`; glossary terms used consistently; exec lessons ≤ planned length | `tcs-scriptwriter` self-check vs domain `glossary.yaml`; Review | no |
| 6 | Duration | rendered/estimated length within ±15% of `duration_min`; when remaking an existing video ≥ 90% of the original (aim 100–120%) and every original point covered | estimate = words ÷ `wpm`; final via ffprobe in `tcs-render-lesson`; coverage checklist from `tcs-source-ingest` transcript | yes |
| 7 | Narration integrity | no truncated TTS (per-line WPM outlier > ±35% of median → retry); cue times from word timestamps | `tcs-render-*` TTS step | yes |
| 8 | Cue sync | max `cue` in props + 1 ≤ number of `^` in the scene; nothing revealed long before it is said | storyboard lint (`tcs-storyboard`); QA stills just after cues | yes |
| 9 | Captions | captions on for every video; ≤ 2 lines, ≤ 42/38 chars per line (Latin/Arabic), ≤ 17/15 cps, sidecar VTT per language | `assets/caption_styles.yaml` rules in `tcs-render-*`; Review | yes |
| 10 | Contrast | text ≥ 4.5:1 (large ≥ 3:1); attention orange never used as small text or under white text | `.venv/bin/python assets/scripts/check_contrast.py [storyboard]` | yes |
| 11 | Text size & density | ≥ 24 px at 1080p (9:16: ≥ 32 px), ≤ 6 bullets per board, ≤ 7 checklist items, no overflow/overlap | schema `maxItems`; QA stills/frame grid in `tcs-render-*` | yes |
| 12 | Alt text & on-screen text | `on_screen_text` derived for every scene; images/icons that carry meaning have alt text in HTML/SCORM/PDF | `tcs-render-lesson` (HTML/SCORM), Review | yes (HTML/SCORM) |
| 13 | Keyboard & interactivity | branching choices, sims and quizzes operable by keyboard; focus visible; no time limits without control | `tcs-render-lesson` HTML/SCORM checks; Review with Tab-through | yes (interactive) |
| 14 | Arabic renders correctly | `direction: rtl`; Arabic font from theme (IBM Plex Sans Arabic / Cairo / Noto Kufi Arabic); no tofu/disconnected letters; bidi isolates around Latin runs/URLs; digits consistent (Western or Arabic-Indic per brief); mirrored layouts; SVG illustration text kept LTR | `tcs-localize` checks + Arabic QA stills; native-speaker Review for Egyptian colloquial | yes (AR) |
| 15 | No text in generated imagery | every `generated_images[].prompt` ends with "no text, no letters, no numbers, no signage, no logos"; outputs inspected | storyboard lint; Review of generated images | yes |
| 16 | No real people/brands | no real people, likenesses, logos or brand names in mock-ups/B-roll without written permission; fictional Northwind Co., `.example` domains | Review of mock-ups + B-roll contact sheet | yes |
| 17 | Asset licences recorded | every shipped non-placeholder asset has `license` in `storyboard.assets[]` / `assets_licenses.yaml`; no `placeholder` assets in a final | `tcs-render-*` asset report; `assets/MANIFEST.md` fields | yes |
| 18 | Look & feel | no one-sided thick accent borders on cards; no generic "AI look" (glow gradients everywhere, random 3D blobs, emoji icons); neutral theme or client preset; never cream/terracotta; logo slot empty unless supplied | Review of QA stills / frame grid; theme preset check | yes |
| 19 | B-roll quality | no visible logos, readable screens, text overlays, hoodie-hacker/matrix clichés; clips loop/slow (≥ 0.6×) rather than freeze | contact sheet Review in explainer flow | yes (explainer) |
| 20 | Technical | Remotion composition ids only `[a-zA-Z0-9-]`; audio present; loudness ≈ −16 LUFS; no black/blank frames (fades can look blank in frame grids — check mid-scene) | `tcs-render-remotion` / `tcs-render-openmontage` | yes (video) |
| 21 | Compliance evidence | outro `evidence_line` when the course maps to a framework; SCORM reports status + score; records per domain `compliance.yaml` | `tcs-render-lesson` SCORM export; Review | if compliance requested |
| 22 | Versioned | storyboard/quiz version or commit recorded; tracker row updated | orchestrator state + tracker export | no |

## QA loop (video targets)
1. Build TTS + timeline → print scene timings.
2. Render QA stills mid-scene and just after cues → fix overlap/clipping/empty half-screens/arrows that miss targets.
3. Final render → extract 6–9 frames + ffprobe (duration, audio) → items 6, 9–11, 14, 18–20.
4. Parallel production: ≤ 5 agents at once (8 hit session limits in the worked example).

## Waivers
Record `{key: "other", value: "waive QA#<n>", signal: "<why>", confidence, source: "user", flagged: true}` in
`decisions.json`; repeat in `decisions.md`. Items 2, 15, 16 and 17 cannot be waived for external delivery.
