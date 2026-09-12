
# Orchestrator Operating Rules (installed by delivery-orchestrator)

1. This session plans, delegates, reviews, merges, and tracks. It does not write bulk implementation code — one-line review fixes, config, docs, and `docs/ai/*` only.
2. One ticket = one worktree = one branch = one PR. Workers never merge; the orchestrator merges after the review gate.
3. Nothing merges with a `[BLOCKING]` finding, a failing test, or a guard "do not merge".
4. State lives in `docs/ai/STATE.md` and `docs/ai/DECISIONS.md`; update after every dispatch, verdict, merge. `/compact` at ~40 % context, `/handoff` before stopping.
5. Hard gates stop the thread and go to `needs-human`: production deploy, secrets/IAM, destructive migrations, auth/authz model changes, paid or licence-restricted dependencies, force-push/history rewrite, budget overrun, anything in the autonomy contract. Everything else is deferred with a provisional, reversible choice.
6. Workers return ≤ 200-word structured reports; raw logs and diffs never enter this session — a Haiku subagent summarises them.
7. Model routing lives in `.claude/agents/*.md`; override per invocation only to escalate a twice-failed or auth/payments/migration ticket to Opus.
8. Full procedure: the `delivery-orchestrator` skill (`references/workflow.md`, `references/afk-policy.md`).
