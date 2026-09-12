# delivery-orchestrator

Interview-driven kickoff and end-to-end multi-agent orchestration for Claude Code. One skill takes you from "I want to build/change X" to merged, reviewed code — and lets you walk away.

## What it does

1. **Interview** — pins the exact entry point in ≤ 3 short rounds: new vs existing project, product type (web, API, mobile, desktop, CLI, library, data/ML, automation, extension), current stage (idea → docs → spec → tickets → prototype → MVP → feature → bugs → refactor → migration), destination, constraints, and an **autonomy contract** (AFK level, decisions you reserve, run box). Existing repos are surveyed first so it only asks what it can't infer.
2. **Prototype offer** — proposes a timeboxed throwaway prototype (HTML flow mock, UI variants, terminal logic model, or integration spike) when it would change a decision, before any heavy investment.
3. **Bootstrap** — installs `mattpocock-skills`, `amElnagdy/guard-skills`, `amElnagdy/review-skills` (optionally `codex-delegate`); writes worktree-isolated subagents with per-role model routing (`implementer`=Sonnet, `reviewer`/`spec-critic`=Opus, `researcher`/`test-runner`=Haiku), guardrail `settings.json`, and `docs/ai/{BRIEF,STATE,DECISIONS}.md`.
4. **Run** — Mode A (research → prototype → wayfinder/grill-with-docs → ADRs → to-spec → spec debate → to-tickets), Mode B (wave-based parallel implementation in git worktrees → debate-review + guards → squash-merge → test-runner), Mode C (fast lane for bugs/small features).
5. **AFK policy** — defers every question nothing depends on to `DECISIONS.md` with a reversible provisional choice, reorders work around blocked hard gates, batches questions, and stops cleanly with `/handoff` only when the whole frontier is blocked.

## When to use it

Invoke at the start of any new project, feature, refactor, migration, or bug batch — especially when you plan to hand the work to agents and step away. It also resumes: if `docs/ai/STATE.md` exists it skips the interview and continues.

## Install

```bash
# from this repo
npx skills add TamerElsherif/tamer-skills --skill delivery-orchestrator --agent claude-code
# or drop the folder into .claude/skills/ (project) or ~/.claude/skills/ (user)
```

Prerequisites in the target repo: git, `gh` authenticated, Node 18+ (for `npx skills`), Claude Code with subagents + worktrees.

## Use

```
/delivery-orchestrator
```
Answer the interview, approve the route, and either watch or go AFK. Everything the orchestrator needs from you lands in `docs/ai/STATE.md › For Tamer` and `docs/ai/DECISIONS.md`.

Optional one-time bootstrap by hand: `bash <skill-dir>/scripts/bootstrap.sh <repo>` then `/setup-matt-pocock-skills`.

## Examples
**Example 1 — brand-new app, nothing written**
Prompt: `/delivery-orchestrator` → "internal timesheet web app, general idea"
Result: 3 short interview rounds, offers a clickable HTML prototype, then research → grill-with-docs → ADRs → spec → spec debate → tickets → wave 1 implementers in worktrees; `docs/ai/BRIEF.md` and `STATE.md` written.

**Example 2 — PRD + 14 ready issues, going AFK**
Prompt: `Work through the ready issues while I'm away; only ask me about auth.`
Result: repo survey, autonomy contract (afk, auth reserved), tickets hardened, wave board, parallel implement → debate-review → merge; non-auth questions deferred to `DECISIONS.md`; `STATE.md › For Tamer` summary at the end.

**Example 3 — large refactor**
Prompt: `Refactor the monolith so billing can be extracted later.`
Result: improve-codebase-architecture → wayfinder map → ADRs (module boundaries = gate) → spec → tickets → execution.

## Layout

```
delivery-orchestrator/
├── SKILL.md                     # entry: resume check → interview → route → prototype → bootstrap → run → AFK rules
├── references/
│   ├── interview.md             # question tree by product type & stage, autonomy contract, repo survey
│   ├── prototype.md             # when/what/timebox, reaction round, AFK variant
│   ├── workflow.md              # Modes A/B/C, ticket hardening, waves, parallel-safety, review gate
│   ├── afk-policy.md            # decision classes, hard gates, reversibility rule, reordering, DECISIONS.md
│   └── model-routing.md         # per-role models and cost levers
├── assets/
│   ├── agents/                  # implementer, reviewer, spec-critic, researcher, test-runner, docs-writer
│   ├── settings.json            # worktree.baseRef=head, concurrency, git deny rules
│   ├── CLAUDE.orchestrator.md   # appended to the repo's CLAUDE.md
│   └── BRIEF.md · STATE.md · DECISIONS.md
├── scripts/bootstrap.sh         # idempotent repo setup
└── evals/evals.json
```

## Dependencies (installed by bootstrap)

- [mattpocock/skills](https://github.com/mattpocock/skills) — grill-with-docs, wayfinder, to-spec, to-tickets, tdd, code-review, research, prototype, diagnosing-bugs, resolving-merge-conflicts, handoff
- [amElnagdy/guard-skills](https://github.com/amElnagdy/guard-skills) — clean-code-guard, test-guard, docs-guard
- [amElnagdy/review-skills](https://github.com/amElnagdy/review-skills) — debate-review, babysit-pr
- [amElnagdy/delegate-skills](https://github.com/amElnagdy/delegate-skills) — codex-delegate (optional cross-vendor second opinion)

## Changelog
- 2026-09-12 — initial version
