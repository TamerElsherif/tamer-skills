# Character sheet — `manager` (Karim / كريم)

**Role:** Line manager / approver; source of authority pressure (real or impersonated)
**Kit cast id:** `manager` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
man in his 40s, dark-brown skin, short greying hair, neatly trimmed grey-black beard, white shirt with rolled sleeves, navy waistcoat, grey trousers, wristwatch.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#6B4532` |
| hair | `#4A4A4A` |
| shirt | `#FFFFFF` |
| waistcoat | `#363E77` |
| bottom | `#5A6385` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Brisk, good-humoured, busy; decisive; supportive when people verify.

## Voice
openai onyx — brisk, good-humoured (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `handsHips`, `point`, `phone`, `armsOut` · expressions: `neutral`, `happy`, `worried` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Praise verification ('Thanks for checking with me') | Bully or shout |
| Appear as the impersonated authority in scams | Be the villain himself |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.
