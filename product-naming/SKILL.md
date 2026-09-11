---
name: product-naming
description: Find and clear a unique, trademark-friendly product or company name — generate candidates in tiers (meaningful → suggestive → fanciful), verify domains against the live registries (RDAP), run exact-word web searches, check for competitor-name collisions and unwanted meanings across the target market's languages, then rank survivors or critique names the user proposes. Use when the user asks to name or rename a product, company, feature or brand, asks whether a name is "taken", wants alternatives that are "lighter" or "unique", or asks to debate two candidate names.
---

# Product naming and clearance

A name is "unique enough" when **no company or product in the same category uses it, no direct competitor's name is inside it, the domains you need are unregistered, and it carries no unwanted meaning in the market's languages**. Zero web hits is not achievable for any pronounceable word and is not the bar.

## Quick start

1. Intake (one message, don't over-ask): product category, buyers vs users, target markets and their languages, tone wanted (solid / warm / playful), competitors to stay clear of, TLDs needed.
2. Generate a batch of **20 candidates** in one tier (see Tiers). Never search one name at a time.
3. Run `scripts/check_domains.sh <names…>` for `.com` and `.io` (add TLDs with `-t`). Keep only names whose required TLDs are free.
4. Exact-word web search each survivor (`"Name"` in quotes, then `"Name" company OR software OR app`). Drop any with a company, product, app or brand hit in the category or an adjacent one.
5. Competitor collision: does the name contain, rhyme with, or sound like any competitor's name when spoken? (e.g. *Forewiser* contained *Wizer*, a direct competitor.) Drop it.
6. Meaning check in every market language: dictionary meaning, slang, a person's name, a drug, a place. Drop or flag.
7. Present the survivors in a ranked table (see Output) and log what was rejected and why, so nobody re-tries them.

## Tiers — and what to expect

| Tier | Example | Registrable? | Findable in searches? |
|---|---|---|---|
| Descriptive (SecureLearn) | weak mark | no, and taken | — |
| Meaningful word in any language (Vigil, Aman, Yaqaza) | suggestive; ok | **almost always taken** in software/security/training — expect 0 of 20 to survive |
| Coined from a root (Forewise, Heedwise) | suggestive; good | ~1 in 10 survives; the `-wise`/`-ly`/`-ify` suffixes are crowded and date quickly |
| Fanciful (Tandrik, Vanta, Okta) | strongest | ~1 in 4 survives the domain check, ~1 in 2 of those survives the web search |

Start at the tier the user's taste allows, but tell them up front that meaningful words will not survive; move to fanciful after one failed round rather than burning three.

## Generating fanciful candidates

- 5–7 letters, two syllables, hard consonant start, vowel or `-k`/`-n` ending.
- Use only sounds every market pronounces: for Arabic-speaking markets avoid **p** and **v** (become b and f), avoid consonant clusters of three.
- No dictionary root in the market languages; check the obvious ones (English, Latin, Arabic, Persian/Urdu, Indonesian/Malay, Spanish) — a "meaningless" coinage often means *livestock* somewhere.
- Vary the sound: a soft set (vowel-heavy, m/n/l) and a solid set (k/t/d/r) so the user can choose lightness.
- Give the meaning to the **tagline**, not the name.

## Critiquing a proposed name

When the user brings a name, run steps 3–6 on it and answer with: verdict first, then a criteria table (meaning on first hearing, trademark strength, confusion risk, lightness, length/rhythm, pronunciation per market, room to grow, domains, persona potential), then the one fact that decides it. Offer a softer/harder variant with free domains when the user's objection is tone (e.g. Tandrik → Tandrika).

## Output

Table: rank · name · spelling in the market script · free domains · what the web returned · one-line note. Then: rejected names with the reason (one line each). Then the hand-off checklist the user must do themselves:

1. Say it aloud to two or three colleagues in each language.
2. WIPO Global Brand Database, then the national office, in the relevant Nice classes (software 9/42, training 41, security services 45).
3. Register the domains **the same day** — free coinages get drop-caught.

## Pitfalls seen in practice

- "Taken" on the user's side usually means the `.com` is registered — ask how they checked before generating more.
- A name that is clean everywhere can still be a **competitor's name plus a prefix**; always speak it.
- The same coinage may be a rare surname; that is fine. A common given name is not.
- Registry answers: 200 = registered, 404 = free, but a TLD the bootstrap does not serve also returns 404 — the script probes a control domain per TLD to tell them apart.

See [REFERENCE.md](REFERENCE.md) for registry endpoints, trademark databases, phonetic rules and a worked example.
