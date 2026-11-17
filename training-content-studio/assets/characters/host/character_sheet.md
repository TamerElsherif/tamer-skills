# Character sheet — `host` (Lina / لينا)

**Role:** On-screen host / narrator who introduces and wraps up lessons
**Kit cast id:** `host` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
woman in her mid-30s, medium-brown skin, shoulder-length wavy dark-brown hair, small stud earrings, navy blazer over a light-cyan top, charcoal trousers, flat shoes.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#A86B4C` |
| hair | `#3B2A22` |
| top | `#6FC7DA` |
| jacket | `#363E77` |
| bottom | `#3A3F55` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Warm, upbeat, clear; speaks to the viewer directly; never preachy.

## Voice
openai marin (narrator slot) — warm, confident trainer (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `present`, `wave`, `point`, `pointUp` · expressions: `happy`, `neutral` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Address the camera | Act out mistakes (that is the rookie's job) |
| Bookend lessons (title, recap, outro) | Appear in the same scene as a character voiced by marin |
| Point at boards with `point`/`present` |  |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.
