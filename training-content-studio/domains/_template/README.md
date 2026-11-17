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
