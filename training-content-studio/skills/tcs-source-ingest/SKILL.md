---
name: tcs-source-ingest
description: Turns the user's raw source material (PDF/Word/PowerPoint/Excel/Markdown/HTML files, folders, web pages, YouTube/Vimeo or local recordings, Drive/OneDrive folders via rclone, pasted text) into a chunked, citable `sources.yaml` with S/F ids, chunk summaries, extracted facts/procedures/definitions and flagged conflicts or outdated items. Use when someone says "use these documents/this SOP/this video as the source", "ingest", "read my materials", or adds sources to an existing course. Not for writing objectives or lessons (tcs-curriculum), narration (tcs-scriptwriter) or checking finished content against sources (tcs-grounding-check).
---

# tcs-source-ingest

## Purpose
Every later claim in a course must point at a source id. This skill builds that evidence base once, keeps full text in
`cache/` so large sources never have to be re-read, and surfaces contradictions and stale material before scripting.

## Inputs
- Any mix of: local files (`.pdf .docx .pptx .xlsx .md .txt .html`), folders, `https://` pages, YouTube/Vimeo links,
  local video/audio (with optional `.vtt/.srt` sidecar), pasted text, `gdrive:` / `onedrive:` rclone paths.
- Run folder `runs/<run>/` (created by tcs-orchestrator) — output goes to `runs/<run>/sources.yaml`.
- Optional: `--authority 1-5` (5 = official policy), `--language`, `--course-id`, existing `sources.yaml` (`--append`).
- Secrets: `OPENAI_API_KEY` (only for whisper transcription) from env or the file in `TCS_ENV_FILE`.

## Outputs
| File | Content |
|---|---|
| `sources.yaml` | schema `schemas/sources.schema.json`: sources[] with chunks (id, loc, summary, tokens, path), facts[], glossary[], conflicts[] |
| `cache/<Sxx>/<cN>.md` | full text of each chunk (load only what you cite) |
| `cache/candidates.yaml` | deterministic fact candidates per chunk |
| `cache/ingest_report.md` | sources, dates, outdated list, conflicts, skipped inputs + next action |

## Steps
1. **Collect inputs.** List what the user gave; ask only if nothing usable was given. For Drive/OneDrive follow
   `references/loaders.md#cloud-folders` (print the rclone commands; let the user/orchestrator run the copy).
2. **Deterministic ingest** (script optional — a non-Claude user can do this by hand: split into ~1000-token chunks with locations):
   ```bash
   .venv/bin/python skills/tcs-source-ingest/scripts/ingest.py <paths|urls...> \
       --out runs/<run>/sources.yaml --course-id <id> [--authority 5] [--paste notes.txt] [--append]
   ```
   Exit 3 = some inputs skipped (read the report: missing yt-dlp, no API key, rclone path).
3. **Read the report** (`cache/ingest_report.md`): sources, detected dates, outdated (> 3 years), auto conflicts.
4. **LLM pass per chunk** (this is the part that needs a model):
   - `merge_facts.py runs/<run>/sources.yaml --todo --limit 10` → next chunks.
   - For each chunk, fill `templates/chunk_extract_prompt.md` with the chunk file + its candidates; collect YAML outputs
     into `runs/<run>/cache/extract-01.yaml` (shape: `templates/facts_batch.example.yaml`).
   - `merge_facts.py runs/<run>/sources.yaml --batch runs/<run>/cache/extract-01.yaml`
   - Repeat until `--todo` prints "all chunks summarised". Small sources (≤ 3 chunks) → one batch.
5. **Resolve conflicts** using the order in `references/extraction-rules.md#conflicts` (authority → date → specificity → ask).
   Write `resolution` + `chosen_fact` into `conflicts[]`. Unresolvable → keep `unresolved`; the orchestrator raises it at the gate.
6. **Validate**: `.venv/bin/python skills/tcs-source-ingest/scripts/validate_sources.py runs/<run>/sources.yaml`
   (errors must be 0; warnings reviewed).
7. **Hand-off summary** (≤ 10 lines): n sources, n chunks, n facts by kind, conflicts, outdated, gaps
   (topics the user asked for that no source covers → later claims must be `general_knowledge: true` or skipped).

## Rules / QA
- Never invent facts; every fact is something the chunk states. Model knowledge never enters `facts[]`.
- Keep numbers, currencies, units and dates exactly; one atomic statement per fact.
- Arabic sources stay Arabic (facts in source language; translation happens in tcs-localize).
- Cite precisely: `S01#c3` beats `S01`. `loc` = page/section/slide/timestamp.
- Do not paste whole sources into later prompts; downstream skills read summaries/facts and open only cited chunk files.
- Private material: never upload sources anywhere except the transcription call the user configured.
- Sources with authority ≤ 2 (chats, informal notes) can support examples but not policy claims.
- Images/scanned PDFs: no OCR here — describe or OCR externally and re-ingest as text.

## References (load on demand)
- `references/loaders.md` — per-format behaviour, whisper/yt-dlp, rclone Drive/OneDrive commands, chunking, metadata.
- `references/extraction-rules.md` — fact kinds, auto-candidates, conflict + outdated rules, very large sources.
- `templates/chunk_extract_prompt.md`, `templates/facts_batch.example.yaml`.
- Scripts: `ingest.py`, `merge_facts.py`, `validate_sources.py`, `md_to_pdf.py` (fixtures). Tests: `tests/`.
