# Fact extraction, conflicts and outdated material

## Ids and citation
- Sources `S01, S02 …` (append mode continues numbering). Chunks `c1, c2 …` per source.
- Cite as `S01` (whole source) or `S01#c3` (chunk) in storyboard claims, quiz items and curriculum objectives.
- Facts `F001 …` are global, never reused after deletion. Facts carry `source_id`, `chunk_id`, `loc`.

## Fact kinds — what to extract
| kind | Extract when the text… | Example |
|---|---|---|
| policy | states a must/shall/required rule or limit | "A receipt is required for every expense over $25." |
| procedure | names a multi-step process | "Submitting an expense claim (6 steps)" |
| step | is one action of a procedure (`procedure_order` 1..n) | "Attach the receipt photo to each line." |
| definition / term | defines a word (term = short glossary entry) | "Per diem: fixed daily allowance…" |
| warning | says never/do not, or a consequence | "False claims can lead to dismissal." |
| statistic | reports a measured number with year/population | "In 2025, 18% of claims were returned…" |
| example / case | illustrates with a story or worked case | "Mona's client dinner…" |
| fact | other checkable statement (scope, owner, numbers) | "Applies to employees, contractors and interns." |
| quote | a verbatim line worth quoting (with speaker) | "…" — CEO memo, 2026 |

Atomic: one rule per fact. Split "A up to $1,000; B up to $5,000" only if lessons will test them separately.
Keep exact numbers/currencies/units; never round. Paraphrase only to make the fact self-contained.

## Auto-candidates (deterministic)
`ingest.py` seeds facts tagged `auto-candidate` (confidence 0.4) from: numbered/bulleted items under a
procedure-like heading (→ `step`), must/shall lines (→ `policy`), never/do-not lines (→ `warning`),
"X: …" / "means" lines (→ `definition`), % / average lines (→ `statistic`), "Example:" lines, other numeric sentences.
The LLM pass rewrites/keeps/drops them; `merge_facts.py` removes a chunk's auto-candidates when its batch is merged.
If no LLM pass happens (offline), auto-candidates are still citable but the grounding report marks low confidence.

## Conflicts
Automatic (`ingest.py` / `merge_facts.py`): two facts from different chunks with
(≥ 3 shared content words and ≥ 45 % overlap) or (same unit — money, %, days, years… — and ≥ 2 shared words, ≥ 30 % overlap)
**and different numbers** → `conflicts[]` entry `resolution: unresolved`.
Example from the golden sources: expense SOP "keep receipts 7 years" (2026) vs data-retention policy "expense receipts 6 years" (2019).

Resolution order (write it into `resolution` and `chosen_fact`):
1. Higher `authority` wins (official policy > guide > slide deck > chat).
2. Newer effective date wins when authority is equal.
3. More specific scope wins ("expense receipts" over "financial records").
4. Still unclear → `resolution: "ask owner"`; the lesson avoids the number or states both with dates; orchestrator raises it at the gate.

## Outdated material
- Source `date` older than `--max-age-years` (default 3) → facts tagged `outdated?`, listed in `cache/ingest_report.md`.
- Facts with their own old year (statistics "In 2019 …") → flag in the LLM pass via `tags: [outdated?]`.
- Regulatory references (laws, standards, version numbers) → tag `check-currency`; the grounding check reports them.
- Never silently update an outdated number from model knowledge — label `general_knowledge` and cite the year.

## Large sources (books, long videos, 100+ page manuals)
- Ingest once; never paste whole sources into later prompts. Later skills read `sources.yaml` (summaries + facts) and
  open `cache/…/cN.md` only for chunks they cite.
- LLM pass in batches of 5–10 chunks; run `merge_facts.py --todo --limit 10` to get the next batch.
- For > 200 chunks: summarise each chunk, then write a per-source summary fact (`kind: fact`, tag `overview`) from the
  chunk summaries; extract detailed facts only for chunks mapped to curriculum objectives.
