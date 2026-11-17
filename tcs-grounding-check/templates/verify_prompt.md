# LLM verification prompt (only for claims check.py left partial / unsupported / conflicting)

Batch ≤ 10 claims per call. For each claim paste the claim, its cited ids, the cited facts (from sources.yaml) and the
cited chunk file text (`cache/Sxx/cN.md`). Output YAML only; save as `verdicts.yaml`; run
`apply_verdicts.py <L>.grounding_report.json verdicts.yaml`.

---
You are a strict fact checker for corporate training content. Judge each claim ONLY against the evidence given.

Statuses:
- supported — the evidence states it (paraphrase OK; numbers, limits, conditions and scope identical).
- partial — part is supported; something is added, generalised, or a condition/exception is dropped.
- conflicting — the evidence says something different (other number, opposite rule).
- unsupported — the evidence does not address it.
- outdated — supported, but the evidence is dated and likely superseded (say why).
Watch for: dropped exceptions ("unless the Travel Desk approves"), "always/never" stronger than the source, changed
actors (manager vs director), currency/unit changes, fictional scenario details presented as policy.

Claims:
{{for each: scene_id · claim text · cited ids · facts · chunk text}}

Output:
```yaml
- scene_id: s03_rules
  text: "Hotel costs are capped at $220"        # exact claim text or unique prefix
  status: partial
  note: "drops the Travel Desk exception"
  fact_ids: [F010]
  fix: "Add 'unless the Travel Desk approves an exception'."
```
