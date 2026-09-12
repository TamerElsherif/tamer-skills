# Workflow — Modes A, B, C

The orchestrator plans, delegates, reviews, merges, tracks. It does not write bulk code. Skill names below are Matt Pocock's (`mattpocock-skills`) unless marked (guard) = `amElnagdy/guard-skills` or (review) = `amElnagdy/review-skills`.

Contents: 1 Mode A · 2 Ticket hardening & waves · 3 Mode B loop · 4 Parallel-safety rules · 5 Review gate · 6 Mode C · 7 State hygiene · 8 Done

## 1. Mode A — discovery → ADRs → spec → tickets

1. `/setup-matt-pocock-skills` once per repo (creates `CONTEXT.md`, `docs/adr/`, tracker config).
2. **Unknowns in parallel.** One `researcher` subagent (background) per open technical question → `docs/research/<topic>.md`. Never research in the orchestrator session.
3. **Prototype** per `references/prototype.md` if warranted.
4. **Planner by scope**: effort > one session or foggy → `/wayfinder` (resolve decision tickets; `researcher` burns down research tickets; feed the map issue to `/to-spec`). Fits one session → `/grill-with-docs` until every branch is resolved.
5. **ADRs before spec** (written inline by `/grill-with-docs`). Minimum: topology (default modular monolith), data model/store, auth/authz, observability, testing strategy, performance budgets if user-facing, deployment target. Architecture ADRs are a hard gate — in AFK mode pick the reversible option, log `provisional`, continue.
6. `/to-spec` → spec on the tracker with user stories, testable acceptance criteria, non-goals, module map, ADR refs.
7. **Spec debate**: `spec-critic` (Opus, read-only). Optional cross-vendor second opinion via `codex-delegate`. Adjudicate each finding (accept → edit spec; reject → "Debate log" note). Max 2 rounds.
8. `/to-tickets` → tracer-bullet tickets with blocking edges, one issue each.

## 2. Ticket hardening & wave board

Every ticket must carry, in its body:
```
Scope: <paths/globs this ticket may touch>
Blocked-by: #n, #m
Done-when: <acceptance criteria from the spec, verbatim>
Test-command: <exact command>
```
Overlapping Scopes → add a blocking edge so they never share a wave. Shared files (routes index, DI container, schema, lockfiles, i18n indexes, CI config) get their own earlier ticket.

Waves: wave 1 = no blockers; wave k = all blockers in waves < k. Concurrency cap per wave = min(tickets, 4) unless the budget in `BRIEF.md` says otherwise. Write the board to `docs/ai/STATE.md`; label wave-1 tickets `ready-for-agent`.

## 3. Mode B — parallel implementation loop

Repeat until the board is empty or the run box is exhausted:

1. **Dispatch**: one `implementer` subagent per `ready-for-agent` ticket in the wave (Sonnet, `isolation: worktree`, background). Message contains: issue #, full ticket text, Scope, Done-when, Test-command, `CONTEXT.md` excerpt, branch `agent/<issue>-<slug>`. Label `in-progress`; record agent → ticket → branch in STATE.md.
2. **Reports**: workers reply with the ≤ 200-word structured report (branch, PR, files, tests, guards, open questions). Reject anything longer.
3. **Review gate** (Section 5) per PR as it lands — don't wait for the wave.
4. **Merge** approved PRs in dependency order (squash), then `test-runner` (Haiku) on `main`. Red → open a `fix` ticket at the front of the next wave; no further merges until green.
5. **Close** the issue, unblock dependents, relabel next wave, update STATE.md, `/compact` if context ≥ 40 %.
6. **Docs** at wave end or before release: `docs-writer` (Sonnet) → PR → `docs-guard` (guard).

## 4. Parallel-safety rules (non-negotiable)

- One ticket = one worktree = one branch = one PR. Never two workers on a branch.
- Disjoint Scope within a wave. Out-of-Scope need → worker stops and reports; orchestrator extends scope or splits a ticket.
- Workers branch from current `main` HEAD (`worktree.baseRef: "head"`), rebase only their own branch, never touch other worktrees.
- Workers push and open PRs; only the orchestrator merges. No force-push, no edits to `main`.
- After each merge, later-wave workers start from a fresh worktree on the new HEAD.
- Conflicts are resolved by the orchestrator in the main checkout with `resolving-merge-conflicts`.

## 5. Review gate (every PR)

1. `debate-review` (review): main reviewer Opus, second reviewer tries to knock findings down, main reviewer decides; posts one review with inline comments via `gh`. Fallback: `reviewer` subagent running `code-review` (Standards + Spec axes).
2. Guards on the diff: `clean-code-guard` (production code), `test-guard` (tests), `docs-guard` (docs touched). A guard "do not merge" is blocking.
3. Security pass inside the review: injection, authz/IDOR, secrets, N+1/unbounded queries, input validation, error swallowing.
4. Verdict: `approve` · `changes-requested` (blocking list) · `escalate`.
5. `changes-requested` → **resume the same implementer** with the findings (keeps context); `babysit-pr` (review) may drive the rounds. Max 3 rounds → `needs-human`.
6. `approve` → CI green → squash-merge → close issue with PR link.

## 6. Mode C — fast lane

Bug: `implementer` with `diagnosing-bugs` (reproduce → minimise → hypothesise → instrument → fix → regression test). Small feature: `implementer` with a self-written hardened ticket. Independent bugs run in parallel, one worktree each. Review gate, merge, done. Grows past one ticket → switch to Mode A/B.

## 7. State & context hygiene

- `docs/ai/STATE.md`: mode, wave board, active agents, PR status, blockers, `Next action`, `## For Tamer` summary.
- `docs/ai/DECISIONS.md`: every deferred/provisional/needs-human item (format in `afk-policy.md`).
- `/compact` at ~40 % context (write STATE.md first). `/handoff` before ending.
- `domain-modeling` when a term or decision changes `CONTEXT.md`/ADRs. `/improve-codebase-architecture` every few waves on long projects.

## 8. Done

All tickets done · `main` green · acceptance criteria ↔ test names · ADRs/`CONTEXT.md` current · docs pass `docs-guard` · perf budgets measured if declared · no open `[BLOCKING]` · `DECISIONS.md` has no blocking item · human gates signed off.
