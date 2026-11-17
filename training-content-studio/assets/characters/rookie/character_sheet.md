# Character sheet — `rookie` (Sam / سام)

**Role:** New starter / mistake-maker whose slips drive the story (then gets it right)
**Kit cast id:** `rookie` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
young man in his 20s, tan skin, curly black hair, light-blue shirt half-untucked, dark-grey chinos, white trainers, ID badge on a lanyard, often holding a coffee cup.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#C68B5E` |
| hair | `#141414` |
| shirt | `#A9D4F5` |
| bottom | `#4A4F5E` |
| cup | `#FFFFFF` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Good-natured, over-eager, easily rushed; big comic reactions; learns fast.

## Voice
openai ballad — expressive, quick to panic, comic (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `phone`, `facepalm`, `type`, `cheer`, `shrug` · expressions: `worried`, `shocked`, `happy`, `sad` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Make the relatable mistake, then redo it right | Be humiliated or punished harshly |
| Carry a running gag (coffee cup) | Stay wrong at the end of a lesson |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.
