# Mindmap / progressive-reveal playbook

## When to use
- Taxonomies and overviews: "types of X", "levels of Y", "who does what", module intros/recaps.
- Learners need the big picture before details; or a recap that links many items.
- Avoid for sequences (use `steps`/`process_flow`) or stories (cartoon/comic).

## Duration
| Variant | Nodes | Length |
|---|---|---|
| Single map | 6–12 | 20–40 s scene; 1–2 min lesson with zoom-ins |
| Overview + branch maps | 4 + 3×(4–8) | 2–4 min |

## Beat structure (2 min)
| # | Beat | Time | Template |
|---|---|---|---|
| 1 | Title | 4–6 s | `title` |
| 2 | Overview map (branches) | 15–25 s | `mindmap` |
| 3 | Branch A expanded | 15–30 s | `mindmap` (focus A) |
| 4 | Zoom: key term | 10–15 s | `definition` |
| 5 | Branch B / C | 15–30 s each | `mindmap` |
| 6 | Contrast branches | 10–20 s | `comparison` |
| 7 | Check | 10–14 s | `quiz` |
| 8 | Recap (full map held) | 8–12 s | `mindmap` (all cues 0) or `checklist` |
| 9 | Outro | 4–6 s | `outro` |

## Reveal timeline rules
- Depth-first for explanation, breadth-first for comparison.
- `focus` on the branch being discussed (camera eases to it); release focus on the recap.
- ≥ 1.0 s between consecutive node cues; leaves of one branch may share a cue if listed quickly.

## Tree hygiene
- Parallel labels (all nouns or all verbs per level).
- Same term as in the domain glossary (and its Arabic equivalent from `glossary.yaml`).
- No orphan nodes; no single-child branches (merge them).

## Do / Don't
| Do | Don't |
|---|---|
| ≤ 12 nodes, depth ≤ 3 | 30-node "everything" map |
| Labels ≤ 4 words | Sentences in nodes |
| One warn-toned branch | Colour-code every branch differently without meaning |

## Worked example (`templates/example.storyboard.json`)
"Data Classification at a Glance": root "Northwind data" → Public (+ website) → Internal (+ org chart) →
Confidential (+ contracts, + customer personal data) with focus on Confidential; `definition` zoom; `quiz`; `outro`.
