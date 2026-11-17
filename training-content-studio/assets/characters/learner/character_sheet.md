# Character sheet — `learner` (Nour / نور)

**Role:** Everyday employee the audience identifies with; usually makes the right call after thinking
**Kit cast id:** `learner` (SVG persona in `kit/`, built by the render kit with this same id; reference images = kit renders).

## Look
young woman in her 20s, light-olive skin, wears a smooth blue hijab, soft grey cardigan over a white top, dark-blue trousers, white trainers, ID badge on a lanyard.
Flat vector, rounded shapes, uniform outline; never photoreal; not modelled on any real person.

| Part | Colour |
|---|---|
| skin | `#D9A982` |
| hijab | `#006AB3` |
| cardigan | `#9AA3B5` |
| top | `#FFFFFF` |
| bottom | `#26305C` |

Attention orange `#FF6700` is reserved for the antagonist persona of a domain pack — never on this character.

## Personality
Curious, polite, a little hesitant; asks the question the audience is thinking.

## Voice
openai ash — friendly, curious, casual (see `assets/voices.yaml`; Arabic: same voice id, Egyptian-colloquial instructions).

## Acting range
Favourite poses: `think`, `phone`, `type`, `point` · expressions: `think`, `neutral`, `happy`, `worried` (all from `schemas/enums.json`).

## Do / Don't
| Do | Don't |
|---|---|
| Pause and think (`think`) before acting | Be shown as foolish |
| Model the correct behaviour in replays | Wear orange (reserved for the antagonist) |

## Generated imagery
Only when the kit persona cannot do the job (e.g. a poster). Use `prompt.txt` verbatim (locked); replace `{SCENE}` with pose + setting only (or "plain background"),
never edit the character block, keep the no-text suffix last. Record provider, seed and licence in storyboard `generated_images[]`.
