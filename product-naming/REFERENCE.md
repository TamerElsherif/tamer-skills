# Product naming — reference

## Domain availability via RDAP

RDAP is the registries' own JSON protocol; it needs no API key. `scripts/check_domains.sh` asks these registries directly and falls back to the IANA bootstrap (`https://rdap.org/domain/<name>.<tld>`) for other TLDs; the bootstrap does not serve every TLD (`.io` and `.co` among them) and rate-limits bursts, so a control domain is probed per TLD first:

| TLD | Endpoint |
|---|---|
| .com / .net | `https://rdap.verisign.com/com/v1/domain/<name>.com` |
| .io | `https://rdap.identitydigital.services/rdap/domain/<name>.io` |
| .org | `https://rdap.publicinterestregistry.org/rdap/domain/<name>.org` |
| .app / .dev | `https://pubapi.registry.google/rdap/domain/<name>.app` |

Status codes: **200 registered · 404 not registered · anything else = registry unreachable or TLD unsupported** (the script reports `n/a`). A 404 means "not registered right now"; premium-priced or reserved names can still be unavailable to buy, so the final check is the registrar's cart.

## Trademark databases (user must run these; they need a session or captcha)

- WIPO Global Brand Database — https://branddb.wipo.int
- EUIPO TMview — https://www.tmdn.org/tmview
- USPTO — https://tmsearch.uspto.gov
- Egypt: ITDA / Egyptian Patent and Trademark Office search (Arabic UI)
- Saudi Arabia: SAIP trademark search; UAE: MoE trademark search
- Nice classes that matter for software products: **9** (software), **41** (education/training), **42** (SaaS), **45** (security services), 35 (business services) if the product has a marketplace.

## Exact-word web search protocol

1. `"Name"` — everything.
2. `"Name" company OR software OR app OR platform` — commercial uses.
3. `"Name" <category words>` (e.g. *security awareness training*) — same-category uses.
4. For a compound (Forewiser): search each part that could be a brand on its own (*Wizer*).

Interpretation: a company or product in the same or an adjacent category → reject. A person's surname, a place, an opera, a product in an unrelated category (spa, plates, tiles) → note it, keep the name. A common given name → reject (it will never be "yours").

## Phonetics for MENA-first products

- Arabic has no **p** or **v**: Vigilo → "Figilo", Prudify → "Brudify". Prefer b, f, k, t, d, s, r, m, n, l, z, w, y.
- Avoid three-consonant clusters (str, ndr are borderline; Tandrik works because n-d-r splits across syllables).
- Long vowels transliterate cleanly: a → ا, i/ee → ي, o/u → و. Give every shortlist entry its Arabic spelling so the user hears it.
- Check the coinage against Arabic, Persian/Urdu and Turkish roots as well as English; the Gulf and Egypt hear all of them.

## Suffix and pattern warnings

- `-wise`, `-ly`, `-ify`, `-io`, `-ly`, `-hub`, `-ify` are crowded; registrable but generic-feeling and they date.
- `Al-`/`-tech`/`-soft` read as small local IT shops in MENA.
- Anything ending in `-a` reads feminine in Arabic and Romance languages; fine for a brand (Vanta, Drata) but tell the user.

## Worked example (2026-09, security-awareness LMS for Egypt/MENA)

- Rounds 1–10, ~60 meaningful and coined names (Arabic, Latin, English): **0 survived** in class. Examples of what took them: Yaqaza (pharma services, Cairo), Hirz (Saudi security contractor), Diraya (two software firms), Caveo (three security firms), Munio (two), Cautus (two), Doceo (Docebo), Rakeen and Certes (cybersecurity vendors), Tamreen, Darsa, Rasd, Hazm (Gulf apps).
- Round 11, 40 fanciful coinages → 14 with free `.com` → 8 with no commercial web hit: Tandrik, Kamtira, Nesdara, Dastrik, Rasteka, Karnesa, Nestrika, Sondrika. Dropped after search: Ternaka (Indonesian *livestock*), Lodrana (≈ a drug), Salmika/Dortena (given names), Mekrana (a marble town).
- User proposal **Forewiser**: domains free, no web hit, but contains **Wizer**, an established vendor in the same category → advised against. Chosen: **Tandrik**; softer variant with free domains: Tandrika.

## Rename hand-off (when the product already exists)

Rename everything the product *presents* (UI, settings default, mail, API/MCP identity, filenames, storage keys, package name, docs). Keep infrastructure identifiers that would break a running deployment (compose project, databases, volumes, key prefixes, repository name) and leave historical log entries as they were; add a one-line "formerly X" note in README, CLAUDE.md and the domain glossary. Log the decision with the rejected names.
