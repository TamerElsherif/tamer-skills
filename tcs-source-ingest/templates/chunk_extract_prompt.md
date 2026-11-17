# Chunk extraction prompt (one chunk per call)

Use with any LLM. Paste the chunk file (`<run>/cache/Sxx/cN.md`) where marked. Output YAML only.
Collect the outputs into one `extract.yaml` list and run `merge_facts.py <run>/sources.yaml --batch extract.yaml`.

---

You are extracting citable training facts from ONE chunk of a source document.

Source: {{source_id}} "{{source_title}}" ({{source_type}}, dated {{source_date or "unknown"}})
Chunk: {{source_id}}#{{chunk_id}} · location {{loc}}
Auto-candidates already found (keep, rewrite or drop them): {{candidates from cache/candidates.yaml}}

Rules
1. Only what the chunk says. No outside knowledge, no inference beyond a plain paraphrase.
2. One atomic statement per fact (one rule, one number, one step). Keep numbers, units, currencies, limits exactly.
3. `kind` ∈ fact | definition | procedure | step | example | policy | statistic | warning | term | case | quote.
   - `procedure` = the name/purpose of a procedure; each action = `step` with `procedure_order` 1..n.
   - `statistic` = a measured number with its year/population; `policy` = must/shall rule; `warning` = never/don't/consequence.
4. `loc`: the most precise location inside the chunk (page, section, slide, mm:ss) if visible.
5. `date`: only if the chunk states a date for that fact (e.g. "In 2025, …" → 2025).
6. `confidence`: 0.9 verbatim/explicit · 0.7 paraphrased · 0.5 implied.
7. Glossary: domain terms with a definition in the chunk (add Arabic `ar` only if the source gives it).
8. Conflicts: if the chunk contradicts itself, list both texts in `conflicts` (note why).
9. Summary: 1–3 sentences, ≤ 60 words, what a course designer needs to know is in this chunk.
10. Write in the chunk's language. Arabic stays Arabic.

Output (YAML, exactly this shape):
```yaml
- chunk: S01#c1
  summary: "…"
  source_date: "2026-03-01"      # only if the chunk shows the document's effective date
  drop: []                       # ids of existing NON-auto facts that are wrong (rare)
  facts:
    - {kind: policy, text: "A receipt is required for every expense over $25.", loc: "§4 rule 1", confidence: 0.9}
    - {kind: step, text: "Open the Northwind Expenses app and select New Claim.", procedure_order: 2, loc: "§5", confidence: 0.9}
  glossary:
    - {term: "Per diem", definition: "Fixed daily allowance for meals and incidentals on overnight business travel."}
  conflicts: []
```

---
CHUNK TEXT:
{{paste chunk file}}
