# Auto-fix guidance (per status)

Apply fixes to the **source of truth** — the script/storyboard claim, the narration that says it, the on-screen props
that show it, and quiz items — then re-run `check.py`. Never fix by deleting the citation only.

| Status | Typical cause | Fix, in order of preference |
|---|---|---|
| unsupported (unknown id) | typo / source re-numbered | re-cite the correct `S..#c..` from sources.yaml |
| unsupported (no evidence) | claim from model memory or wrong source | 1) re-cite a source that states it · 2) label `general_knowledge: true` if allowed and non-critical (not policy, numbers, legal) · 3) remove the claim and its narration/props |
| unsupported (on-screen number) | number in props not in any claim | add the sourced claim to the scene; fictional scenario numbers → claim "Scenario: … (fictional example)" `[general]` |
| partial | over-generalised, dropped condition, extra number | soften to the source wording; restore the exception; split into two claims and cite each |
| conflicting (number) | wrong figure | change narration/props/claim to the source figure (speakable form in narration) |
| conflicting (sources disagree) | two sources differ | resolve in sources.yaml (authority → newer date → specificity) and cite the chosen fact; else avoid the number ("keep receipts as long as Finance requires") and flag for owner |
| outdated | source older than max age, old statistic | confirm with owner; prefer newer source; or show the year on screen ("in 2019, …") |
| general-knowledge | labelled model knowledge | OK if allowed; keep out of policy rules, legal claims and numbers; prefer sourcing |

Gate rule (orchestrator/autopilot): render only when unsupported + partial + conflicting = 0 (exit code 0).
Autopilot may auto-apply: re-cite, soften, add scenario GK claims, correct numbers to the cited fact. It must NOT
auto-label policy/number claims as general knowledge or resolve source conflicts by itself — record those in decisions.

Never: invent a source, cite a source for a claim it does not contain, or round/convert numbers.
