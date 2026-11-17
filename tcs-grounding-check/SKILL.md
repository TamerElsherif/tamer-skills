---
name: tcs-grounding-check
description: Audits a finished lesson for factual grounding — every storyboard claim, quiz answer key and on-screen number is checked against the cited `sources.yaml` facts and chunk text (ids exist, wording and numbers match, conflicts, outdated sources, uncited numbers), followed by an LLM verification pass; writes `<lesson>.grounding_report.json` plus a markdown summary with fix guidance. Use for "fact-check / verify / is this accurate / check against the sources / why did grounding fail". Not for ingesting sources (tcs-source-ingest), writing claims (tcs-scriptwriter) or schema/visual lint (tcs-storyboard).
---

# tcs-grounding-check

## Purpose
Nothing ships that the sources don't say (or that isn't openly labelled general knowledge). This is the gate between
storyboard/quiz and rendering.

## Inputs
- `runs/<run>/sources.yaml` (+ `cache/` chunk files), `runs/<run>/lessons/<L>/<L>.storyboard.json`,
  optional `<L>.quiz.json` and `curriculum.yaml` (objective coverage). Localized storyboards (`<L>.ar-EG.storyboard.json`)
  are checked the same way (claims usually stay in the source language).

## Outputs
- `runs/<run>/lessons/<L>/<L>.grounding_report.json` (schema `schemas/grounding_report.schema.json`; summary also has `partial`).
- `<L>.grounding_report.md` — counts + table of claims needing fixes + uncovered objectives.
- Exit code: 0 pass · 2 needs fixes · 1 bad input (orchestrator/autopilot gate and `qa/<L>.qa.json` use it).

## Steps
1. **Deterministic check**:
   ```bash
   .venv/bin/python skills/tcs-grounding-check/scripts/check.py --sources runs/<run>/sources.yaml \
     --storyboard runs/<run>/lessons/<L>/<L>.storyboard.json [--quiz …/<L>.quiz.json] [--curriculum runs/<run>/curriculum.yaml]
   ```
   Per claim: cited id exists → candidate facts (cited chunk first) → content-word overlap + number match →
   supported / partial / conflicting / unsupported; sources.yaml conflicts → conflicting; old source/fact → outdated;
   `general_knowledge` → general-knowledge (unsupported if the course forbids it); on-screen numbers missing from the
   scene's claims → unsupported. Quiz keys = correct option(s) + explanation vs cited facts.
2. **LLM verification** for every partial/unsupported/conflicting claim (and a 10 % sample of supported ones on
   policy/number claims): fill `templates/verify_prompt.md` with the claim, cited facts and chunk text; save YAML
   verdicts; `scripts/apply_verdicts.py <report> verdicts.yaml`. Lexical matching misses paraphrases and can't see
   dropped exceptions — the LLM pass is what catches "always" vs "unless…".
3. **Fix** with `references/autofix.md` (re-cite → soften → label general knowledge → remove), editing script,
   storyboard props/narration and quiz consistently; re-run step 1 until exit 0.
4. **Report** to the orchestrator: summary line, fixes applied, open conflicts/outdated items needing the owner.

## Rules / QA
- Evidence = sources.yaml facts + cited chunk text only; model knowledge never upgrades a claim to supported.
- Numbers must match exactly (units, currency, limits); conditions/exceptions must survive.
- Unresolved source conflicts block the claim until resolved in sources.yaml (tcs-source-ingest) or avoided.
- Outdated is a warning for the gate unless the claim is a policy number — then confirm with the owner.
- Fictional scenario details are fine when labelled (claim "Scenario: … (fictional example)" `[general]`).

## References (load on demand)
- `references/autofix.md` — fixes per status, what autopilot may auto-apply.
- `templates/verify_prompt.md` — LLM verification prompt + verdict format.
- Scripts: `check.py`, `apply_verdicts.py`. Tests: `tests/`.
