# Decisions — golden-security-microdrama

Request: 90-second security micro-drama + branching scenario + knowledge check on BEC / CEO-fraud payment requests, English (en-US), 16:9, for all staff incl. finance

| decision | value | signal | confidence | source | alternative rejected |
|---|---|---|---|---|---|
| language | {"primary": "en-US", "subtitles": []} | --lang en | 1.00 | flag | Arabic primary |
| audience | {"id": "all-staff", "roles": ["learner"], "segment": "staff", "notes": "all staff incl. finance / payment approvers"} | request 'for all staff incl. finance' | 1.00 | request | general staff |
| level | beginner-intermediate | mixed audience ('all staff'), jargon density 0.00 | 0.70 | rule | intermediate |
| other (objective_type) | behavior | behavior: 'fraud', 'sources:warningx10' | 0.81 | sources | policy=0.714286, procedure=0.285714, concept=0.142857 |
| domain | security-awareness | --domain security-awareness | 1.00 | flag | - |
| domain_pack | security-awareness | --domain flag | 1.00 | flag | _template |
| objectives | O1: Spot the warning signs of a fake payment or bank-detail change request (analyze); O2: Decide the safe response: call back a known number and keep two-person approval (evaluate); O3: Report a suspicious payment request to IT Security (apply) | intake: user kept the 3 proposed objectives | 1.00 | user | decide.py template objectives (topic parsed from the whole request) |
| formats | ["cartoon", "branching"] | request wording pins ['cartoon', 'branching']; behavior -> ['cartoon', 'branching'] | 0.95 | request | ['cartoon', 'branching'] (rule) |
| other (assessment) | {"assessment": "knowledge-check", "evidence": false, "broll": false} | assessment for behavior | 0.80 | rule | no assessment |
| blend | ["cartoon", "branching"] | primary cartoon + secondary branching (max 2/lesson, 3/course) | 0.80 | rule | single format |
| length | {"lessons": 1, "minutes_per_lesson": 1.5, "total_minutes": 1.5} | request '90-second' | 1.00 | request | microlearning default |
| wpm | 140 | beginner-intermediate 140 wpm | 0.80 | rule | 155 wpm |
| verbosity | standard | all-staff / beginner-intermediate | 0.70 | rule | detailed |
| targets | ["video", "lesson", "scorm"] | intake Q2: 'MP4 16:9, HTML lesson and SCORM' | 1.00 | user | derived from formats |
| aspect | ["16:9"] | --aspect 16:9 | 1.00 | flag | 16:9 primary |
| renderer | remotion | default: standalone kit (OpenMontage alternative documented in RENDER_COMMANDS.md) | 0.80 | default | openmontage |
| other (sources) | {"files": ["sources/northwind-payment-verification-policy.md"], "general_knowledge_allowed": true} | intake Q1: 'use the policy; general knowledge OK, labelled' | 1.00 | user | - |
| other (cast) | ["rookie", "exec", "vex", "mentor"] | domain scenarios.md #3 CEO fraud + #2 BEC | 0.80 | default | - |
| other (approval) | {"status": "approved", "edits": []} | gate shown (skeleton + M1L1 preview); simulated user: 'Approve' | 1.00 | user | - |

Estimate: ~37,000 tokens, ~$0.36 (TTS 1.5 min, 0 images). Scope: full. Pause after: none.
