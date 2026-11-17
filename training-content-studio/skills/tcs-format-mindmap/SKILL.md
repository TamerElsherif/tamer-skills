---
name: tcs-format-mindmap
description: Builds the mindmap-format scenes of a lesson storyboard — a node tree that expands with progressive reveal in sync with narration (reveal timeline + focus moves). Use when the chosen or requested format is "mindmap", "mind map", "concept map", "expanding diagram", "progressive reveal" or "big-picture overview". Not for linear procedures (tcs-format-explainer steps or tcs-format-screencast-sim) or hand-drawn boards (tcs-format-doodle).
---

# tcs-format-mindmap

## Purpose
Show how a topic is structured — categories, sub-types, relationships — by growing a tree node by node.
Great for overviews, taxonomies (types of malware, data classes), module intros and recaps.

## Inputs
- Approved lesson (`curriculum.yaml`), facts/glossary from `sources.yaml`, domain `glossary.yaml` for consistent labels.

## Outputs
- `mindmap` scenes: `{root, nodes[]{id, label, parent ("root" or node id), cue, icon?, tone?}, focus[]{cue, node}}`.
  The **node tree** is `nodes[]` (parent links); the **reveal timeline** is the `cue` on each node + `focus[]`.
- Supporting scenes: `title`, `definition` (zoom into one node), `comparison`, `quiz`, `checklist`, `outro`.
- Fill-ins `templates/node_tree.yaml`, `templates/script_template.md`; fragment `templates/example.storyboard.json`.

## Steps
1. Build the tree first (`templates/node_tree.yaml`): root = lesson topic, 3–5 branches, ≤ 3 leaves per branch, depth ≤ 3.
2. Order the reveal: branch → its leaves → next branch (depth-first) unless comparing branches (breadth-first).
3. Script narration with one `^` per node reveal; `focus` cues when the narrator dwells on a branch.
4. If one map exceeds 12 nodes, split: overview map (branches only) + one map per branch.
5. Follow with a `definition`/`comparison` zoom for the most important branch, then `quiz` + recap.
6. Claims per scene; validate (every `parent` exists; cues ascending; max cue + 1 ≤ `^` count).

## Rules / QA
- ≤ 12 nodes per scene, labels ≤ 4 words, icons from the kit subset; `tone: warn` for the risky branch only.
- Node `cue` ascending in reading order; children never appear before their parent.
- RTL: tree mirrors (root right-to-left growth) — handled by kit when `direction: rtl`; keep labels short for Arabic width.
- A mindmap scene should last 15–40 s; hold ≥ 2 s on the complete map.

## Blends
- **mindmap + explainer**: map as the module intro/recap, explainer scenes in between.
- **mindmap + job-aid**: the completed map is printed as the job-aid (static target renders final state).
- **mindmap + series**: one branch per nudge; flashcards per leaf.
- **mindmap + narrated-deck**: map slide as agenda; each branch becomes a section.

## References
- `references/playbook.md`, `templates/node_tree.yaml`, `templates/script_template.md`, `templates/example.storyboard.json`.
