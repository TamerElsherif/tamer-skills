---
name: delivery-orchestrator
description: Interview-driven kickoff and end-to-end orchestration for software work — new apps, new features, refactors, migrations, bug batches. Interrogates the user to pin the exact entry point (new vs existing project, app type, current stage, goal, constraints, AFK tolerance), offers a fast throwaway prototype before heavy investment, bootstraps the multi-agent workspace (worktree-isolated implementer/reviewer subagents with per-role model routing), then drives the Matt Pocock chain (research → prototype → wayfinder/grill-with-docs → to-spec → spec debate → to-tickets → parallel implement → debate-review → merge) in AFK mode, deferring human decisions that nothing depends on. Use this whenever the user says they are starting a project, kicking off work, planning a feature or refactor, "what should we do first", "let's build", "plan this", "work through these issues", or wants to hand a project to agents and walk away — even if they don't say "orchestrate".
---

# Delivery Orchestrator

You turn "I want to build/change X" into merged, reviewed code with minimal human interruption. You do it in four moves: **interview → route → bootstrap → run**. You are the orchestrator; subagents do the coding.

Read the reference files only when you reach the step that needs them:

| When | Read |
|---|---|
| Starting the interview | `references/interview.md` |
| Deciding whether to offer a prototype | `references/prototype.md` |
| Entering AFK mode or hitting a human question | `references/afk-policy.md` |
| Running the phases (Modes A/B/C, review gate, waves) | `references/workflow.md` |
| Choosing/justifying models | `references/model-routing.md` |
| Bootstrapping the repo | `scripts/bootstrap.sh` + `assets/` |

## 0. Resume check (before anything else)

If `docs/ai/STATE.md` exists in the repo: do **not** re-interview. Read it, summarise mode/wave/blockers in 5 lines, and continue from Section 4 (or from the `Next action` line in STATE.md). Ask only about items marked `needs-human`.

## 1. Interview — pin the entry point

Goal: know exactly where the work starts, what "done" means, and how autonomous you may be. Ask in rounds of ≤ 4 questions using the AskUserQuestion tool (multiple choice where possible; free text for goal/constraints). Stop asking as soon as the route is unambiguous — an interview is a cost, not a ritual.

**Round 1 — always (unless already answered in the request):**
1. New project or existing codebase?
2. What are we producing? (Web app · API/service · Mobile — Android/iOS/cross-platform · Desktop — Electron/Tauri · CLI · Library/SDK · Data/ML pipeline · Automation/integration · Browser extension · Other)
3. Current stage: general idea · idea documented (PRD/notes) · spec written · tickets/issues exist · prototype exists · MVP live · expanding a feature · fixing bugs · large refactor · migration/port
4. What must be true at the end of this run? (one sentence; this becomes the destination)

**Round 2 — branch on answers.** `references/interview.md` has the full question tree: per-app-type questions (hosting, stores, offline, signing, auto-update…), per-stage questions (where the docs are, which tickets, bug list), constraints (stack locks, deadline, budget cap, compliance such as ISO 27001/SOC 2 data handling), and tracker (GitHub Issues default).

**Round 3 — autonomy contract (always):**
- AFK level: `supervised` (ask at every gate) · `afk` (ask only at hard gates, defer the rest) · `full-afk` (defer everything deferrable, stop only at hard gates with dependents).
- Which decisions the user insists on making (defaults to the hard-gate list in `afk-policy.md`).
- Time/token box for this run (e.g., "stop after wave 2" or "max ~2h").
- Prototype appetite: yes/no/"only if you think it de-risks something".

**Existing codebase — inspect before asking.** Run a quick survey (README, manifest, `git log --oneline -30`, test dir, CI config, `docs/adr`, open issues via `gh issue list`) and pre-fill answers; ask only what you could not infer. Say what you inferred in one line so the user can correct it.

Write the interview result to `docs/ai/BRIEF.md` (template in `assets/BRIEF.md`). It is the contract for the run.

## 2. Route — choose the entry point

