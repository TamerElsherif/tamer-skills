# Prioritization method (catalogue → ranked picks)

Generalized from the worked example (`_extraction.md` §2: 216 security courses → 20 picks, 10/5/5).
Use when there are more candidate topics than you will build. Script: `scripts/prioritize.py`; by hand: same steps in a table.

## Steps

| # | Step | Rule | Recorded as |
|---|---|---|---|
| 1 | **Filter** | drop out-of-remit topics, retired/irrelevant labels, regions you don't serve, text-only originals (if media required) | `decision: out-of-scope` + reason |
| 2 | **Already built** | titles in `existing` → `previously-built`; candidates sharing ≥50 % title words with a built item → gap = 1; same subject cluster → gap = 0.5 | `previously-built`, `why: gap:…` |
| 3 | **Score** 0–5 per dimension | see table below | `scores{}` |
| 4 | **Priority** | `P = Σ wᵢ·scoreᵢ` (weights sum to 1) | `priority` |
| 5 | **Dedupe by subject** | cluster = "Alternative versions" links ∪ explicit `clusters` regexes ∪ same normalized title (variant words stripped), within one audience segment. Keep the **richest original** (cartoon/whiteboard > explainer > text; more media; more languages); it inherits the cluster's best score per dimension | `deprioritised-duplicate` + "duplicate subject of …" |
| 6 | **Quotas** | greedy by P: each item goes to its preferred segment, else an eligible fallback segment with room. `family_cap` (soft) limits picks per subject family (parent + specialisations via the prerequisite column); relaxed if a quota would stay empty | `include`, `tier: Top`, `rank` |
| 7 | **Tier** | next `tier2` items → `tier-2`; rest → `tier-3`; every row keeps a reason | `tier-2` / `tier-3` |
| 8 | **Validate sources** (manual) | open each pick's original; if the file doesn't match the title, swap in the sibling from the same cluster and note it | reason "replaces #n …" |

## Scoring dimensions

| Dimension | Meaning | Automatic signal (config) | Typical high |
|---|---|---|---|
| impact | harm if people get it wrong | `scoring.keywords.impact` on the title (topic column counts `topic_penalty` lower) | BEC, ransomware, help-desk SE |
| frequency | how often the audience meets it | title keywords; audience breadth (`audience_frequency`, e.g. "all staff" = 4); `foundation_bonus` if many items list it as prerequisite; `specialisation_penalty` if it has a prerequisite | phishing, passwords |
| gap | not already covered | default 3; lowered by step 2 | — |
| urgency | emerging / time-sensitive | `scoring.keywords.urgency` | deepfakes, MFA fatigue, ClickFix |
| compliance | mandatory / evidence needed | label column (`label_compliance`: core/mandatory = 5 … optional = 1) and compliance keywords (ISO 27001, PCI…) | annual core courses |

Defaults: impact .30 · frequency .25 · gap .20 · urgency .15 · compliance .10. A domain pack can change any of them.
If the candidate file already has `scores:` per item, those are used as-is (manual scoring workshop).

## Configuration (resolution order)

Layered, later wins: `templates/prioritization.default.yaml` → `templates/prioritization.<pack>.yaml` →
`domains/<pack>/prioritization.yaml` (or `prioritization:` in `domains/<pack>/pack.yaml`) → `--config profile.yaml`.
CLI `--weights`, `--quotas`, `--tier2`, `--existing` override the profile.

Keys: `weights`, `quotas` (segment → n), `tiers.tier2`, `family_cap`, `segments[]` (`id`, `match` substrings on
"audience | title", one `default: true`), `filters` (`exclude_topics`, `exclude_labels`, `allowed_regions`, `require_media`),
`scoring` (`default`, `topic_penalty`, `specialisation_penalty`, `foundation_bonus`, `label_compliance`,
`audience_frequency`, `keywords.{impact,frequency,urgency,compliance}`, `richness_format`), `clusters`, `title_noise`,
`existing`, `families` (`{id: {match: [...], cap: n}}` subject families for the soft cap), `format_map`
(original style → plugin format), `minutes_per_lesson`. A pack file written in the descriptive shape
(`quotas` with `exec`, `audiences{seg: [labels]}`, `clusters{id: {members}}`) is adapted: aliases map to segment ids,
labels extend segment matching, cluster members become extra families (profile families win on overlap).

## Input formats

- **Spreadsheet** (`.xlsx`/`.csv`, opened read-only): the sheet with a title-like header and the most rows (or `--sheet`).
  Columns found by synonym: id `#`, title `Course/Title`, topic, audience `Target audience`, label `Priority/Status`,
  region, format, media `Videos`, alternatives `Alternative versions`, languages, prerequisite `Dependency (take first)`.
- **YAML**: `candidates: [{id, title, topic, audience, label, region, format, media_count, alternatives, prerequisite, scores?}]`.

## Output

`curriculum.yaml` (schema-valid, `approval: draft`): one module per segment (≤ 12 lessons; split ≥ 7 by hand into ≤ 6),
one DRAFT objective per included item (rewrite them — step 3 of SKILL.md), `prioritization.items[]` for **every**
candidate with scores, priority, decision, tier, rank, reason. `--md` writes the ranked table for the approval gate.

## Validation against the worked example

`prioritize.py Security-awareness-course-catalog.xlsx --pack security-awareness` (catalogue 216 rows; profile
`templates/prioritization.security-awareness.yaml`, existing = AI-Driven Spear Phishing, ISO 27001: Awareness):

- **18 of the session's 20 picks** reproduced (17 exact + "Information & Data" for "Data Loss" — same subject cluster,
  the method picks the richer whiteboard original).
- Differences: *Ransomware* (session's #21) instead of *MFA Fatigue* (here #22, family cap with passwords subjects), and
  *C-Suite: Passwords* instead of *C-Suite: Social Engineering* (tied priority; the social-engineering family cap was
  already used by the staff and help-desk courses).
- 45 duplicates, 70 out-of-scope (H&S, conduct, regional laws, simulation micro-trainings, blog-only), 2 previously built.
- Regression check: `scripts/test_prioritize.py` (set `TCS_TEST_CATALOG` and `TCS_TEST_TRACKER` to run it on a real catalogue).

Judgement calls the script cannot make — keep them for the human at the gate: cross-segment duplicates (an exec variant
of a staff course), a "story" original that is better than its richer sibling, and wrong-video folders (step 8).
