# Interview question tree

Rules: rounds of ≤ 4 questions; multiple choice where the answer space is finite; skip anything already known from the request, the repo survey, or `docs/ai/BRIEF.md`; stop when the route and the autonomy contract are unambiguous. Prefer questions whose answer changes what you will do next — never ask for completeness.

## Round 1 — orientation (always)

| # | Question | Options |
|---|---|---|
| 1 | New project or existing codebase? | New · Existing (path/repo) |
| 2 | What are we producing? | Web app · API/service · Mobile · Desktop · CLI · Library/SDK · Data/ML pipeline · Automation/integration · Browser extension · Other |
| 3 | Current stage? | General idea · Documented idea (PRD/notes) · Spec written · Tickets exist · Prototype exists · MVP live · Expanding a feature · Fixing bugs · Large refactor · Migration/port |
| 4 | What must be true at the end of this run? | free text → becomes `Destination` |

## Round 2 — branch on product type

Ask only the rows that change architecture or tooling decisions.

### Web app
- Rendering: SPA · SSR/SSG · MPA · "you decide"
- Who uses it: internal/employees · customers · public/anonymous
- Auth: existing IdP (Google Workspace / Entra ID / Okta) · email+password · social · none
- Hosting target: cloud (which) · on-prem/VM · container/Kubernetes · serverless · "you decide"
- Data: relational · document · existing DB (which) · none
- Expected scale (rough users/req/s) and any p95 latency budget

### API / service
- Consumers: internal services · partner · public
- Protocol: REST · GraphQL · gRPC · events/queue
- Multi-tenant? SLA? Rate limiting needed?

### Mobile
- Platform: Android native (Kotlin) · iOS native (Swift) · Cross-platform (Flutter · React Native · KMP · .NET MAUI · "you decide")
- Distribution: Play/App Store · enterprise/MDM · sideload/internal testing
- Offline-first? Push notifications? Device features (camera, BLE, GPS)?
- Backend: exists (URL/repo) · build alongside · none

### Desktop
- Framework: Electron · Tauri · native (which OS) · "you decide"
- OS targets, code signing/notarisation available?, auto-update needed?, installer type

### CLI / Library / SDK
- Language & runtime targets, distribution (npm/PyPI/binary), semver/API stability expectations

### Data / ML pipeline
- Batch vs streaming, data sources & volumes, orchestration (Airflow/Dagster/cron), where models are served, PII present?

### Automation / integration
- Systems involved (e.g. NetSuite, M365, Google Workspace, ServiceNow), trigger (schedule/webhook/manual), failure tolerance, idempotency needs

### Browser extension
- Browsers, Manifest V3 constraints, store publishing, permissions needed

## Round 2 — branch on stage

| Stage | Ask |
|---|---|
| General idea | Who is it for, the one core workflow, what exists today (spreadsheet? manual process?), 3 things it must NOT do |
| Documented idea | Where are the docs (paths/links)? Are they authoritative or aspirational? |
| Spec written | Path/issue of spec; was it reviewed by anyone? Any known gaps? |
| Tickets exist | Tracker + label/filter to pick them up; any ordering the user already knows; anything already in progress |
| Prototype exists | Path; what did it prove / disprove; is any of it keepable? |
| MVP live | Repo, deploy target, monitoring; what breaks if we're wrong (blast radius) |
| Expanding a feature | Feature description, modules it touches, is there a spec or just a request |
| Fixing bugs | Bug list source (issues/label/paste), repro availability, severity order, any that block others |
| Large refactor | Motivation (velocity? scale? cost? security?), what must not change (public API? DB schema? URLs?), test coverage today |
| Migration/port | From → to, hard cut-over or parallel run, data migration involved, deadline |

## Round 2 — constraints (ask once, all stages)

- Stack locks: "must use X" / "must not use Y" (default: reuse what the repo/company already runs)
- Deadline or milestone dates
- Budget cap for this run (tokens/$ or time) → sets the implementer concurrency cap
- Compliance/data handling: PII, regulated data, audit evidence needs (ISO 27001 / SOC 2 style controls → these become hard gates and ADRs)
- Tracker: GitHub Issues (default) · Linear · local files
- Deployment topology preference: monolith · modular monolith (default) · microservices (only with a stated reason) · serverless

## Round 3 — autonomy contract (always)

| Item | Options / default |
|---|---|
| AFK level | supervised · afk (default) · full-afk |
| Decisions the user insists on | free list; defaults to hard gates in `afk-policy.md` |
| Run box | "until done" · "stop after wave N" · "max ~N hours" · "max N implementer runs" |
| Prototype appetite | yes · no · only if it de-risks something (default) |
| Merge policy | orchestrator squash-merges after review (default) · open PRs only, human merges |
| Notification | where to leave the end-of-run summary (STATE.md + handoff by default) |

## Existing-codebase survey (run before Round 2)

```
cat README.md | head -80; ls; cat package.json pyproject.toml go.mod Cargo.toml 2>/dev/null | head -60
git log --oneline -30; git branch -a | head; ls .github/workflows docs/adr CONTEXT.md 2>/dev/null
ls test tests spec __tests__ 2>/dev/null | head; gh issue list --limit 30 2>/dev/null
```
Infer: language/framework, package manager, test/lint/typecheck commands, CI, default branch, whether Matt Pocock setup exists, open tickets. Present inferences in ≤ 6 lines and ask only for corrections.

## Output — `docs/ai/BRIEF.md`

Use `assets/BRIEF.md`. It must contain: Destination, product type + key type-specific answers, stage, route chosen, constraints, autonomy contract, prototype decision, and the survey inferences (for existing repos).
