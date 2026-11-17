#!/usr/bin/env bash
# Full test pass for tcs-render-lesson. Run from the plugin root: bash skills/tcs-render-lesson/tests/run_all.sh
# Outputs go to runs/tcs-test/ (gitignored).
set -euo pipefail
PY=.venv/bin/python; S=skills/tcs-render-lesson/scripts; T=skills/tcs-render-lesson/tests; F=$T/fixtures; O=runs/tcs-test
$PY $S/html_lesson.py $F/en.storyboard.json --quiz $F/en.quiz.json --out $O/lessons/en
$PY $S/html_lesson.py $F/ar.storyboard.json --out $O/lessons/ar
$PY $S/html_lesson.py $F/gallery.storyboard.json --out $O/lessons/gallery
$PY $S/deck.py $F/en.storyboard.json --quiz $F/en.quiz.json --out $O/deck/en
$PY $S/deck.py $F/ar.storyboard.json --out $O/deck/ar
$PY $S/jobaid.py $F/en.storyboard.json --out $O/jobaid/en-a4.pdf
$PY $S/jobaid.py $F/en.storyboard.json --out $O/jobaid/en-letter.pdf --paper Letter
$PY $S/jobaid.py $F/jobaid.ar.yaml --out $O/jobaid/ar.pdf
$PY $S/scorm.py --lesson-dir $O/lessons --curriculum $F/curriculum.yaml --quiz $F/en.quiz.json --out $O/security-basics-scorm12.zip
$PY $S/scorm_check.py $O/security-basics-scorm12.zip
$PY $T/test_runtime.py $O/security-basics-scorm12.zip
$PY $T/test_sim.py $O/lessons/gallery --scene scast_assess
$PY $T/check_pptx.py $O/deck/en/M1L1.pptx $O/deck/ar/M1L2.pptx
for f in skills/tcs-format-*/templates/example*.storyboard.json; do   # format-skill examples (agent E)
  n=$(basename "$(dirname "$(dirname "$f")")")$(basename "$f" .storyboard.json | sed 's/example//')
  $PY $S/html_lesson.py "$f" --out $O/fmt/$n >/dev/null && $PY $S/deck.py "$f" --out $O/fmtdeck/$n --no-html >/dev/null && echo "ok  $n"
done
# visual QA: $PY $T/shoot.py $O/lessons/en/index.html --out $O/shots/en --query reveal=1 && $PY $T/contact_sheet.py $O/shots/en --out $O/sheets/en.png
echo "ALL TESTS PASSED"
