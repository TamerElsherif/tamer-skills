# Prototype — buy certainty cheaply

A prototype exists to change a decision. If you cannot name the decision it will inform, do not build it.

## When to offer one

Offer (or, in AFK mode, just build) a prototype when stage ≤ "spec exists" **and** at least one of:
- The destination has a user-facing UI and the user has not seen anything yet
- A workflow has > 3 steps or branching states that are hard to describe in prose
- An integration is unproven (third-party API, device feature, legacy system, auth provider)
- Two architectures are plausible and a 1-hour spike would settle it
- The user's description contains words like "something like", "similar to", "you know the kind of thing"

Skip when: the user said no in the interview; stage is "tickets exist" or later; the change is internal with no UX or integration risk.

## Timebox

30–90 minutes of agent time, one implementer subagent, `isolation: worktree`, branch `proto/<slug>`. Never merged. Deleted after the reaction is captured (keep only `docs/ai/proto-<slug>.md`).

## Which kind

Use Matt Pocock's `prototype` skill (model-invoked) and pick the variant:

| Question to answer | Build |
|---|---|
| Does the flow/state make sense? | Single shareable HTML file with hard-coded data; every screen/state clickable |
| Which look & feel? | 2–3 radically different UI variants toggleable from one route — not shades of the same design |
| Does the business logic hold up? | Runnable terminal app with the domain model and a scripted scenario |
| Will integration X work? | Spike: smallest script that authenticates, calls the real API, and prints the result; note limits/latency |
| Can the architecture handle it? | Throwaway skeleton with the two candidate structures side by side, one request path each |

Per product type: web → HTML file or Vite scratch app; mobile → Expo/Flutter web preview or Figma-like HTML mock; desktop → HTML mock inside a bare Electron/Tauri shell only if native APIs are the question; API → OpenAPI stub + mock server; data pipeline → notebook or script over a 1 % sample.

## Reaction round

Ask exactly three things: What's wrong? What's missing? What should we NOT build? Record answers in `docs/ai/BRIEF.md` under `Prototype learnings` and feed them into `/grill-with-docs` or `/to-spec`.

In AFK mode: leave the three questions in `DECISIONS.md` as `deferred`, record your own reading of the prototype (what it proved/disproved), and continue to spec. The spec debate and the first wave's review gate are the safety net for a wrong reading.

## Anti-patterns

- Prototype code creeping into `main` "because it works"
- Adding tests, error handling, or auth to a prototype
- More than one prototype per open question
- Presenting a prototype without stating the decision it is meant to inform
