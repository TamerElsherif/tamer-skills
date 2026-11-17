# tamer-skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) by Tamer ElSherif. One folder per skill; every folder has its own `README.md` with install and usage instructions.

| Skill | What it does |
|---|---|
| [delivery-orchestrator](./delivery-orchestrator) | Interview-driven kickoff and end-to-end orchestration for software work |
| [product-naming](product-naming/) | Find and clear a unique, trademark-friendly product name: tiered generation, live domain checks (RDAP), exact-word web search, competitor-collision and cross-language checks, ranked shortlist, name critiques |
| [push-to-tamer-skills](./push-to-tamer-skills) | Publish a skill to Tamer's personal skills repository github.com/TamerElsherif/tamer-skills |
| [rabet-podcast-studio](./rabet-podcast-studio) | Skill set for producing and publishing Rabet (رابط) Podcast content |
| [rabet-reels](./rabet-reels) | Produce 9:16 reels + thumbnails (and 16:9 YouTube episode thumbnails, titles and descriptions) from Rabet (راب… |
| [tcs-assessment](./tcs-assessment) | Builds the assessment for a lesson or course |
| [tcs-autopilot](./tcs-autopilot) | Fully automated course production with no questions |
| [tcs-curriculum](./tcs-curriculum) | Plans a course outline only |
| [tcs-format-branching](./tcs-format-branching) | Builds a choose-your-path scenario for a lesson |
| [tcs-format-cartoon](./tcs-format-cartoon) | Builds the cartoon-format scenes of a lesson storyboard |
| [tcs-format-comic](./tcs-format-comic) | Builds the comic-format scenes of a lesson storyboard |
| [tcs-format-doodle](./tcs-format-doodle) | Builds the doodle/whiteboard-format scenes of a lesson storyboard |
| [tcs-format-explainer](./tcs-format-explainer) | Builds the explainer-format scenes of a lesson storyboard |
| [tcs-format-job-aid](./tcs-format-job-aid) | Builds a job aid for a lesson |
| [tcs-format-mindmap](./tcs-format-mindmap) | Builds the mindmap-format scenes of a lesson storyboard |
| [tcs-format-narrated-deck](./tcs-format-narrated-deck) | Builds the narrated-deck format of a lesson storyboard |
| [tcs-format-screencast-sim](./tcs-format-screencast-sim) | Builds screencast and software-simulation scenes for a lesson |
| [tcs-format-series](./tcs-format-series) | Plans and builds an episodic training series with gamification and spaced reinforcement |
| [tcs-grounding-check](./tcs-grounding-check) | Audits a finished lesson for factual grounding |
| [tcs-localize](./tcs-localize) | Produces a second-language version of an existing lesson |
| [tcs-orchestrator](./tcs-orchestrator) | Interactive entry point for making training content end to end |
| [tcs-render-lesson](./tcs-render-lesson) | Renders a lesson's storyboard.json / quiz.json / curriculum.yaml into the NON-VIDEO deliverables |
| [tcs-render-openmontage](./tcs-render-openmontage) | Renders a lesson storyboard.json to MP4 through the user's local OpenMontage install (video_compose atelier re… |
| [tcs-render-remotion](./tcs-render-remotion) | Renders a lesson storyboard.json (or every lesson in a runs/<id> folder) to MP4 with the plugin's own standalo… |
| [tcs-scriptwriter](./tcs-scriptwriter) | Writes the spoken narration script for one lesson |
| [tcs-source-ingest](./tcs-source-ingest) | Turns the user's raw source material (PDF/Word/PowerPoint/Excel/Markdown/HTML files, folders, web pages, YouTu… |
| [tcs-storyboard](./tcs-storyboard) | Converts a finished lesson script into the render-agnostic `<lesson>.storyboard.json` |
| [training-content-studio](./training-content-studio) | Plugin (22 skills): Produce grounded training content on any subject |

## Install all skills at once

```sh
git clone git@github.com:TamerElsherif/tamer-skills.git ~/tamer-skills
mkdir -p ~/.claude/skills
for d in ~/tamer-skills/*/; do [ -f "$d/SKILL.md" ] && ln -sfn "$d" ~/.claude/skills/$(basename "$d"); done
```

`git pull` in `~/tamer-skills` updates every linked skill. To install a single skill, or into one project only, see that skill's README.

## Publishing convention (for every new skill)

1. Author the skill in its own folder: `SKILL.md` (frontmatter `name` + `description`, under 100 lines), `REFERENCE.md` / `EXAMPLES.md` when needed, `scripts/` for deterministic steps.
2. Add a `README.md` inside the folder: one-paragraph purpose, **Install** (personal and project-only), **Use** (three example prompts), **Files**.
3. Add a row to the table above.
4. Commit as `feat: <skill-name> skill` and push to `main`.
5. Link it into `~/.claude/skills/` on every machine that should have it.
