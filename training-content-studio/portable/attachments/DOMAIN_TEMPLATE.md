# DOMAIN PACK: _template

## README.md
# Domain pack template

Copy this folder to `domains/<pack-id>/` and fill each file. A pack adds domain knowledge to the generic skills; it
never changes schemas. Everything here is optional except `pack.yaml`. Facts that learners will be tested on must still
come from client sources (`sources.yaml`); pack content is labelled `general_knowledge` unless sourced.

| File | Read by | Purpose |
|---|---|---|
| `pack.yaml` | orchestrator / autopilot | id, languages, audiences, detection keywords, file list |
| `glossary.yaml` | scriptwriter, localize, mindmap | EN + AR (MSA + Egyptian usage) terms |
| `personas.yaml` | cartoon, comic, branching, series | role mapping of core personas + extra personas (with kit look, voice, locked prompt) |
| `scenarios.md` | cartoon, comic, branching, explainer | realistic situations, red flags, safe actions, premises |
| `prioritization.yaml` | curriculum | weights, audience quotas, dedupe clusters, tiers |
| `compliance.yaml` | curriculum, outro evidence line, SCORM export | frameworks, evidence records to keep |
| `format_defaults.yaml` | orchestrator / autopilot | default formats by objective type and audience, blends, music, theme |
| `mockups.yaml` | explainer, cartoon, series | ready-made props for email/chat/mfa/browser/popup templates |

Validation: `.venv/bin/python portable/build_portable.py --check` parses every pack YAML and validates mock-up presets
against `schemas/storyboard.schema.json`.
Reference implementation: `domains/security-awareness/`.


## compliance.yaml
```yaml
schema_version: "1.0"
general_knowledge: true        # confirm with the client's compliance owner
frameworks:
  <framework-id>:
    name: "<standard / regulation>"
    controls:
      - {id: "<clause>", title: "<title>", meaning: "<what training evidence it implies>"}
    evidence_line: "<optional outro line>"
records_to_keep:
  - {field: learner_id}
  - {field: course_id}
  - {field: content_version}
  - {field: language}
  - {field: completed_at}
  - {field: score}
```

## format_defaults.yaml
```yaml
schema_version: "1.0"
default_formats_by_objective_type: {concept: [explainer], behavior: [cartoon], procedure: [screencast-sim, job-aid], policy: [narrated-deck, job-aid], recall: [series]}
default_formats_by_audience: {standard: [explainer]}
blends: [[explainer, job-aid]]
durations_min: {micro: 1.5, standard: 3.5}
music_by_format: {explainer: explainer, cartoon: cartoon, doodle: whiteboard, narrated-deck: executive}
theme: {default: neutral}
always_include: ["<domain must-haves>"]
```

## glossary.yaml
```yaml
schema_version: "1.0"
general_knowledge: true
terms:
  # term: stable id · en · ar (MSA) · ar_eg (spoken Egyptian usage, may be the English word) · keep_en_in_ar · definition
  - {term: "<id>", en: "<English term>", ar: "<المصطلح بالفصحى>", ar_eg: "<كما يُقال في مصر>", keep_en_in_ar: true, definition: "<one sentence>"}
notes:
  - "Wrap Latin terms inside Arabic text in bidi isolates (U+2066 … U+2069)."
```

## mockups.yaml
```yaml
schema_version: "1.0"
presets: {}
#  <preset-id>:
#    template: email_mock | chat_mock | browser_mock | mfa_prompt | popup | code_mock | screencast
#    props: { … exactly as in schemas/storyboard.schema.json for that template … }
```

## pack.yaml
```yaml
schema_version: "1.0"
id: <pack-id>                     # kebab-case, equals folder name
title: "<Domain title>"
version: "0.1.0"
languages: [en-US, ar-EG]
audiences: [standard]             # audience keys used by prioritization quotas
files:
  glossary: glossary.yaml
  personas: personas.yaml
  scenarios: scenarios.md
  prioritization: prioritization.yaml
  compliance: compliance.yaml
  format_defaults: format_defaults.yaml
  mockups: mockups.yaml
detect_keywords: ["<keyword>", "<keyword>"]
facts_policy: "Definitions may be general_knowledge; procedures, thresholds, contacts and policy rules must come from client sources."
```

## personas.yaml
```yaml
schema_version: "1.0"
role_mapping:                 # core personas from assets/characters/personas.yaml → roles in this domain
  mentor: "<expert role>"
  rookie: "<who makes the typical mistake>"
  learner: "<who gets it right>"
personas: {}                  # optional extra personas:
#  <id>:
#    display_name: {en: "<Name>", ar: "<الاسم>"}
#    role: "<role>"
#    kit_cast: <id>            # ask the kit owner to add an SVG persona with this id
#    look: "<age, skin, hair, outfit>"
#    palette: {top: "#RRGGBB"}  # attention #FF6700 reserved for an antagonist, if any
#    voice: {provider: openai, voice: <voice>, instructions: "<acting>"}
#    poses: [idle]              # from schemas/enums.json
#    expressions: [neutral]
#    prompt: "<locked flat-vector prompt> {SCENE}. no text, no letters, no numbers, no signage, no logos"
```

## prioritization.yaml
```yaml
schema_version: "1.0"
weights: {impact: 0.30, frequency: 0.25, gap: 0.20, urgency: 0.15, compliance: 0.10}   # must sum to 1.0
scoring_anchors:
  impact: "<what 5 vs 1 means here>"
  frequency: "<…>"
  gap: "<…>"
  urgency: "<…>"
  compliance: "<…>"
quotas: {standard: 10}          # tier-1 picks per audience
tiers: {tier-1: "quota picks", tier-2: "next N", tier-3: "remaining in scope"}
filters_out_of_scope: ["<what to exclude>"]
dedupe: {rule: "One item per cluster unless a variant adds a distinct objective or audience.", decision_for_dropped: deprioritised-duplicate}
clusters:
  <cluster-id>: {label: "<label>", members: ["<topic>", "<topic>"]}
```

## scenarios.md
# <Domain> scenarios

General knowledge unless a source id is given. Fictional company Northwind Co.; `.example` domains only.

| # | Situation | Micro-drama premise (cast) | Warning signs / common mistakes | Right action (source id) | Templates / mock-up preset |
|---|---|---|---|---|---|
| 1 | <situation> | <premise> (rookie, mentor) | <signs> | <action> (S##) | <templates> |

## Premise rules
- Relatable, recoverable mistakes; end with the right action modelled.
- No real people, brands, phone numbers or live URLs.

