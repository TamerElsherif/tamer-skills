# Render commands (run from the plugin root; run folder = examples/golden-sop-deck-jobaid)

```bash
R=examples/golden-sop-deck-jobaid
export TCS_ENV_FILE=/path/to/.env      # OPENAI_API_KEY for TTS + whisper cue timing (never copied into run files)

# 0. run + sources
.venv/bin/python skills/tcs-autopilot/scripts/run_state.py init $R --request "Narrated deck + job aid from the Northwind Co. expense SOP for new employees (EN + Egyptian Arabic)"
.venv/bin/python skills/tcs-source-ingest/scripts/ingest.py examples/_shared/sop/expenses.pdf --out $R/sources.yaml --course-id northwind-expenses --authority 5
.venv/bin/python skills/tcs-source-ingest/scripts/merge_facts.py $R/sources.yaml --batch $R/cache/extract-01.yaml   # LLM chunk pass
.venv/bin/python skills/tcs-source-ingest/scripts/merge_facts.py $R/sources.yaml --batch $R/cache/extract-02.yaml   # metadata fact
.venv/bin/python skills/tcs-source-ingest/scripts/validate_sources.py $R/sources.yaml

# 1. intake proposal (then overridden by intake.md answers) + plan
.venv/bin/python skills/tcs-autopilot/scripts/decide.py "Create a narrated deck and a one-page job aid from our expense SOP for new employees (beginners), English with an Egyptian Arabic version of the deck" \
  --sources examples/_shared/sop/expenses.pdf --lang both --targets video,deck,lesson,scorm,jobaid --aspect 16:9 \
  --review skeleton --domain _template --renderer remotion --sources-summary $R/sources.yaml --out $R
.venv/bin/python skills/tcs-curriculum/scripts/validate_curriculum.py $R/curriculum.yaml --sources $R/sources.yaml

# 2. M1L1 script -> storyboard -> quiz -> grounding
L=$R/lessons/M1L1
.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py budget --minutes 3 --level beginner --lang en-US
.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py check $L/M1L1.script.md
.venv/bin/python skills/tcs-scriptwriter/scripts/script_md.py to-storyboard $L/M1L1.script.md --out $L/M1L1.storyboard.json
#   (tcs-storyboard: templates + props filled, then)
.venv/bin/python skills/tcs-storyboard/scripts/derive_text.py $L/M1L1.storyboard.json --force
.venv/bin/python skills/tcs-storyboard/scripts/validate_storyboard.py $L/M1L1.storyboard.json --stage final --quiz $L/M1L1.quiz.json --target-min 3
.venv/bin/python skills/tcs-storyboard/scripts/preview.py $L/M1L1.storyboard.json --out $L/M1L1.preview.md
.venv/bin/python skills/tcs-assessment/scripts/validate_quiz.py $L/M1L1.quiz.json --curriculum $R/curriculum.yaml --sources $R/sources.yaml
.venv/bin/python skills/tcs-grounding-check/scripts/check.py --sources $R/sources.yaml --storyboard $L/M1L1.storyboard.json --quiz $L/M1L1.quiz.json --curriculum $R/curriculum.yaml

# 3. ar-EG localization of M1L1
.venv/bin/python skills/tcs-localize/scripts/localize.py skeleton $L/M1L1.storyboard.json --lang ar-EG --numerals western
#   (fill tr: in M1L1.ar-EG.translate.yaml — Egyptian colloquial adaptation)
.venv/bin/python skills/tcs-localize/scripts/localize.py apply $L/M1L1.ar-EG.storyboard.json $L/M1L1.ar-EG.translate.yaml
.venv/bin/python skills/tcs-localize/scripts/rtl_lint.py $L/M1L1.ar-EG.storyboard.json --source $L/M1L1.storyboard.json

# 4. QA gate (writes qa/*.qa.json + grounding reports)
.venv/bin/python tools/qa.py $R
.venv/bin/python tools/qa.py $R --lang ar-EG --lesson M1L1

# 5. renders
.venv/bin/python skills/tcs-render-remotion/scripts/render_lesson.py $R --lesson M1L1 --target video     # MP4 16:9 + grid + timing.json
.venv/bin/python skills/tcs-render-lesson/scripts/deck.py $R --lesson M1L1                    # PPTX + deck.html
.venv/bin/python skills/tcs-render-lesson/scripts/deck.py $R --lesson M1L1 --lang ar-EG       # RTL PPTX + deck.html
.venv/bin/python skills/tcs-render-lesson/scripts/jobaid.py $R --lesson M1L2 --paper A4 --pages 1
.venv/bin/python skills/tcs-render-lesson/scripts/html_lesson.py $R --lesson M1L1
.venv/bin/python skills/tcs-render-lesson/scripts/html_lesson.py $R --lesson M1L2
.venv/bin/python skills/tcs-render-lesson/scripts/scorm.py --run $R
.venv/bin/python skills/tcs-render-lesson/scripts/scorm_check.py $R/renders/course/scorm/northwind-expenses-scorm12.zip
.venv/bin/python skills/tcs-localize/scripts/subtitles.py $L/M1L1.storyboard.json --timing $L/M1L1.timing.json
.venv/bin/python skills/tcs-localize/scripts/subtitles.py $L/M1L1.ar-EG.storyboard.json --timing $L/M1L1.timing.json

# 6. report
.venv/bin/python skills/tcs-autopilot/scripts/report.py $R
```
