# Character sheet — `mentor` (Omar / عمر)

**Role:** Subject-matter expert (IT/security/HR/finance) who explains the rule and the why
**Kit cast id:** `mentor` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
man in his 30s, light-brown skin, short black hair, rectangular glasses, short beard, blue polo shirt, khaki trousers, lanyard badge, tablet in hand.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#B98563` |
| hair | `#1F1A17` |
| polo | `#006AB3` |
| bottom | `#C9B48A` |
| glasses | `#363E77` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Calm, friendly, slightly dry humour; explains in one line, then shows how.

## Voice
openai echo — calm, warm, clear (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `present`, `stop`, `point`, `pointUp` · expressions: `happy`, `neutral`, `think` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Turn the story into the lesson | Lecture for more than ~20 s |
| Use `stop` pose for the key rule | Mock the rookie |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.
