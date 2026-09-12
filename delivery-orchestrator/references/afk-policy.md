# AFK policy — how to keep moving without the human

The user wants to walk away. Every stop costs them a context switch, so stopping is a last resort and must be earned by a real dependency.

## Decision taxonomy

Classify every open question before acting on it:

| Class | Definition | Action |
|---|---|---|
| **Hard gate** | Irreversible, costly, security-relevant, or listed by the user in the autonomy contract | Stop that thread. Log `needs-human`. Work around it (see reordering). |
| **Dependent** | Reversible, but a ticket in the *current* wave needs the answer | Pick the provisional answer (reversibility rule), log `deferred`, mark affected tickets `provisional`, continue |
| **Independent** | Nothing in flight depends on it | Log `deferred` with your provisional choice; continue; never mention it mid-run |
| **Cosmetic** | Naming, wording, colours, copy | Decide, log one line, move on |

Default hard gates (always, regardless of AFK level):
- Deploying to any shared/production environment
- Creating, rotating, or reading secrets/credentials; changing IAM/roles
- Destructive data migrations or schema drops; anything that deletes user data
- Changing the auth/authz model (who can see/do what)
- Adding paid services, licence-restricted (GPL/AGPL in proprietary code) or unvetted dependencies
- Force-pushing, rewriting shared history, deleting branches other than the worker's own
- Spending beyond the run box agreed in the interview
- Anything the user named in the autonomy contract

## AFK levels

| Level | Behaviour |
|---|---|
| `supervised` | Ask at every gate (hard and dependent). Independent questions still deferred and batched at wave end. |
| `afk` (default) | Ask only at hard gates. Dependent → provisional + `provisional` label. Batch all questions at the end of each wave. |
| `full-afk` | Same as `afk`, plus: hard gates that have no dependents are logged and skipped; stop only when a hard gate blocks the entire frontier or the run box is exhausted. |

## Reversibility rule (choosing provisionally)

When you must choose without the user, choose the option that is cheapest to undo:
- Feature flag / config switch over a hard-coded behaviour
- Adapter/interface over a direct third-party call
- Additive migration (new column/table) over altering/dropping
- Conservative default (deny, off, smallest scope, lowest cost) over permissive
- Keep the old path alive behind the new one for one wave
Record the choice, the alternative, and the undo cost in `DECISIONS.md`.

## Reordering around a blocked gate

1. Mark the blocked ticket(s) `blocked (needs-human)` in STATE.md.
2. Recompute the frontier: every `ready` ticket whose blockers are done or merely `provisional`.
3. Dispatch those. Pull later-wave tickets forward if their Scope is disjoint from anything in flight.
4. If the frontier is empty: finish in-flight work, run the review gate on open PRs, merge what's approved, run `test-runner`, write `/handoff`, write the `needs-human` batch, stop.

## `docs/ai/DECISIONS.md` format

```
| # | Date | Class | Question | Provisional choice | Alternative | Undo cost | Depends on it | Status |
|---|---|---|---|---|---|---|---|---|
| 7 | 2026-09-12 | deferred | Pagination style for /orders | cursor-based | offset | low (query param shape) | #14 | provisional |
| 8 | 2026-09-12 | needs-human | Enable Stripe live keys | — | — | — | #21 | blocking |
```

## End-of-run summary (what the human reads first)

≤ 15 lines at the top of STATE.md under `## For Tamer`:
1. Destination status: met / partial (what's missing)
2. Merged PRs (count + titles), open PRs awaiting review or human merge
3. `needs-human` items ordered by how much work each unblocks
4. `provisional` choices worth a second look (max 5, highest undo cost first)
5. Next action if resumed

## Things AFK never licenses

- Widening the spec's scope or acceptance criteria
- Marking a ticket done with failing or skipped tests
- Merging a PR with a `[BLOCKING]` review finding
- Editing another worker's branch or worktree
- Guessing at compliance-relevant behaviour (data retention, logging of PII, access control) — those are hard gates
