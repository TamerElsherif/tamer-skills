# Render commands — golden example 1 (run from the plugin root)

Keys: `export TCS_ENV_FILE=/path/to/.env` (OPENAI_API_KEY for TTS + word timing). Nothing else is required.

```bash
R=examples/golden-security-microdrama
L=$R/lessons/M1L1

# Sources
.venv/bin/python skills/tcs-source-ingest/scripts/ingest.py $R/sources/northwind-payment-verification-policy.md \
    --out $R/sources.yaml --course-id northwind-bec-microdrama --authority 5
.venv/bin/python skills/tcs-source-ingest/scripts/merge_facts.py $R/sources.yaml --batch $R/cache/extract-01.yaml
.venv/bin/python skills/tcs-source-ingest/scripts/validate_sources.py $R/sources.yaml

# Plan + gate
.venv/bin/python skills/tcs-curriculum/scripts/validate_curriculum.py $R/curriculum.yaml

# Script -> storyboard -> quiz -> grounding
.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py check $L/M1L1.script.md
.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py to-storyboard $L/M1L1.script.md --out $L/M1L1.storyboard.json  # then fill props (tcs-storyboard)
.venv/bin/python skills/tcs-storyboard/scripts/derive_text.py $L/M1L1.storyboard.json --force
.venv/bin/python skills/tcs-storyboard/scripts/validate_storyboard.py $L/M1L1.storyboard.json --stage final --quiz $L/M1L1.quiz.json --target-min 1.5
.venv/bin/python skills/tcs-storyboard/scripts/preview.py $L/M1L1.storyboard.json --out $L/M1L1.preview.md
.venv/bin/python skills/tcs-assessment/scripts/validate_quiz.py $L/M1L1.quiz.json --curriculum $R/curriculum.yaml --sources $R/sources.yaml
.venv/bin/python skills/tcs-grounding-check/scripts/check.py --sources $R/sources.yaml --storyboard $L/M1L1.storyboard.json \
    --quiz $L/M1L1.quiz.json --curriculum $R/curriculum.yaml --lesson-id M1L1 --out $L/M1L1.grounding_report.json

# QA gate -> qa/M1L1.qa.json (then re-apply the LLM verification verdicts)
.venv/bin/python tools/qa.py $R
.venv/bin/python skills/tcs-grounding-check/scripts/apply_verdicts.py $L/M1L1.grounding_report.json $L/M1L1.verdicts.yaml

# Video (standalone Remotion kit) -> renders/M1L1/video/M1L1_16x9.mp4 (+ .grid.jpg)
.venv/bin/python skills/tcs-render-remotion/scripts/prepare.py $L/M1L1.storyboard.json --quiz $L/M1L1.quiz.json --out $R/renders/M1L1/video/work
.venv/bin/python skills/tcs-render-remotion/scripts/stills.py $R/renders/M1L1/video/work          # look at qa/stills_16x9/sheet.jpg
.venv/bin/python skills/tcs-render-remotion/scripts/render_lesson.py $R --lesson M1L1 --target video

# Alternative (not run): render through an OpenMontage install (set OPENMONTAGE_ROOT first)
.venv/bin/python skills/tcs-render-remotion/scripts/render_lesson.py $R --lesson M1L1 --target video --engine openmontage

# HTML lesson + SCORM 1.2
.venv/bin/python skills/tcs-render-lesson/scripts/html_lesson.py $R --lesson M1L1
.venv/bin/python skills/tcs-render-lesson/scripts/scorm.py --run $R
.venv/bin/python skills/tcs-render-lesson/scripts/scorm_check.py $R/renders/course/scorm/northwind-bec-microdrama-scorm12.zip

# Report
.venv/bin/python skills/tcs-autopilot/scripts/report.py $R
```
