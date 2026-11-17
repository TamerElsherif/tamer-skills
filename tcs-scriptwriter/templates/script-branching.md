---
# Branching scenario. Linear video follows the (correct) path; lesson/SCORM targets render the full graph.
course_id: {{course_id}}
lesson_id: {{lesson_id}}
title: {{lesson title}}
language: {{en-US}}
formats: [branching]
level: {{level}}
target_min: {{duration_min}}
objective_ids: [{{O1}}]
cast: [learner, customer]
---

## s01_setup | setup | {{O1}}
template: cartoon
narrator: {{Situation in 2 sentences; the viewer is the learner.}}
customer: ^ {{the request that creates the dilemma}}
claim: {{context fact}} [{{S01#c1}}]

## s02_decide | decision | {{O1}}
narrator: What do you do?
choice: {{best action}} -> s03_good (correct)
choice: {{tempting wrong action}} -> s04_bad
choice: {{partly right action}} -> s05_meh
claim: {{the rule that decides the answer}} [{{S01#c1}}]

## s03_good | consequence | {{O1}}
narrator: ^ {{Outcome + why it is right (cite the rule).}}
claim: {{rule}} [{{S01#c1}}]

## s04_bad | consequence | {{O1}}
narrator: ^ {{Outcome + what rule it broke, no shaming.}}
claim: {{consequence}} [{{S01#c1}}]

## s05_meh | consequence | {{O1}}
narrator: ^ {{Outcome + what was missing.}}
claim: {{rule}} [{{S01#c1}}]

## s06_debrief | recap | {{O1}}
template: checklist
narrator: {{Debrief:}} ^ {{key behaviour 1}} ^ {{key behaviour 2}}
claim: {{recap}} [{{S01#c1}}]
