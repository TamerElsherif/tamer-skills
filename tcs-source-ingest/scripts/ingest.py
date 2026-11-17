#!/usr/bin/env python3
"""Deterministic half of tcs-source-ingest.

Loads sources (files, folders, URLs, YouTube/Vimeo, pasted text), splits them into ~800-1200-token chunks
with locations, caches full chunk text under <run>/cache/<Sxx>/cN.md, writes sources.yaml (schema 1.0) with
[auto] chunk summaries and auto-candidate facts, plus cache/candidates.yaml and cache/ingest_report.md.
The LLM step (tcs-source-ingest SKILL.md, step 4) then replaces [auto] summaries and candidates via merge_facts.py.

Usage:
  ingest.py <path|folder|url|youtube-url|remote:path ...> --out runs/x/sources.yaml
            [--paste FILE|-] [--text "..."] [--append] [--course-id ID] [--language en-US]
            [--authority 1-5] [--no-seed-facts] [--max-age-years 3] [--today YYYY-MM-DD]
Exit codes: 0 ok, 1 nothing ingested / error, 3 some inputs skipped (see report).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as htmllib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TARGET_MIN, TARGET_MAX = 800, 1200  # tokens per chunk
DOC_EXT = {".pdf": "pdf", ".docx": "docx", ".pptx": "pptx", ".xlsx": "xlsx", ".md": "markdown",
           ".markdown": "markdown", ".txt": "text", ".html": "html", ".htm": "html"}
AV_EXT = {".mp4": "video", ".mov": "video", ".mkv": "video", ".webm": "video", ".m4v": "video",
          ".mp3": "audio", ".wav": "audio", ".m4a": "audio", ".ogg": "audio", ".flac": "audio"}
IMG_EXT = {".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image", ".gif": "image"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}


# --------------------------------------------------------------------------- data
@dataclass
class Segment:
    loc: str          # "p. 3", "§ 4. Policy rules", "slide 5", "00:01:20-00:02:10", "Sheet1 rows 1-40"
    text: str
    heading: str = ""


@dataclass
class Loaded:
    type: str
    title: str
    uri: str
    segments: list[Segment] = field(default_factory=list)
    date: str | None = None
    owner: str | None = None
    language: str | None = None
    pages_or_duration: str | None = None
    note: str | None = None


# --------------------------------------------------------------------------- helpers
def norm(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = t.replace("\u00ad", "")
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


ABBR = re.compile(r"\b(Co|Inc|Ltd|LLC|Mr|Mrs|Ms|Dr|No|vs|etc|e\.g|i\.e|approx|Dept|St)\.", re.I)


def sent_split(text: str) -> list[str]:
    """Sentence split that does not break after common abbreviations (Co., e.g., No.)."""
    prot = ABBR.sub(lambda m: m.group(0)[:-1] + "\u2024", text)
    parts = re.split(r"(?<=[.!?؟])\s+", prot)
    return [x.replace("\u2024", ".").strip() for x in parts if x.strip()]


def unwrap(text: str) -> str:
    """Join hard-wrapped PDF lines: a long line without end punctuation continues on the next line."""
    lines, out = text.splitlines(), []
    for ln in lines:
        s = ln.strip()
        if out and s and out[-1] and not re.search(r"[.!?:;؟]$", out[-1]) \
                and not re.match(r"^([-*•▪]|\d+[.)]\s)", s) \
                and (len(out[-1]) >= 60 or s[:1].islower()):
            out[-1] = out[-1] + " " + s
        else:
            out.append(s)
    return "\n".join(out)


def est_tokens(t: str) -> int:
    words = len(t.split())
    return max(int(words * 1.33), len(t) // 4)


def detect_lang(t: str) -> str:
    sample = t[:4000]
    ar = len(re.findall(r"[\u0600-\u06FF]", sample))
    lat = len(re.findall(r"[A-Za-z]", sample))
    if ar > lat:
        egy = len(re.findall(r"(?:^|\s)(?:ده|دي|عشان|إزاي|ازاي|مش|كده|بتاع|إيه|ليه|هنا|دلوقتي)(?=\s|$)", sample))
        return "ar-EG" if egy >= 3 else "ar-MSA"
    gb = len(re.findall(r"\b\w+(?:ise|isation|our)\b", sample))
    return "en-GB" if gb >= 3 else "en-US"


DATE_PATTERNS = [
    r"(?:effective|issued|published|last (?:reviewed|updated|revised)|date|version date)\s*(?:date)?\s*[:\-]?\s*"
    r"(\d{4}-\d{2}-\d{2}|\d{1,2} [A-Z][a-z]+ \d{4}|[A-Z][a-z]+ \d{1,2},? \d{4})",
]
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def parse_date(s: str) -> str | None:
    s = s.strip().rstrip(".")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return m.group(0)
    m = re.match(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", s)
    if m and m.group(2).lower() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    m = re.match(r"([A-Za-z]+) (\d{1,2}),? (\d{4})", s)
    if m and m.group(1).lower() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
    m = re.match(r"D:(\d{4})(\d{2})(\d{2})", s)  # PDF metadata
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def find_doc_date(text: str) -> str | None:
    head = text[:3000]
    found = []
    for pat in DATE_PATTERNS:
        for m in re.finditer(pat, head, re.I):
            d = parse_date(m.group(1))
            if d:
                found.append((m.group(0).lower(), d))
    for label in ("effective", "last reviewed", "last updated", "last revised", "issued", "published", "date"):
        for k, d in found:
            if k.startswith(label):
                return d
    return found[0][1] if found else None


def find_owner(text: str) -> str | None:
    m = re.search(r"^\s*(?:owner|policy owner|document owner|author)\s*[:\-]\s*(.+)$", text[:3000], re.I | re.M)
    return m.group(1).strip()[:120] if m else None


def load_env_key(name: str) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    envf = os.environ.get("TCS_ENV_FILE")
    if envf and Path(envf).expanduser().exists():
        for line in Path(envf).expanduser().read_text().splitlines():
            m = re.match(rf"^\s*(?:export\s+)?{name}\s*=\s*['\"]?([^'\"\s]+)", line)
            if m:
                return m.group(1)
    return None


# --------------------------------------------------------------------------- loaders
def load_pdf(p: Path) -> Loaded:
    import pymupdf
    doc = pymupdf.open(str(p))
    meta = doc.metadata or {}
    toc = {page: title for _lvl, title, page in doc.get_toc()}
    segs, current = [], ""
    for i, page in enumerate(doc, 1):
        current = toc.get(i, current)
        t = unwrap(norm(page.get_text()))
        if t:
            segs.append(Segment(f"p. {i}", t, current))
    full = "\n".join(s.text for s in segs)
    date = find_doc_date(full) or parse_date(meta.get("modDate") or "") or parse_date(meta.get("creationDate") or "")
    return Loaded("pdf", meta.get("title") or p.stem, str(p), segs, date, find_owner(full) or meta.get("author") or None,
                  pages_or_duration=f"{doc.page_count} pages")


def split_markdown(text: str) -> list[Segment]:
    segs, head, buf = [], "", []
    for line in text.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            if "\n".join(buf).strip():
                segs.append(Segment(f"§ {head}" if head else "§ (intro)", norm("\n".join(buf)), head))
            head, buf = m.group(2).strip(), [line]
        else:
            buf.append(line)
    if "\n".join(buf).strip():
        segs.append(Segment(f"§ {head}" if head else "§ (intro)", norm("\n".join(buf)), head))
    return segs


def load_markdown(p: Path) -> Loaded:
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return Loaded("markdown", m.group(1).strip() if m else p.stem, str(p), split_markdown(text),
                  find_doc_date(text), find_owner(text))


def load_text(p: Path, typ: str = "text", text: str | None = None, title: str | None = None) -> Loaded:
    text = text if text is not None else p.read_text(encoding="utf-8", errors="replace")
    paras = [x for x in re.split(r"\n\s*\n", text) if x.strip()]
    segs = [Segment(f"para {i}", norm(x)) for i, x in enumerate(paras, 1)]
    first = text.strip().splitlines()[0][:80] if text.strip() else "Untitled"
    return Loaded(typ, title or (p.stem if p else first), str(p) if p else "pasted", segs,
                  find_doc_date(text), find_owner(text))


def load_docx(p: Path) -> Loaded:
    import docx
    d = docx.Document(str(p))
    segs, head, buf = [], "", []

    def flush():
        if "\n".join(buf).strip():
            segs.append(Segment(f"§ {head}" if head else "§ (intro)", norm("\n".join(buf)), head))

    for para in d.paragraphs:
        style = (para.style.name or "").lower() if para.style is not None else ""
        if style.startswith("heading") or style == "title":
            flush()
            head, buf = para.text.strip(), [para.text]
        else:
            prefix = "- " if "list" in style else ""
            buf.append(prefix + para.text)
    flush()
    for ti, table in enumerate(d.tables, 1):
        rows = [" | ".join(c.text.strip() for c in r.cells) for r in table.rows]
        segs.append(Segment(f"table {ti}", norm("\n".join(rows)), f"table {ti}"))
    cp = d.core_properties
    full = "\n".join(s.text for s in segs)
    date = find_doc_date(full) or (cp.modified.date().isoformat() if cp.modified else None)
    return Loaded("docx", cp.title or p.stem, str(p), segs, date, cp.author or find_owner(full))


def load_pptx(p: Path) -> Loaded:
    from pptx import Presentation
    pr = Presentation(str(p))
    segs = []
    for i, slide in enumerate(pr.slides, 1):
        texts, title = [], ""
        for shp in slide.shapes:
            if shp.has_text_frame and shp.text_frame.text.strip():
                if shp == getattr(slide.shapes, "title", None):
                    title = shp.text_frame.text.strip()
                texts.append(shp.text_frame.text)
            if getattr(shp, "has_table", False) and shp.has_table:
                for r in shp.table.rows:
                    texts.append(" | ".join(c.text for c in r.cells))
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
            texts.append("Speaker notes: " + slide.notes_slide.notes_text_frame.text)
        if texts:
            segs.append(Segment(f"slide {i}", norm("\n".join(texts)), title))
    cp = pr.core_properties
    return Loaded("pptx", cp.title or p.stem, str(p), segs,
                  cp.modified.date().isoformat() if cp.modified else None, cp.author or None,
                  pages_or_duration=f"{len(pr.slides)} slides")


def load_xlsx(p: Path) -> Loaded:
    import openpyxl
    wb = openpyxl.load_workbook(str(p), read_only=True, data_only=True)
    segs = []
    for ws in wb.worksheets:
        rows = [r for r in ws.iter_rows(values_only=True) if any(v not in (None, "") for v in r)]
        if not rows:
            continue
        header = [str(h) if h is not None else f"col{j}" for j, h in enumerate(rows[0], 1)]
        lines = []
        for r in rows[1:]:
            lines.append("; ".join(f"{h}: {v}" for h, v in zip(header, r) if v not in (None, "")))
        for k in range(0, max(len(lines), 1), 40):
            part = lines[k:k + 40]
            segs.append(Segment(f"{ws.title} rows {k + 2}-{k + 1 + len(part)}", norm("\n".join(part)), ws.title))
    return Loaded("xlsx", p.stem, str(p), segs)


class _HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.segs: list[Segment] = []
        self.head, self.buf, self.skip, self.title, self._in = "", [], 0, "", None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer", "noscript", "svg"):
            self.skip += 1
        if tag in ("h1", "h2", "h3"):
            self._flush()
            self._in = tag
        if tag == "title":
            self._in = "title"
        if tag in ("p", "li", "br", "tr", "div"):
            self.buf.append("\n- " if tag == "li" else "\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "noscript", "svg") and self.skip:
            self.skip -= 1
        if tag in ("h1", "h2", "h3", "title"):
            self._in = None

    def handle_data(self, data):
        if self.skip:
            return
        if self._in == "title":
            self.title += data
        elif self._in in ("h1", "h2", "h3"):
            self.head += data
            self.buf.append(data)
        else:
            self.buf.append(data)

    def _flush(self):
        t = norm("".join(self.buf))
        if t:
            self.segs.append(Segment(f"§ {self.head.strip()}" if self.head.strip() else "§ (intro)", t, self.head.strip()))
        self.head, self.buf = "", []

    def close(self):
        super().close()
        self._flush()


def load_html_text(raw: str, uri: str, typ: str = "html") -> Loaded:
    hp = _HTML()
    hp.feed(raw)
    hp.close()
    full = "\n".join(s.text for s in hp.segs)
    return Loaded(typ, htmllib.unescape(hp.title.strip()) or uri, uri, hp.segs, find_doc_date(full), find_owner(full))


def load_html(p: Path) -> Loaded:
    return load_html_text(p.read_text(encoding="utf-8", errors="replace"), str(p))


def load_url(url: str) -> Loaded:
    import requests
    r = requests.get(url, timeout=30, headers={"User-Agent": "tcs-source-ingest/1.0"})
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        tmp = Path(tempfile.mkdtemp()) / "download.pdf"
        tmp.write_bytes(r.content)
        ld = load_pdf(tmp)
        ld.type, ld.uri = "url", url
        return ld
    ld = load_html_text(r.text, url, "url")
    ld.date = ld.date or parse_date(r.headers.get("last-modified", "")[5:16] if r.headers.get("last-modified") else "")
    return ld


def fmt_ts(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def parse_vtt(text: str) -> list[tuple[float, float, str]]:
    cues, seen = [], set()
    for block in re.split(r"\n\s*\n", text):
        m = re.search(r"(\d+):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d+):(\d{2}):(\d{2})[.,](\d{3})", block)
        if not m:
            m2 = re.search(r"(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2})[.,](\d{3})", block)
            if not m2:
                continue
            a = int(m2.group(1)) * 60 + int(m2.group(2))
            b = int(m2.group(4)) * 60 + int(m2.group(5))
            body = block[m2.end():]
        else:
            a = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            b = int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7))
            body = block[m.end():]
        line = re.sub(r"<[^>]+>", "", body).strip()
        line = re.sub(r"\s+", " ", line)
        if line and line not in seen:  # auto-captions repeat lines
            seen.add(line)
            cues.append((a, b, line))
    return cues


def timed_segments(cues: list[tuple[float, float, str]], window: float = 60.0) -> list[Segment]:
    segs, buf, start = [], [], None
    for a, b, t in cues:
        start = a if start is None else start
        buf.append(t)
        if b - start >= window:
            segs.append(Segment(f"{fmt_ts(start)}-{fmt_ts(b)}", norm(" ".join(buf))))
            buf, start = [], None
    if buf:
        segs.append(Segment(f"{fmt_ts(start or 0)}-{fmt_ts(cues[-1][1])}", norm(" ".join(buf))))
    return segs


def ytdlp_bin() -> list[str] | None:
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        return None


def whisper_transcribe(audio: Path) -> list[tuple[float, float, str]]:
    """OpenAI whisper-1 via requests; splits files > 24 MB with ffmpeg."""
    import requests
    key = load_env_key("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set (env or TCS_ENV_FILE) - cannot transcribe")
    work = Path(tempfile.mkdtemp())
    small = work / "audio.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio), "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "32k", str(small)], check=True)
    parts = [small]
    if small.stat().st_size > 24 * 1024 * 1024:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(small), "-f", "segment", "-segment_time",
                        "1200", "-c", "copy", str(work / "part%03d.mp3")], check=True)
        parts = sorted(work.glob("part*.mp3"))
    cues, offset = [], 0.0
    for part in parts:
        with part.open("rb") as fh:
            r = requests.post("https://api.openai.com/v1/audio/transcriptions",
                              headers={"Authorization": f"Bearer {key}"},
                              data={"model": "whisper-1", "response_format": "verbose_json"},
                              files={"file": (part.name, fh, "audio/mpeg")}, timeout=600)
        r.raise_for_status()
        js = r.json()
        for s in js.get("segments", []):
            cues.append((offset + s["start"], offset + s["end"], s["text"].strip()))
        if js.get("segments"):
            offset = cues[-1][1]
    return cues


def load_av_file(p: Path, typ: str) -> Loaded:
    sidecar = next((p.with_suffix(s) for s in (".vtt", ".srt") if p.with_suffix(s).exists()), None)
    if sidecar:
        cues = parse_vtt(sidecar.read_text(encoding="utf-8", errors="replace"))
        note = f"transcript from {sidecar.name}"
    else:
        cues = whisper_transcribe(p)
        note = "transcribed with OpenAI whisper-1"
    dur = fmt_ts(cues[-1][1]) if cues else None
    return Loaded(typ, p.stem, str(p), timed_segments(cues), pages_or_duration=dur, note=note)


def load_online_video(url: str, cache: Path) -> Loaded:
    typ = "vimeo" if "vimeo.com" in url else "youtube"
    ytd = ytdlp_bin()
    if not ytd:
        raise RuntimeError("yt-dlp not installed: `uv pip install -p .venv/bin/python yt-dlp` (or brew install yt-dlp)")
    work = cache / "_av" / hashlib.sha1(url.encode()).hexdigest()[:10]
    work.mkdir(parents=True, exist_ok=True)
    meta = json.loads(subprocess.run(ytd + ["-J", "--no-warnings", url], capture_output=True, text=True,
                                     check=True).stdout)
    subprocess.run(ytd + ["--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", "en.*,ar.*",
                          "--sub-format", "vtt", "-o", str(work / "sub"), url], capture_output=True, text=True)
    vtts = sorted(work.glob("sub*.vtt"), key=lambda f: ("orig" in f.name, ".en" not in f.name))
    if vtts:
        cues, note = parse_vtt(vtts[0].read_text(encoding="utf-8", errors="replace")), f"subtitles {vtts[0].name}"
    else:
        subprocess.run(ytd + ["-x", "--audio-format", "mp3", "-o", str(work / "audio.%(ext)s"), url],
                       capture_output=True, text=True, check=True)
        cues, note = whisper_transcribe(next(work.glob("audio.*"))), "audio transcribed with whisper-1"
    up = meta.get("upload_date")
    return Loaded(typ, meta.get("title") or url, url, timed_segments(cues),
                  f"{up[:4]}-{up[4:6]}-{up[6:]}" if up else None, meta.get("uploader"),
                  pages_or_duration=fmt_ts(meta.get("duration") or 0), note=note)


def rclone_instructions(arg: str) -> str:
    remote = arg.split(":", 1)[0]
    kind = "OneDrive" if "onedrive" in remote.lower() else "Google Drive"
    return (f"{kind} remote `{arg}` is not fetched automatically. Copy it locally, then ingest the folder:\n"
            f"  rclone lsf {arg} --max-depth 2          # inspect\n"
            f"  rclone copy {arg} runs/<run>/inbox/{remote} --drive-export-formats docx,xlsx,pptx,pdf\n"
            f"  .venv/bin/python skills/tcs-source-ingest/scripts/ingest.py runs/<run>/inbox/{remote} --out ...\n"
            f"Record the original `{arg}` as uri (use --uri-prefix) so citations point to Drive.")


# --------------------------------------------------------------------------- chunking
def split_long(text: str, limit: int) -> list[str]:
    if est_tokens(text) <= limit:
        return [text]
    sents = [x for ln in text.split("\n") for x in sent_split(ln)]
    out, buf = [], ""
    for s in sents:
        if buf and est_tokens(buf + " " + s) > limit:
            out.append(buf.strip())
            buf = s
        else:
            buf = (buf + " " + s).strip()
    if buf:
        out.append(buf.strip())
    return out


def loc_range(a: str, b: str) -> str:
    if a == b:
        return a
    ma, mb = re.match(r"(p\.|slide|para) (\d+)", a), re.match(r"(p\.|slide|para) (\d+)", b)
    if ma and mb and ma.group(1) == mb.group(1):
        return f"{ma.group(1)} {ma.group(2)}-{mb.group(2)}"
    ta, tb = re.match(r"(\d\d:\d\d:\d\d)-", a), re.match(r"\d\d:\d\d:\d\d-(\d\d:\d\d:\d\d)", b)
    if ta and tb:
        return f"{ta.group(1)}-{tb.group(1)}"
    return f"{a} … {b}"


def chunk_segments(segs: list[Segment], lo: int = TARGET_MIN, hi: int = TARGET_MAX) -> list[dict]:
    pieces = []
    for s in segs:
        for part in split_long(s.text, hi):
            pieces.append((s.loc, part, s.heading))
    chunks, cur, locs, heads = [], [], [], []
    for loc, text, head in pieces:
        if cur and est_tokens("\n\n".join(cur + [text])) > hi and est_tokens("\n\n".join(cur)) >= lo * 0.5:
            chunks.append((cur, locs, heads))
            cur, locs, heads = [], [], []
        cur.append(text)
        locs.append(loc)
        if head and head not in heads:
            heads.append(head)
        if est_tokens("\n\n".join(cur)) >= lo:
            chunks.append((cur, locs, heads))
            cur, locs, heads = [], [], []
    if cur:
        tail = "\n\n".join(cur)
        if chunks and est_tokens(tail) < lo * 0.5 and est_tokens("\n\n".join(chunks[-1][0]) + tail) <= hi * 1.15:
            pc, pl, ph = chunks[-1]
            chunks[-1] = (pc + cur, pl + locs, ph + [h for h in heads if h not in ph])
        else:
            chunks.append((cur, locs, heads))
    out = []
    for i, (texts, locs, heads) in enumerate(chunks, 1):
        body = "\n\n".join(texts)
        out.append({"id": f"c{i}", "loc": loc_range(locs[0], locs[-1]), "text": body, "headings": heads,
                    "tokens": est_tokens(body)})
    return out


def auto_summary(text: str, headings: list[str]) -> str:
    body = re.sub(r"^#+\s.*$", "", text, flags=re.M)
    sents = [s for s in sent_split(re.sub(r"\s+", " ", body)) if len(s.split()) > 3]
    lead = " ".join(sents[:2])[:280]
    h = "; ".join(headings[:4])
    return f"[auto] {h + ' — ' if h else ''}{lead}".strip()


# --------------------------------------------------------------------------- candidates
NUM_RE = re.compile(r"(?:[$€£]|EGP|USD|SAR|AED)?\s?\d[\d,]*(?:\.\d+)?\s?(?:%|percent|per cent|days?|hours?|years?|months?|weeks?|minutes?|nights?|EGP|USD)?", re.I)
META_LINE = re.compile(r"^(version|effective date|owner|last (reviewed|updated|revised)|document (id|owner)|"
                       r"classification|approved by|issued)\s*[:\-]", re.I)
RULES = [
    ("example", re.compile(r"^\s*(example|e\.g\.|for example|case study|scenario)\b|مثال", re.I)),
    ("warning", re.compile(r"\b(never|do not|don't|must not|prohibited|forbidden|not allowed|warning|caution|disciplinary|misconduct)\b|لا ت|ممنوع|تحذير", re.I)),
    ("definition", re.compile(r"^\s*[-*]?\s*\**[A-Z][\w ()/-]{1,40}\**\s*[:\-–]\s+\S|\b(means|is defined as|refers to)\b|يقصد ب|تعريف", re.I)),
    ("statistic", re.compile(r"\d+(?:\.\d+)?\s?(?:%|percent|per cent)|\baverage\b|\bon average\b|\bmedian\b", re.I)),
    ("policy", re.compile(r"\b(must|shall|required|is required|are required|mandatory|are not reimbursed|is capped|applies to)\b|يجب|لازم|إلزامي", re.I)),
]


def candidates_for_chunk(text: str) -> list[dict]:
    out, order, in_proc = [], 0, False
    lines = [ln.strip() for ln in text.splitlines()]
    heading = ""
    for ln in lines:
        if not ln:
            continue
        hm = re.match(r"^#{1,4}\s+(.*)", ln)
        if hm or (len(ln.split()) <= 8 and re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", ln) and not ln.endswith(".")):
            heading = hm.group(1) if hm else ln
            in_proc = bool(re.search(r"procedure|steps|how to|process|submitting|خطوات|إجراء", heading, re.I))
            order = 0
            continue
        item = re.match(r"^(?:[-*•]|\d+[.)]|step \d+[:.]?)\s+(.*)$", ln, re.I)
        txt = re.sub(r"\*\*", "", item.group(1) if item else ln).strip()
        if len(txt.split()) < 4 or META_LINE.match(txt):
            continue
        if not item and len(txt.split()) <= 8 and not re.search(r"[.!?؟]$", txt):
            continue  # title / heading-like line
        for sent in ([txt] if item else [s for s in sent_split(txt) if len(s.split()) >= 4]):
            kind = None
            if item and in_proc:
                order += 1
                kind = "step"
            else:
                for k, rx in RULES:
                    if rx.search(sent):
                        kind = k
                        break
            if not kind and NUM_RE.search(sent) and re.search(r"\d", sent):
                kind = "fact"
            if not kind:
                continue
            c = {"kind": kind, "text": sent[:400], "heading": heading}
            if kind == "step":
                c["procedure_order"] = order
            dm = re.search(r"\b(19|20)\d{2}\b", sent)
            if dm:
                c["year"] = int(dm.group(0))
            out.append(c)
    return out


# --------------------------------------------------------------------------- conflicts / outdated
STOP = set("a an the of to for and or in on at by with is are be been was were this that these those it its as from "
           "any every all each per must shall can may will should not no than more less up into after before "
           "within over under your their our employee employees company".split())


SYN = {"keep": "retain", "kept": "retain", "store": "retain", "stored": "retain", "retention": "retain",
       "hold": "retain", "reimburse": "pay", "reimbursed": "pay", "refund": "pay", "submit": "file",
       "submitted": "file", "file": "file", "claim": "claim", "staff": "employee", "worker": "employee"}
UNIT_WORDS = {"year", "years", "day", "days", "month", "months", "hour", "hours", "night", "nights", "week",
              "weeks", "minute", "minutes", "percent", "business"}


def content_tokens(t: str) -> set[str]:
    toks = re.findall(r"[^\W\d_]+", t.lower())
    out = set()
    for w in toks:
        if w in STOP or len(w) < 3 or w in UNIT_WORDS:
            continue
        w = SYN.get(w, w)
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[: -len(suf)]
                break
        out.add(w)
    return out


def numbers_in(t: str) -> set[str]:
    t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", t)}


def units_in(t: str) -> set[str]:
    u = set()
    for m in re.finditer(r"([$€£]|EGP|USD)?\s?\d[\d,.]*\s?(%|percent|years?|days?|months?|hours?|nights?|weeks?)?", t, re.I):
        if m.group(1):
            u.add("money")
        if m.group(2):
            u.add(m.group(2).lower().rstrip("s").replace("percent", "%"))
    return u


YEARS = {str(y) for y in range(1990, 2100)}


def detect_conflicts(facts: list[dict], existing: list[dict] | None = None, max_total: int = 60) -> list[dict]:
    """Pairs of facts from different chunks: same topic words, different numbers. O(n^2) on numeric facts only."""
    known = {tuple(sorted(c.get("fact_ids", []))) for c in (existing or [])}
    prepped = []
    for f in facts:
        n = numbers_in(f["text"]) - YEARS
        t = content_tokens(f["text"])
        if n and t:
            prepped.append((f, n, t, units_in(f["text"])))
    out, per = [], {}
    for i, (a, na, ta, ua) in enumerate(prepped):
        if len(out) >= max_total:
            break
        for b, nb, tb, ub in prepped[i + 1:]:
            if per.get(a["id"], 0) >= 2 or len(out) >= max_total:
                break
            if na == nb or (a.get("source_id") == b.get("source_id") and a.get("chunk_id") == b.get("chunk_id")):
                continue
            shared = ta & tb
            if len(shared) < 2:
                continue
            overlap = len(shared) / min(len(ta), len(tb))
            if (overlap >= 0.45 and len(shared) >= 3) or (ua & ub and overlap >= 0.3):
                key = tuple(sorted([a["id"], b["id"]]))
                if key in known:
                    continue
                known.add(key)
                per[a["id"]] = per.get(a["id"], 0) + 1
                out.append({"fact_ids": list(key),
                            "note": f"[auto] same topic ({', '.join(sorted(shared)[:5])}) but different numbers: "
                                    f"{a['id']}={sorted(na)} vs {b['id']}={sorted(nb)}",
                            "resolution": "unresolved"})
    return out


def outdated_sources(sources: list[dict], today: dt.date, max_age_years: float) -> list[tuple[str, str, float]]:
    res = []
    for s in sources:
        d = s.get("date")
        try:
            dd = dt.date.fromisoformat(d[:10]) if d else None
        except ValueError:
            dd = None
        if dd:
            age = (today - dd).days / 365.25
            if age > max_age_years:
                res.append((s["id"], d, round(age, 1)))
    return res


# --------------------------------------------------------------------------- main
def classify(arg: str) -> str:
    if re.match(r"^https?://", arg):
        if re.search(r"(youtube\.com|youtu\.be|vimeo\.com)", arg):
            return "online-video"
        return "url"
    if re.match(r"^[A-Za-z][\w-]*:(?!//)", arg) and not Path(arg).exists() and not re.match(r"^[A-Za-z]:\\", arg):
        return "remote"
    return "path"


def expand_paths(p: Path) -> list[Path]:
    if p.is_dir():
        return sorted(f for f in p.rglob("*") if f.is_file() and f.name not in SKIP_NAMES
                      and not f.name.startswith(".") and f.suffix.lower() in {**DOC_EXT, **AV_EXT, **IMG_EXT})
    return [p]


def load_path(p: Path) -> Loaded:
    ext = p.suffix.lower()
    if ext in AV_EXT:
        return load_av_file(p, AV_EXT[ext])
    if ext in IMG_EXT:
        return Loaded("image", p.stem, str(p), [], note="image: describe it in the LLM step (no OCR here)")
    typ = DOC_EXT.get(ext, "text")
    return {"pdf": load_pdf, "docx": load_docx, "pptx": load_pptx, "xlsx": load_xlsx, "markdown": load_markdown,
            "html": load_html}.get(typ, load_text)(p)


def rel(p: Path, base: Path) -> str:
    try:
        return str(p.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(p)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*")
    ap.add_argument("--out", required=True)
    ap.add_argument("--paste", action="append", default=[], help="file with pasted text, or - for stdin")
    ap.add_argument("--text", action="append", default=[], help="pasted text inline")
    ap.add_argument("--title", help="title for pasted text")
    ap.add_argument("--append", action="store_true", help="add to an existing sources.yaml")
    ap.add_argument("--course-id")
    ap.add_argument("--language", choices=["en-US", "en-GB", "ar-EG", "ar-MSA"])
    ap.add_argument("--authority", type=int, choices=range(1, 6))
    ap.add_argument("--no-seed-facts", action="store_true")
    ap.add_argument("--max-age-years", type=float, default=3.0)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--uri-prefix", help="replace local folder prefix in uri, e.g. 'gdrive:Policies'")
    a = ap.parse_args(argv)

    out = Path(a.out)
    run = out.parent
    cache = run / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": "1.0", "sources": [], "facts": []}
    if a.append and out.exists():
        data = yaml.safe_load(out.read_text(encoding="utf-8")) or data
    if a.course_id:
        data["course_id"] = a.course_id
    data.setdefault("general_knowledge_allowed", True)
    data.setdefault("conflicts", [])
    hashes = {}
    for s in data["sources"]:
        hp = cache / s["id"] / "_sha1"
        if hp.exists():
            hashes[hp.read_text().strip()] = s["id"]
    next_s = max([int(s["id"][1:]) for s in data["sources"]] + [0]) + 1
    next_f = max([int(f["id"][1:]) for f in data["facts"]] + [0]) + 1

    report, skipped, loaded = [], [], []
    jobs: list[tuple[str, object]] = []
    for arg in a.inputs:
        kind = classify(arg)
        if kind == "path":
            p = Path(arg).expanduser()
            if not p.exists():
                skipped.append(f"{arg}: not found")
                continue
            jobs += [("path", f) for f in expand_paths(p)]
        else:
            jobs.append((kind, arg))
    for f in a.paste:
        jobs.append(("pasted", sys.stdin.read() if f == "-" else Path(f).read_text(encoding="utf-8")))
    for t in a.text:
        jobs.append(("pasted", t))

    for kind, obj in jobs:
        try:
            if kind == "remote":
                skipped.append(rclone_instructions(str(obj)))
                continue
            if kind == "path":
                ld = load_path(obj)
                if a.uri_prefix and a.inputs:
                    base = Path(a.inputs[0]).expanduser()
                    if base.is_dir():
                        ld.uri = f"{a.uri_prefix.rstrip('/')}/{rel(Path(obj), base)}"
            elif kind == "url":
                ld = load_url(obj)
            elif kind == "online-video":
                ld = load_online_video(obj, cache)
            else:
                ld = load_text(None, "pasted", obj, a.title or "Pasted text")
            loaded.append(ld)
        except Exception as e:  # keep going; report
            skipped.append(f"{obj if kind != 'pasted' else 'pasted text'}: {type(e).__name__}: {e}")

    all_new_facts, cand_dump = [], {}
    for ld in loaded:
        full = "\n\n".join(s.text for s in ld.segments)
        sha = hashlib.sha1((full or ld.uri).encode()).hexdigest()
        if sha in hashes:
            report.append(f"- duplicate of {hashes[sha]}: {ld.uri} (skipped)")
            continue
        sid = f"S{next_s:02d}"
        next_s += 1
        hashes[sha] = sid
        sdir = cache / sid
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "_sha1").write_text(sha)
        chunks = chunk_segments(ld.segments) if ld.segments else []
        src = {"id": sid, "type": ld.type, "uri": ld.uri, "title": ld.title,
               "retrieved_at": dt.datetime.now().replace(microsecond=0).isoformat(),
               "language": a.language or detect_lang(full or ld.title)}
        if ld.owner:
            src["owner"] = ld.owner
        if ld.date:
            src["date"] = ld.date
        if a.authority:
            src["authority"] = a.authority
        if ld.pages_or_duration:
            src["pages_or_duration"] = ld.pages_or_duration
        src["chunks"] = []
        for c in chunks:
            cpath = sdir / f"{c['id']}.md"
            cpath.write_text(f"<!-- {sid}#{c['id']} · {c['loc']} · {ld.title} -->\n\n{c['text']}\n", encoding="utf-8")
            src["chunks"].append({"id": c["id"], "loc": c["loc"], "summary": auto_summary(c["text"], c["headings"]),
                                  "tokens": c["tokens"], "path": rel(cpath, run)})
            cands = candidates_for_chunk(c["text"])
            cand_dump[f"{sid}#{c['id']}"] = cands
            if not a.no_seed_facts:
                for cd in cands:
                    fact = {"id": f"F{next_f:03d}", "kind": cd["kind"], "text": cd["text"], "source_id": sid,
                            "chunk_id": c["id"], "loc": c["loc"], "confidence": 0.4, "tags": ["auto-candidate"]}
                    if cd.get("procedure_order"):
                        fact["procedure_order"] = cd["procedure_order"]
                    if ld.date:
                        fact["date"] = ld.date
                    if cd.get("heading"):
                        fact["tags"].append("h:" + cd["heading"][:60])
                    next_f += 1
                    all_new_facts.append(fact)
        if not chunks:
            src["chunks"] = [{"id": "c1", "loc": "whole", "summary": f"[auto] {ld.note or 'no extractable text'}"}]
        data["sources"].append(src)
        report.append(f"- {sid} {ld.type} `{ld.title}` · {len(chunks)} chunks · date {ld.date or '?'} · "
                      f"lang {src['language']}{' · ' + ld.note if ld.note else ''}")

    data["facts"].extend(all_new_facts)
    data["conflicts"] = data.get("conflicts", []) + detect_conflicts(data["facts"], data.get("conflicts"))
    if not data["conflicts"]:
        data.pop("conflicts")
    old = outdated_sources(data["sources"], dt.date.fromisoformat(a.today), a.max_age_years)
    for sid, d, age in old:
        for f in data["facts"]:
            if f["source_id"] == sid and "outdated?" not in f.setdefault("tags", []):
                f["tags"].append("outdated?")

    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    (cache / "candidates.yaml").write_text(yaml.safe_dump(cand_dump, allow_unicode=True, sort_keys=False),
                                           encoding="utf-8")
    lines = [f"# Ingest report ({a.today})", "", "## Sources", *report]
    if old:
        lines += ["", f"## Possibly outdated (> {a.max_age_years:g} years)"] + [f"- {s}: dated {d} ({g} y)" for s, d, g in old]
    if data.get("conflicts"):
        lines += ["", "## Conflicts to resolve"] + [f"- {c['fact_ids']}: {c['note']}" for c in data["conflicts"]
                                                     if c.get("resolution") in (None, "unresolved")]
    if skipped:
        lines += ["", "## Skipped / needs action"] + [f"- {s}" for s in skipped]
    lines += ["", f"Facts: {len(data['facts'])} ({len(all_new_facts)} new auto-candidates). "
                  "Next: LLM pass per chunk (templates/chunk_extract_prompt.md) → merge_facts.py."]
    (cache / "ingest_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if not loaded and not a.append:
        return 1
    return 3 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
