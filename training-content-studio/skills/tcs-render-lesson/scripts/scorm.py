#!/usr/bin/env python3
"""Package rendered HTML lessons as a SCORM 1.2 zip (one SCO per lesson, organised by curriculum modules).

Usage:
  .venv/bin/python skills/tcs-render-lesson/scripts/scorm.py --lesson-dir <dir> [--lesson-dir <dir> ...]
        --curriculum curriculum.yaml [--quiz <lesson>.quiz.json ...] --out course.zip [--title "..."] [--lang ar-EG]

--lesson-dir may point at one rendered lesson (contains lesson.json from html_lesson.py) or at a parent folder
whose sub-folders are rendered lessons. Lessons are matched to curriculum lessons by lesson_id (M1L1 …).
--quiz files only override the mastery score (pass_mark) per lesson; scoring itself is inside the lesson.
Then run scorm_check.py on the zip.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import TEMPLATES, load_data, load_validated, render_pending  # noqa: E402

LMS_MARKER = "<!--TCS_LMS-->"
SHARED_JS = "shared/scorm12.js"


def xml_id(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]", "-", s)
    return s if re.match(r"[A-Za-z_]", s) else f"id-{s}"


def find_lessons(dirs: list[Path]) -> dict[str, Path]:
    found = {}
    for d in dirs:
        cands = [d] if (d / "lesson.json").exists() else sorted(p.parent for p in d.glob("*/lesson.json"))
        if not cands:
            sys.exit(f"error: no lesson.json under {d} (render it with html_lesson.py first)")
        for c in cands:
            meta = json.loads((c / "lesson.json").read_text(encoding="utf-8"))
            if meta["lesson_id"] in found:
                sys.exit(f"error: duplicate lesson_id {meta['lesson_id']} in {c} and {found[meta['lesson_id']]}")
            found[meta["lesson_id"]] = c
    return found


def build(lesson_dirs, curriculum_path, quizzes, out_zip: Path, title=None, lang=None) -> Path:
    cur = load_validated(curriculum_path, "curriculum")
    lessons = find_lessons(lesson_dirs)
    pass_override = {}
    for q in quizzes or []:
        qd = load_validated(q, "quiz")
        if qd.get("lesson_id"):
            pass_override[qd["lesson_id"]] = qd.get("pass_mark", 80)
    course = cur["course"]
    lang = lang or course["languages"]["primary"]
    ar = lang.startswith("ar")
    pick = lambda o: (o.get("title_ar") if ar and o.get("title_ar") else o["title"])
    ctitle = title or pick(course)

    stage = Path(tempfile.mkdtemp(prefix="tcs-scorm-"))
    try:
        (stage / "shared").mkdir()
        shutil.copy2(TEMPLATES / "scorm12.js", stage / SHARED_JS)
        org_items, resources, used = [], [], set()

        def sco(lid, cur_lesson):
            src = lessons[lid]
            meta = json.loads((src / "lesson.json").read_text(encoding="utf-8"))
            dst = stage / lid
            shutil.copytree(src, dst)
            idx = dst / meta.get("entry", "index.html")
            html = idx.read_text(encoding="utf-8")
            if LMS_MARKER not in html:
                sys.exit(f"error: {idx} has no {LMS_MARKER} marker (re-render with html_lesson.py)")
            idx.write_text(html.replace(LMS_MARKER, f'<script src="../{SHARED_JS}"></script>'), encoding="utf-8")
            files = sorted(p.relative_to(stage).as_posix() for p in dst.rglob("*") if p.is_file())
            rid = xml_id(f"res-{lid}")
            file_xml = "".join(f'\n      <file href={quoteattr(f)}/>' for f in files)
            resources.append(
                f'    <resource identifier="{rid}" type="webcontent" adlcp:scormtype="sco" href={quoteattr(f"{lid}/{meta.get("entry", "index.html")}")}>'
                f'{file_xml}\n      <dependency identifierref="res-shared"/>\n    </resource>')
            mastery = ""
            if meta.get("has_quiz"):
                pm = int(round(pass_override.get(lid, meta.get("pass_mark", 80))))
                mastery = f"\n          <adlcp:masteryscore>{pm}</adlcp:masteryscore>"
            t = meta.get("title") or (pick(cur_lesson) if cur_lesson else lid)
            used.add(lid)
            return (f'        <item identifier="{xml_id("item-" + lid)}" identifierref="{rid}" isvisible="true">\n'
                    f'          <title>{escape(t)}</title>{mastery}\n        </item>')

        for m in cur["modules"]:
            kids = [sco(l["id"], l) for l in m["lessons"] if l["id"] in lessons]
            if kids:
                org_items.append(f'      <item identifier="{xml_id("mod-" + m["id"])}" isvisible="true">\n'
                                 f'        <title>{escape(pick(m))}</title>\n' + "\n".join(kids) + "\n      </item>")
        extra = [lid for lid in lessons if lid not in used]
        if extra:
            print("warning: lessons not in curriculum, appended at the end:", ", ".join(extra), file=sys.stderr)
            org_items.append("\n".join(sco(lid, None) for lid in extra))
        if not used:
            sys.exit("error: none of the rendered lessons match curriculum lesson ids")
        manifest = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{xml_id('tcs-' + course['id'])}" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="org-1">
    <organization identifier="org-1">
      <title>{escape(ctitle)}</title>
{chr(10).join(org_items)}
    </organization>
  </organizations>
  <resources>
{chr(10).join(resources)}
    <resource identifier="res-shared" type="webcontent" adlcp:scormtype="asset">
      <file href="{SHARED_JS}"/>
    </resource>
  </resources>
</manifest>
"""
        (stage / "imsmanifest.xml").write_text(manifest, encoding="utf-8")
        out_zip.parent.mkdir(parents=True, exist_ok=True)
        if out_zip.exists():
            out_zip.unlink()
        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(stage / "imsmanifest.xml", "imsmanifest.xml")
            for p in sorted(stage.rglob("*")):
                if p.is_file() and p.name != "imsmanifest.xml":
                    z.write(p, p.relative_to(stage).as_posix())
        stale = out_zip.parent / "RENDER_PENDING.md"
        if stale.exists():
            stale.unlink()
        print(f"scorm: {out_zip}  scos={len(used)} ({', '.join(sorted(used))})")
        return out_zip
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, help="run folder: lessons from renders/*/lesson, curriculum.yaml, "
                                             "out renders/course/scorm/<course>-scorm12.zip")
    ap.add_argument("--lesson-dir", type=Path, action="append")
    ap.add_argument("--curriculum", type=Path)
    ap.add_argument("--quiz", type=Path, action="append")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--title")
    ap.add_argument("--lang", help="language for course/module titles (default: curriculum primary)")
    a = ap.parse_args()
    if a.run:
        a.curriculum = a.curriculum or a.run / "curriculum.yaml"
        a.lesson_dir = a.lesson_dir or sorted(p.parent for p in (a.run / "renders").glob("*/lesson/lesson.json"))
        a.quiz = a.quiz or sorted((a.run / "lessons").glob("*/*.quiz.json"))
        if not a.out:
            cid = load_data(a.curriculum)["course"]["id"]
            a.out = a.run / "renders" / "course" / "scorm" / f"{cid}-scorm12.zip"
        if not a.lesson_dir:
            render_pending(a.run / "renders" / "course" / "scorm", "no rendered HTML lessons (renders/<L>/lesson/) yet",
                           [f".venv/bin/python skills/tcs-render-lesson/scripts/html_lesson.py {a.run}",
                            f".venv/bin/python skills/tcs-render-lesson/scripts/scorm.py --run {a.run}"])
            return
    if not (a.lesson_dir and a.curriculum and a.out):
        ap.error("give --run <run dir> or --lesson-dir + --curriculum + --out")
    build(a.lesson_dir, a.curriculum, a.quiz, a.out, a.title, a.lang)


if __name__ == "__main__":
    main()
