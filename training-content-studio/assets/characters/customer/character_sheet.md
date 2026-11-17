# Character sheet — `customer` (Dana / دانة)

**Role:** Customer, supplier or external partner; requests and payments come from (or are faked as) her
**Kit cast id:** `customer` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
woman in her 50s, fair skin with freckles, short silver bob haircut, green blazer over a cream-white blouse, dark trousers, tote bag.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#F0CFB4` |
| hair | `#C8CCD4` |
| blazer | `#1E7F4F` |
| blouse | `#F7F7F2` |
| bottom | `#2E3446` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Polite and professional; becomes impatient when stakes rise (useful pressure without villainy).

## Voice
openai coral — polite, slightly impatient under pressure (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `phone`, `handsHips`, `hold`, `wave` · expressions: `neutral`, `worried`, `happy`, `angry` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Represent legitimate external contacts | Be portrayed as the attacker |
| Be the person whose identity is spoofed |  |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.
