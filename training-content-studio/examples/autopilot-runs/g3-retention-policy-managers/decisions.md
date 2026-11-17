# Decisions — g3-retention-policy-managers

Request: Explain our new data retention policy to managers

| decision | value | signal | confidence | source | alternative rejected |
|---|---|---|---|---|---|
| language | {"primary": "en-US", "subtitles": []} | request written in English, no MENA cue | 0.85 | request | Arabic primary + English subtitles |
| audience | {"id": "managers", "roles": ["manager"], "segment": "executive"} | wording 'managers' | 0.75 | request | general staff |
| level | beginner-intermediate | audience cue 'managers' | 0.75 | request | intermediate |
| other (objective_type) | policy | policy: 'policy', 'retention' | 0.80 | request | concept=1 |
| domain | policy-compliance | no pack keyword; inferred from objective type 'policy' | 0.60 | rule | a specific domain pack |
| domain_pack | _template | no domain pack matched | 0.70 | default | closest pack |
| objectives | O1: Explain what the new data retention policy requires and why (understand); O2: Apply the new data retention policy to everyday decisions (apply); O3: Decide how to handle exceptions and edge cases under the new data retention policy (evaluate) | type=policy (Bloom matched: know->remember/understand, do->apply, decide->analyze/evaluate); no sources/count wording -> default objective set for type | 0.55 | default | single broad objective |
| formats | ["narrated-deck", "job-aid"] | policy -> ['cartoon']; managers audience -> narrated-deck primary + job-aid | 0.75 | rule | ['cartoon'] (type default) |
| other (assessment) | {"assessment": "post-test", "evidence": true, "broll": false} | assessment for policy; compliance evidence (completion + attestation) | 0.80 | rule | no assessment |
| blend | ["narrated-deck", "job-aid"] | primary narrated-deck + secondary job-aid (max 2/lesson, 3/course) | 0.80 | rule | single format |
| length | {"lessons": 3, "minutes_per_lesson": 5, "total_minutes": 15} | microlearning: 1 objective/lesson, 5 min for policy (band 3-7), <= 6 lessons/module | 0.75 | rule | one long lesson |
| wpm | 140 | beginner-intermediate 140 wpm | 0.80 | rule | 155 wpm |
| verbosity | concise | managers / beginner-intermediate | 0.70 | rule | detailed |
| targets | ["deck", "video", "jobaid", "scorm"] | narrated-deck->deck+video; job-aid->jobaid; 3 lessons + compliance evidence -> + SCORM | 0.80 | rule | video only |
| aspect | ["16:9"] | 16:9 master | 0.80 | rule | 9:16 only |
| renderer | remotion | standalone kit (tcs-render-remotion); no OPENMONTAGE_ROOT | 0.60 | rule | openmontage |

Estimate: ~78,000 tokens, ~$1.17 (TTS 15.0 min, 6 images). Scope: full. Pause after: plan.
