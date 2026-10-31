# Spec, episode.json and config

## Mini-episode spec (`episodes/<name>.json`)

Paths are absolute or relative to the spec file. Times are **source seconds** in the full-episode master (no teaser).

```json
{
  "episode": "episode.json",
  "prefix": "Ep3 PLP",
  "title": "إطار الـ PLP من الأول للآخر - إزاي تخلّي المنتج Profit Engine",
  "out_dir": "<videos>/Episode 3/PLP Framework Episode",
  "punch_in": 1.12,
  "cards": "none",
  "burned_in": [[43, 49], [118, 123.5], [225.5, 233]],
  "cta": {"at": ["after_intro", "middle", "end"], "lang": "en"},
  "hook": [
    {"in": 445.50, "out": 450.50, "who": "Haitham", "first": "لأن أنا باعتبر إن الكودينج",
     "last": "ليابيليتي مش أسد", "what": "Cold open 1: coding is a liability"}
  ],
  "body": [
    {"sec": "why", "in": 40.35, "out": 241.45, "join": "cut", "who": "Tamer → Haitham → Hossam",
     "first": "كان فيه دايمًا اعتقاد", "last": "limitations بتاعتها", "what": "…"},
    {"sec": "why", "in": 250.45, "out": 270.73, "join": "jump", "…": "…"},
    {"sec": "map", "in": 1382.42, "out": 1405.68, "join": "swipe", "…": "…"}
  ],
  "brief": {
    "kicker": "رابط بودكاست · الحلقة الثالثة · حلقة الـ PLP",
    "headline_en": "Ep3 PLP: the Profit-Led Product framework, start to finish",
    "speakers": "Haitham Fouad, Hossam Ezzat, Tamer ElSherif (host)",
    "main_idea": "…", "audience": "…",
    "storyline": ["Cold open: …", "Why PLP: …"],
    "editing_notes": ["Kept on purpose: …"],
    "chapters": {"hook": "مقدمة", "why": "…", "map": "الأربع مراحل"},
    "broll": [["Why PLP", "Growth-at-all-costs vs profit-led chart; …"]],
    "description_ar": "…"
  }
}
```

| Key | Meaning |
|---|---|
| `prefix`, `title` | file name `<prefix> - <title> (src …) [mmMss].mp4`; title is the Arabic episode title |
| `out_dir` | where the video and brief go (else `episodes.out_dir` from config) |
| `hook` | cold-open montage, hard cuts, before the intro logo. 2–3 lines, each a complete micro-idea. `[]` = start on the intro |
| `body[].join` | how the piece meets the one before: `cut` (hard), `jump` (same conversation, skipped part), `swipe` (from elsewhere in the episode). The first body piece always follows the intro logo with a cut |
| `body[].sec` | section key: chapters (`brief.chapters`) start at each section's first piece |
| `who/first/last/what` | for the brief and for `check_edges.py` (expected first/last words) |
| `punch_in` | zoom on jump cuts with the same framing (default 1.12; `0` = off) |
| `cards` | `"auto"` (each speaker's first ≥ 6.8 s solo shot in the body), `"none"`, or `[{"who": "Tamer", "src": 512.0}]` |
| `burned_in` | source windows where the master already shows a name card (the CTA avoids them) |
| `cta` | `null` = no pop-up (only after the user said no; rule 1). `at`: any of `after_intro` (body start + `after_intro_delay`, default 20 s), `middle` (half the length), `end` (`end_lead` s before the outro, default 25), or output seconds. `lang`: `en` (SUBSCRIBE / SUBSCRIBED) or `ar` (اشترك / مشترك). `right_edge`: card's right edge in px on a 1920-wide frame (default: flush right); EP1 masters have a burned-in logo bottom-right, use 1650. Each pop-up takes the nearest free 6 s slot within ±90 s: no joint, name card, burned-in card or other pop-up within 1 s |
| `assets` | optional overrides of the config `episodes` keys for this spec |
| `intro`, `outro` | optional per-spec logo videos |

## `episode.json` (written by `prep_episode.py`)

`master`, `wav`, `words`, `proxy`, `shots` (paths), `split` (shot indexes that are split screens), `fps`, `width`,
`height`, `duration`, `teaser_offset` (seconds to add for the uploaded version with the teaser, used in the brief).
Ep 3 points at the older `hq/` files: `projects/rabet-ep3-reels/episodes/episode.json`.

`shots.json`: `[[start, end, who], …]`. `who` is a key of `episodes.name_cards` for solo shots, `split` for
multi-person frames, anything else (e.g. `Intro`, `?`) to ignore.

## `~/.rabet-reels.json` → `episodes`

```json
"episodes": {
  "intro": "<videos>/Assets/Intro - Outro/Intro-Logo-AE.mp4",
  "outro": "<videos>/Assets/Intro - Outro/Outro-Logo-AE-NEW.mp4",
  "name_cards": {"Tamer": ".../NameCard_tamer_IT-AI-Transformation-Expert.mov",
                 "Hossam": ".../NameCard_hossam.mov", "Haitham": ".../NameCard_haitham.mov"},
  "out_dir": "optional default output folder",
  "cta_dir": "~/.cache/rabet-episodes/cta",
  "channel": "رابط بودكاست",
  "handle": "@RabetPodcast"
}
```
Name cards are 3840×2160 ProRes 4444 with alpha (bottom-left lower third, ~6 s).
