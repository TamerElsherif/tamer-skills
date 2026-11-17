# Loaders — what `ingest.py` does per input

| Input | Detected by | Loader | `loc` format | Notes |
|---|---|---|---|---|
| PDF | `.pdf` | PyMuPDF text per page, hard-wraps re-joined, TOC → headings | `p. 3`, `p. 3-4` | scanned PDFs have no text → chunk summary says so; OCR externally then re-ingest |
| Word | `.docx` | python-docx paragraphs; Heading/Title styles split sections; tables appended | `§ Heading`, `table 2` | core_properties author/modified used when text lacks Owner/Effective date |
| PowerPoint | `.pptx` | python-pptx shape text + tables + **speaker notes** per slide | `slide 5` | notes often hold the real narration — keep them |
| Excel | `.xlsx` | openpyxl; header row → `col: value` lines, 40 rows per segment | `Sheet rows 2-41` | for catalogs/trackers; formulas read as cached values |
| Markdown | `.md` | split on `#`…`####` headings | `§ 4. Policy rules` | |
| Text | `.txt`, unknown | blank-line paragraphs | `para 7` | |
| HTML file / URL | `.html` / `http(s)://` | stdlib HTMLParser; drops script/style/nav/footer; h1–h3 split | `§ heading` | URL PDFs are downloaded and loaded as PDF; `type: url` |
| YouTube / Vimeo | host match | `yt-dlp` subtitles (manual → auto, en/ar) → else audio → whisper-1 | `00:01:20-00:02:25` | 60 s windows; needs `yt-dlp` (`uv pip install -p .venv/bin/python yt-dlp`) |
| Local video/audio | `.mp4 .mov .mkv .webm .mp3 .wav .m4a …` | sidecar `.vtt/.srt` if present, else ffmpeg → mono 16 kHz 32 kbps mp3 → whisper-1 | `hh:mm:ss-hh:mm:ss` | files > 24 MB split into 20-min parts |
| Image | `.png .jpg .webp` | recorded only | `whole` | describe in the LLM step (vision model) |
| Pasted text | `--text "…"`, `--paste file`, `--paste -` | text loader | `para N` | `type: pasted`, title from `--title` |
| Folder | directory | recursive, supported extensions only, hidden files skipped | per file | one source per file |
| Drive / OneDrive | `remote:path` (rclone syntax) | **not run** — prints rclone instructions, exit code 3 | — | see below |

## Whisper (OpenAI `whisper-1`)
- Key: `OPENAI_API_KEY` from env, or from the file named in `TCS_ENV_FILE` (`KEY=value` lines). Never written anywhere.
- `POST https://api.openai.com/v1/audio/transcriptions` (`model=whisper-1`, `response_format=verbose_json`) via `requests`.
- Segment timestamps → 60 s windows → `loc` ranges; chunk files keep the window text.
- Arabic audio: whisper auto-detects; Egyptian colloquial transcribes acceptably — spot-check names and numbers.

## Cloud folders (rclone) — instructions, not automation
The user has an rclone remote `gdrive:` (Google Drive). OneDrive works the same once configured (`rclone config` → `onedrive`).
```bash
rclone lsd gdrive:                                   # list top folders
rclone lsf "gdrive:Training/Expenses" --max-depth 2  # inspect
rclone copy "gdrive:Training/Expenses" runs/<run>/inbox/gdrive --drive-export-formats docx,xlsx,pptx,pdf
.venv/bin/python skills/tcs-source-ingest/scripts/ingest.py runs/<run>/inbox/gdrive \
    --uri-prefix "gdrive:Training/Expenses" --out runs/<run>/sources.yaml
# OneDrive
rclone copy "onedrive:Policies" runs/<run>/inbox/onedrive && ingest.py runs/<run>/inbox/onedrive --uri-prefix onedrive:Policies --out …
```
- Google Docs/Sheets/Slides export only with `--drive-export-formats`.
- Shared drives: `rclone lsd gdrive: --drive-shared-with-me` or a remote with `team_drive` set.
- Ask before copying large folders (> 1 GB); copy only what the course needs.

## Chunking
- Target 800–1200 tokens (estimate = max(words × 1.33, chars / 4)); segments are packed in order, never across sources.
- Over-long segments split at sentence boundaries (abbreviations like "Co." and "e.g." protected).
- `loc` of a chunk = first … last segment location (`p. 1-2`, `§ A … § C`, `00:00:00-00:03:00`).
- Full text: `cache/<Sxx>/<cN>.md` (header comment with citation id). sources.yaml keeps only summaries → later skills
  load just the chunks they cite (`path` is relative to the run folder).

## Metadata
- `date`: "Effective date / Last reviewed / Last updated / Issued / Published / Date:" in the first 3000 chars, else file metadata.
- `owner`: "Owner: / Policy owner: / Author:" line, else file metadata author.
- `language`: Arabic-script share → `ar-*` (≥ 3 Egyptian markers ده/دي/عشان/مش/إزاي… → `ar-EG`, else `ar-MSA`); English `-ise/-our` spellings → `en-GB`.
- `authority`: set with `--authority 5` for official policy/standards, 3 for internal guides, 1 for informal notes/chats.
- Duplicate content (same SHA-1 of extracted text) is skipped and reported.
