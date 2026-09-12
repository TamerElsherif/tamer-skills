# Model routing

Models are fixed per role in `assets/agents/*.md` frontmatter (`model:` accepts `fable`, `opus`, `sonnet`, `haiku`, or a full ID such as `claude-opus-5`). The orchestrator may override per invocation only for the escalation cases below.

| Role | Model | Why |
|---|---|---|
| Orchestrator (main session) | Fable 5.1 for Mode A; Opus 5 acceptable for long Mode B loops | Judgement-heavy, low output volume in planning; bookkeeping-heavy in execution |
| `spec-critic` | Opus 5 | Adversarial reasoning over a short doc, runs once or twice |
| `reviewer` / debate-review main | Opus 5 | Subtle spec drift and security issues are where cheaper models miss |
| debate-review second reviewer | Sonnet 5, or Codex via `codex-delegate` | Filters false positives; different vendor = independent failure modes |
| `implementer`, `docs-writer` | Sonnet 5 | Bulk of tokens; safe behind TDD + guards + review |
| `researcher`, `test-runner`, Explore | Haiku 4.5 | High volume, low judgement, summary output |

Escalate an implementer to Opus per invocation when: a ticket fails review twice, or its Scope includes auth, payments, or data migrations.

Cost levers, in order of impact: (1) implementer concurrency cap, (2) worker `maxTurns`, (3) report length limit (keeps orchestrator context small → fewer compactions), (4) Haiku for everything that only summarises, (5) `effort: medium` on implementers, `high` only on reviewers.

Never run two orchestrator-tier sessions on the same repo.
