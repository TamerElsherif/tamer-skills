# Decisions — g1-netsuite-expenses

Request: Teach new hires how to submit expenses in NetSuite

| decision | value | signal | confidence | source | alternative rejected |
|---|---|---|---|---|---|
| language | {"primary": "en-US", "subtitles": []} | request written in English, no MENA cue | 0.85 | request | Arabic primary + English subtitles |
| audience | {"id": "new-hires", "roles": ["learner", "rookie"], "segment": "staff"} | wording 'new hires' | 0.80 | request | general staff |
| level | beginner | audience cue 'new hires' | 0.80 | request | intermediate |
| other (objective_type) | procedure | procedure: 'how to', 'submit' | 0.95 | request | concept (default) |
| domain | software-procedure | no pack keyword; inferred from objective type 'procedure' | 0.60 | rule | a specific domain pack |
| domain_pack | _template | no domain pack matched | 0.70 | default | closest pack |
| objectives | O1: Identify what you need before you submit expenses in NetSuite (remember); O2: Complete the steps to submit expenses in NetSuite correctly (apply); O3: Check your work and fix common errors when you submit expenses in NetSuite (analyze) | type=procedure (Bloom matched: know->remember/understand, do->apply, decide->analyze/evaluate); no sources/count wording -> default objective set for type | 0.55 | default | single broad objective |
| formats | ["screencast-sim", "job-aid"] | procedure + software cue 'NetSuite' -> ['screencast-sim', 'job-aid'] | 0.75 | rule | ['explainer'] (concept rule) |
| other (assessment) | {"assessment": "scenario", "evidence": false, "broll": false} | assessment for procedure | 0.80 | rule | no assessment |
| blend | ["screencast-sim", "job-aid"] | primary screencast-sim + secondary job-aid (max 2/lesson, 3/course) | 0.80 | rule | single format |
| length | {"lessons": 3, "minutes_per_lesson": 5, "total_minutes": 15} | microlearning: 1 objective/lesson, 5 min for procedure (band 3-7), <= 6 lessons/module | 0.75 | rule | one long lesson |
| wpm | 130 | beginner 130 wpm | 0.80 | rule | 145 wpm |
| verbosity | standard | new-hires / beginner | 0.70 | rule | detailed |
| targets | ["video", "jobaid", "video-vertical", "scorm"] | screencast-sim->video; job-aid->jobaid; video format -> + 9:16 nudge cut; 3 lessons -> + SCORM | 0.80 | rule | video only |
| aspect | ["16:9", "9:16"] | 16:9 master + 9:16 nudge cut | 0.80 | rule | 9:16 only |
| renderer | remotion | standalone kit (tcs-render-remotion); no OPENMONTAGE_ROOT | 0.60 | rule | openmontage |

Estimate: ~84,000 tokens, ~$0.98 (TTS 15.0 min, 0 images). Scope: full. Pause after: none.
