"""Shared helpers for tcs-render-lesson scripts: paths, validation, theme, i18n, icons, personas.

Run scripts with the plugin venv: `.venv/bin/python skills/tcs-render-lesson/scripts/<name>.py ...`
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = SKILL_DIR.parent.parent
SCHEMAS = PLUGIN_ROOT / "schemas"
TEMPLATES = SKILL_DIR / "templates"
ASSETS = PLUGIN_ROOT / "assets"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500;600"
    "&family=Cairo:wght@400;600;700&family=IBM+Plex+Sans+Arabic:wght@400;600"
    "&family=IBM+Plex+Mono:wght@400;600&family=Caveat:wght@500;700&display=swap"
)

# ---------------------------------------------------------------- loading + validation

def load_data(path: str | Path):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in (".yaml", ".yml"):
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)


def validate(data, schema_name: str, label: str = "", schema_path: Path | None = None) -> list[str]:
    """Validate against schemas/<schema_name>.schema.json (Draft 2020-12). Returns error strings."""
    from jsonschema import Draft202012Validator
    sp = schema_path or (SCHEMAS / f"{schema_name}.schema.json")
    schema = json.loads(sp.read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    errs = []
    for e in sorted(v.iter_errors(data), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(x) for x in e.absolute_path) or "(root)"
        errs.append(f"{label or schema_name}: {loc}: {e.message[:300]}")
    return errs


def load_validated(path, schema_name, schema_path=None, strict=True):
    data = load_data(path)
    errs = validate(data, schema_name, Path(path).name, schema_path)
    if errs:
        for e in errs[:40]:
            print("SCHEMA ERROR", e, file=sys.stderr)
        if strict:
            sys.exit(f"{path}: {len(errs)} schema error(s); fix the file or pass --no-strict")
    return data


def die(msg: str):
    sys.exit(f"error: {msg}")

# ---------------------------------------------------------------- language

def is_rtl(doc: dict) -> bool:
    if doc.get("direction"):
        return doc["direction"] == "rtl"
    return str(doc.get("language", "")).startswith("ar")


def html_lang(code: str) -> str:
    return {"en-US": "en-US", "en-GB": "en-GB", "ar-EG": "ar-EG", "ar-MSA": "ar"}.get(code, code or "en")


UI = {
    "en": {
        "next": "Next", "back": "Back", "start": "Start", "restart": "Restart", "of": "of",
        "transcript": "Transcript", "show_transcript": "Show transcript", "scene": "Scene",
        "check": "Check answer", "correct": "Correct", "incorrect": "Not quite", "try_again": "Try again",
        "continue": "Continue", "reveal": "Reveal next", "reveal_all": "Show all", "flip": "Flip card",
        "score": "Score", "pass": "Passed", "fail": "Not passed yet", "pass_mark": "Pass mark",
        "final_check": "Knowledge check", "results": "Your results", "dont": "Don't", "do": "Do",
        "skip": "Skip to lesson content", "step": "Step", "next_step": "Next step", "done": "Done",
        "red_flags": "Show red flags", "your_choice": "Your choice", "outcome": "Outcome",
        "choose": "Choose one", "order_hint": "Set the position of each item", "match_hint": "Pick the matching item",
        "position": "Position", "select": "Select…", "complete": "Lesson complete", "progress": "Progress",
        "audio": "Narration audio", "notes": "Speaker notes", "image_missing": "Visual placeholder",
        "menu": "Lesson menu", "jump": "Go to scene", "print": "Print", "branch_restart": "Replay scenario",
        "true": "True", "false": "False", "front": "Front", "back_side": "Back", "answered": "answered", "sim_wrong": "Not that step.", "sim_done": "Task complete.", "sim_fail": "Out of attempts — review the demo and try again.",
    },
    "ar": {
        "next": "التالي", "back": "السابق", "start": "ابدأ", "restart": "ابدأ من جديد", "of": "من",
        "transcript": "النص المكتوب", "show_transcript": "اعرض النص", "scene": "مشهد",
        "check": "تحقّق من الإجابة", "correct": "إجابة صحيحة", "incorrect": "ليست صحيحة تمامًا", "try_again": "حاول مرة أخرى",
        "continue": "متابعة", "reveal": "اكشف التالي", "reveal_all": "اعرض الكل", "flip": "اقلب البطاقة",
        "score": "الدرجة", "pass": "ناجح", "fail": "لم تنجح بعد", "pass_mark": "درجة النجاح",
        "final_check": "اختبار المعرفة", "results": "نتيجتك", "dont": "لا تفعل", "do": "افعل",
        "skip": "انتقل إلى محتوى الدرس", "step": "خطوة", "next_step": "الخطوة التالية", "done": "تم",
        "red_flags": "اعرض العلامات التحذيرية", "your_choice": "اختيارك", "outcome": "النتيجة",
        "choose": "اختر إجابة واحدة", "order_hint": "حدّد ترتيب كل عنصر", "match_hint": "اختر العنصر المطابق",
        "position": "الترتيب", "select": "اختر…", "complete": "اكتمل الدرس", "progress": "التقدّم",
        "audio": "التعليق الصوتي", "notes": "ملاحظات المتحدث", "image_missing": "مكان الصورة",
        "menu": "قائمة الدرس", "jump": "اذهب إلى المشهد", "print": "طباعة", "branch_restart": "أعد السيناريو",
        "true": "صح", "false": "خطأ", "front": "الوجه", "back_side": "الظهر", "answered": "تمت الإجابة", "sim_wrong": "مش دي الخطوة.", "sim_done": "تمّت المهمة.", "sim_fail": "خلصت المحاولات — راجع العرض وحاول تاني.",
    },
}


def ui(doc: dict) -> dict:
    return UI["ar" if is_rtl(doc) else "en"]

# ---------------------------------------------------------------- theme

DEFAULT_COLORS = {
    "navy": "#363E77", "blue": "#006AB3", "cyan": "#6FC7DA", "attention": "#FF6700",
    "bg": "#F4F7FB", "card": "#FFFFFF", "ink": "#1B2140", "muted": "#5B6385",
    "safe": "#1E9E6A", "line": "#D7DEEA",
}
ALIASES = {"primary": "navy", "secondary": "blue", "accent": "blue", "accent2": "cyan", "orange": "attention",
           "warn": "attention", "danger": "attention", "background": "bg", "text": "ink", "green": "safe",
           "surface": "card", "border": "line"}
DEFAULT_FONTS = {"latin": "Poppins", "body": "Inter", "arabic": "Cairo", "mono": "IBM Plex Mono", "hand": "Caveat"}


PRESET_MAP = {"surface": "card", "accent": "blue", "accent_2": "cyan", "attention_text": "attention_text",
              "ink_strong": "ink_strong"}


def load_presets() -> dict:
    p = ASSETS / "theme_presets.yaml"
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def theme(doc: dict) -> dict:
    """Resolve colours: defaults <- assets/theme_presets.yaml preset <- storyboard theme.colors."""
    t = doc.get("theme") or {}
    colors = dict(DEFAULT_COLORS)
    presets = load_presets()
    pre = (presets.get("presets") or {}).get(t.get("preset") or presets.get("default", "neutral"), {})
    for k, v in (pre.get("colors") or {}).items():
        colors[PRESET_MAP.get(k, ALIASES.get(k, k))] = v
    colors.setdefault("ink_strong", "#1E2350")
    colors.setdefault("attention_text", "#B34700")
    for k, v in (t.get("colors") or {}).items():
        colors[ALIASES.get(k, k)] = v
    fonts = dict(DEFAULT_FONTS)
    fonts.update({k: v for k, v in (t.get("fonts") or {}).items() if v})
    return {"colors": colors, "fonts": fonts, "logo": t.get("logo"), "evidence_line": t.get("evidence_line")}


def css_vars(th: dict, rtl: bool) -> str:
    c, f = th["colors"], th["fonts"]
    head = f"'{f['arabic']}', 'IBM Plex Sans Arabic', 'Noto Kufi Arabic', sans-serif" if rtl else f"'{f['latin']}', 'Inter', system-ui, sans-serif"
    body = f"'{f['arabic']}', 'IBM Plex Sans Arabic', 'Noto Kufi Arabic', sans-serif" if rtl else f"'{f['body']}', 'Inter', system-ui, sans-serif"
    lines = [f"--{k.replace('_', '-')}:{v};" for k, v in c.items()]
    lines += [f"--font-head:{head};", f"--font-body:{body};", f"--font-mono:'{f['mono']}', ui-monospace, monospace;",
              f"--font-hand:'{f['hand']}', 'Comic Sans MS', cursive;"]
    return ":root{" + "".join(lines) + "}"

# ---------------------------------------------------------------- text helpers

def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def strip_cues(s: str) -> str:
    return re.sub(r"\s*\^\s*", " ", s or "").strip()


def line_text(line: dict, rtl: bool) -> str:
    if rtl and line.get("text_ar"):
        return strip_cues(line["text_ar"])
    return strip_cues(line.get("text", ""))


def slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9-]+", "-", s).strip("-").lower() or "x"


_PERSONAS = None


def personas() -> dict:
    """Persona registry from assets/characters/personas.yaml + domains/*/personas.yaml (id -> dict)."""
    global _PERSONAS
    if _PERSONAS is None:
        _PERSONAS = {}
        try:
            import yaml
            files = [ASSETS / "characters" / "personas.yaml"] + sorted((PLUGIN_ROOT / "domains").glob("*/personas.yaml"))
            for f in files:
                if f.exists():
                    _PERSONAS.update((yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("personas") or {})
        except Exception:
            pass
    return _PERSONAS


def display_name(cast: str, rtl: bool) -> str:
    dn = (personas().get(cast) or {}).get("display_name") or {}
    return (dn.get("ar") if rtl else dn.get("en")) or dn.get("en") or (cast or "").replace("_", " ").title()


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


def chrome(args: list[str], timeout=120) -> subprocess.CompletedProcess | None:
    exe = find_chrome()
    if not exe:
        return None
    base = [exe, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
            "--hide-scrollbars", "--allow-file-access-from-files"]
    return subprocess.run(base + args, capture_output=True, text=True, timeout=timeout)


def audio_duration(path: Path) -> float | None:
    exe = shutil.which("ffprobe")
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
                           capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except Exception:
        return None


AUDIO_EXT = (".mp3", ".m4a", ".wav", ".ogg")


def find_scene_audio(audio_dir: Path | None, scene_id: str) -> Path | None:
    if not audio_dir or not audio_dir.is_dir():
        return None
    for ext in AUDIO_EXT:
        p = audio_dir / f"{scene_id}{ext}"
        if p.exists():
            return p
    return None

# ---------------------------------------------------------------- run-folder contract (skills/tcs-orchestrator/references/run-layout.md)

def lesson_inputs(arg: Path, lesson: str | None = None, lang: str | None = None, quiz: Path | None = None) -> list[dict]:
    """Accept a storyboard file OR a run dir (runs/<id>/ with lessons/<L>/<L>[.<lang>].storyboard.json).
    Returns [{lesson_id, storyboard, quiz, run_dir}]; quiz defaults to the sibling <L>[.<lang>].quiz.json."""
    arg = Path(arg)
    out = []
    if arg.is_file():
        name = arg.name.split(".storyboard.json")[0]
        lid = name.split(".")[0]
        q = quiz
        if q is None:
            for cand in (arg.with_name(f"{name}.quiz.json"), arg.with_name(f"{lid}.quiz.json")):
                if cand.exists() and cand != arg:
                    q = cand
                    break
        run_dir = arg.parent.parent.parent if arg.parent.parent.name == "lessons" else None
        out.append({"lesson_id": lid, "storyboard": arg, "quiz": q, "run_dir": run_dir})
        return out
    lessons_dir = arg / "lessons" if (arg / "lessons").is_dir() else None
    if not lessons_dir:
        die(f"{arg} is neither a storyboard file nor a run folder with lessons/")
    for d in sorted(p for p in lessons_dir.iterdir() if p.is_dir()):
        if lesson and d.name != lesson:
            continue
        sb = d / (f"{d.name}.{lang}.storyboard.json" if lang else f"{d.name}.storyboard.json")
        if not sb.exists():
            continue
        q = quiz
        if q is None:
            for cand in ((d / f"{d.name}.{lang}.quiz.json") if lang else None, d / f"{d.name}.quiz.json"):
                if cand and cand.exists():
                    q = cand
                    break
        out.append({"lesson_id": d.name, "storyboard": sb, "quiz": q, "run_dir": arg})
    if not out:
        die(f"no lessons/<L>/<L>{'.' + lang if lang else ''}.storyboard.json found under {arg}")
    return out


def default_out(item: dict, target: str, out: Path | None, lang: str | None = None, multi: bool = False) -> Path:
    if out and not multi:
        return Path(out)
    if out and multi:
        return Path(out) / item["lesson_id"]
    if item.get("run_dir"):
        base = Path(item["run_dir"]) / "renders" / item["lesson_id"] / target
        return base / lang if lang else base
    die("--out is required when the storyboard is not inside a run folder (runs/<id>/lessons/<L>/)")


def render_pending(folder: Path, reason: str, commands: list[str]) -> Path:
    """Write RENDER_PENDING.md (never fail the pipeline because a local dependency is missing)."""
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / "RENDER_PENDING.md"
    body = "\n".join(f"    {c}" for c in commands)
    p.write_text(f"# Render pending\n\nReason: {reason}\n\nWhen the dependency is available, run:\n\n{body}\n", encoding="utf-8")
    print(f"pending: {p} ({reason})")
    return p