| Stage | Mode | First step |
|---|---|---|
| General idea | A | parallel `researcher` on unknowns → prototype offer → `/wayfinder` (multi-session) or `/grill-with-docs` (fits one session) |
| Idea documented (PRD/notes, no spec) | A | import docs into `CONTEXT.md` via `/grill-with-docs` → `/to-spec` |
| Spec exists | A | `spec-critic` debate → `/to-tickets` |
| Tickets/issues exist | B | harden tickets (Scope / Blocked-by / Done-when / Test-command) → wave board → parallel implement |
| Prototype exists, no spec | A | grill using the prototype as evidence → ADRs → `/to-spec` |
| MVP live, expand feature | A (scoped) | `/grill-with-docs` on the feature → `/to-spec` → `/to-tickets` |
| Fixing bugs | C | `/triage` the list → one `implementer` per independent bug (parallel) with `diagnosing-bugs` |
| Large refactor | A | `/improve-codebase-architecture` → `/wayfinder` → ADRs → spec → tickets |
| Migration/port | A | `researcher` on target platform → spike prototype → ADR → spec → tickets |

State the route in two lines. Do not ask permission to start the standard flow — that is what the autonomy contract was for.

## 3. Prototype offer — cheap certainty before investment

If stage ≤ "spec exists" and the destination has any UI, UX, or unproven-integration risk, propose a **timeboxed throwaway prototype** before speccing (details in `references/prototype.md`): single-file HTML for flows/state, terminal app for business logic, 2–3 radically different UI variants for look-and-feel, or a 1-hour spike for a risky integration. Show it, get one round of reaction, record what changed the plan in `docs/ai/BRIEF.md`, delete the prototype. If the user declined prototypes in the interview, skip silently. In AFK mode: build it, leave the reaction request in `DECISIONS.md`, and continue with the spec using your best reading — the spec debate will catch drift.

## 4. Bootstrap the workspace (once per repo)

Run `scripts/bootstrap.sh` (or do its steps by hand if the shell is restricted). It installs `mattpocock-skills`, `amElnagdy/guard-skills` (clean-code-guard, test-guard, docs-guard), `amElnagdy/review-skills` (debate-review, babysit-pr), optionally `codex-delegate`; runs `/setup-matt-pocock-skills`; copies `assets/agents/*.md` → `.claude/agents/`, `assets/settings.json` → `.claude/settings.json`, `assets/CLAUDE.orchestrator.md` → appended to `CLAUDE.md`, `assets/STATE.md` + `assets/DECISIONS.md` → `docs/ai/`. Then resolve the exact installed skill IDs and patch the `skills:` lists in the agent files (plugin skills may be scoped like `mattpocock-skills:tdd`), and run `claude plugin validate .claude/agents`. Skip any part that already exists.

## 5. Run — follow `references/workflow.md`

Mode A (discover → ADRs → spec → debate → tickets → waves), Mode B (parallel implementers in worktrees → debate-review + guards → merge in dependency order → test-runner on main → next wave), Mode C (fast lane). Model routing per role is fixed in the agent frontmatter (`references/model-routing.md` explains why). Keep `docs/ai/STATE.md` current after every dispatch, verdict, and merge; `/compact` at ~40 % context; `/handoff` before stopping.

## 6. AFK behaviour — the rules that make walking away safe

Full policy in `references/afk-policy.md`. The short version:

- **Defer, don't block.** Any question whose answer nothing in the current wave depends on goes to `docs/ai/DECISIONS.md` as `deferred` with a provisional choice, the reason, and how to reverse it. Continue.
- **Prefer the reversible option** when choosing provisionally (feature flag over hard switch, adapter over direct dependency, additive migration over destructive).
- **Hard gates always stop**: production deploy, secrets/credentials, destructive data migrations, auth/authz model changes, paid third-party services, licence-restricted dependencies, anything the user listed in the autonomy contract.
- **Reorder work around a blocked gate.** Pull forward tickets that don't depend on it; only stop when the whole frontier is blocked — then write `/handoff` and a `needs-human` summary and stop cleanly.
- **Batch questions.** When you do need a human, ask everything pending in one message, ordered by what unblocks the most work.
- **Never silently widen scope.** A discovery that changes the spec is a `needs-human` item, not a unilateral rewrite — unless it is a pure bug fix within a ticket's Scope.

## 7. Definition of done for this run

The destination sentence from the interview is met and demonstrable (tests map to acceptance criteria) · `main` green · ADRs and `CONTEXT.md` updated · `DECISIONS.md` has no `deferred` item that is now blocking · `STATE.md` shows what's next · a `/handoff` exists if anything remains.
