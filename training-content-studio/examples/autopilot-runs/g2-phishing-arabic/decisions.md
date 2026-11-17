# Decisions — g2-phishing-arabic

Request: توعية الموظفين بالتصيد الاحتيالي

| decision | value | signal | confidence | source | alternative rejected |
|---|---|---|---|---|---|
| language | {"primary": "ar-EG", "subtitles": ["en-US"]} | request written in Arabic script (100% of letters) | 0.90 | request | English primary |
| audience | {"id": "all-staff", "roles": ["learner"], "segment": "staff"} | wording 'الموظفين' | 0.70 | request | general staff |
| level | beginner-intermediate | mixed audience ('الموظفين'), jargon density 0.00 | 0.70 | rule | intermediate |
| other (objective_type) | behavior | behavior: 'توعية', 'التصيد', 'الاحتيال' | 0.95 | request | concept (default) |
| domain | security-awareness | pack keywords ['التصيد', 'الاحتيال'] | 0.90 | rule | workplace-behavior |
| domain_pack | security-awareness | matched 2 keyword(s) | 0.90 | rule | _template |
| objectives | O1: اكتشف علامات التصيد الاحتيالي في مواقف واقعية (analyze); O2: قرّر التصرف الأكثر أمانًا عند مواجهة التصيد الاحتيالي (evaluate); O3: أبلغ عن التصيد الاحتيالي المشتبه به عبر القناة الصحيحة (apply) | type=behavior (Bloom matched: know->remember/understand, do->apply, decide->analyze/evaluate); no sources/count wording -> default objective set for type | 0.55 | default | single broad objective |
| formats | ["cartoon", "branching"] | behavior -> ['cartoon', 'branching'] | 0.75 | rule | ['explainer'] (concept rule) |
| other (assessment) | {"assessment": "knowledge-check", "evidence": false, "broll": false} | assessment for behavior | 0.80 | rule | no assessment |
| blend | ["cartoon", "branching"] | primary cartoon + secondary branching (max 2/lesson, 3/course) | 0.80 | rule | single format |
| length | {"lessons": 3, "minutes_per_lesson": 5, "total_minutes": 15} | microlearning: 1 objective/lesson, 5 min for behavior (band 3-7), <= 6 lessons/module | 0.75 | rule | one long lesson |
| wpm | 126 | beginner-intermediate 140 wpm x0.9 Arabic | 0.80 | rule | 155 wpm |
| verbosity | standard | all-staff / beginner-intermediate | 0.70 | rule | detailed |
| targets | ["video", "lesson", "video-vertical", "scorm"] | cartoon->video; branching->lesson; video format -> + 9:16 nudge cut; 3 lessons -> + SCORM | 0.80 | rule | video only |
| aspect | ["16:9", "9:16"] | 16:9 master + 9:16 nudge cut | 0.80 | rule | 9:16 only |
| renderer | remotion | standalone kit (tcs-render-remotion); no OPENMONTAGE_ROOT | 0.60 | rule | openmontage |
| other (grounding) | general_knowledge | no --sources and no sources.yaml | 0.90 | default | grounded content |

Estimate: ~111,000 tokens, ~$1.22 (TTS 15.0 min, 0 images). Scope: full. Pause after: none.

Warnings:
- No sources supplied: content will be general knowledge; every claim is labelled general_knowledge and listed in REPORT.md.
