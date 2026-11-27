# storytelling-techniques

A library of storytelling mechanics and a way to apply them to a speaker's own stories without changing
their voice. The first entry is the Chappelle method: dialogue instead of labels, an expectation then a
turn, specific detail, and the five beats Setup → Escalation → Turn → Peak → Button.

## What it's for
Most stories in talks and reels are told as a summary: "my uncle was stingy", "I was under a lot of pressure".
This skill turns a real story into one that lands: it maps it onto five beats, replaces labels with dialogue
and adjectives with exact details, finds the turn, and writes the Button. It also reviews stories in scripts
and rehearsal recordings, and grows the library when you share a video about another storyteller's method.

## When to use it
- Writing or rewriting a story for a talk, lecture, podcast, reel or post
- Choosing an opening story or hook
- Reviewing a story in a script or a rehearsal ("the story fell flat, why?")
- Adding a new technique source (a video or article about how someone tells stories)
- **Not for:** inventing stories or details that didn't happen; copying a comedian's material or persona.

## Install
```bash
npx skills add TamerElsherif/tamer-skills --skill storytelling-techniques --agent claude-code
# recommended alongside:
npx skills add TamerElsherif/tamer-skills --skill speaking-style --agent claude-code
npx skills add TamerElsherif/tamer-skills --skill public-speaking-coach --agent claude-code
# manual: copy the folder to .claude/skills/ (project) or ~/.claude/skills/ (user)
```

## How to use
- **Rewrite:** "Here's my story about X, I'll tell it in a 20-minute stage talk to make the point Y." Claude
  reads your speaking profile (if you have one), maps the story to the five beats, asks for missing true
  details, and returns a beat table with timings plus the story written your way, marked with pauses, stress,
  voiced lines and volume cues. Saved under `projects/speaking-coach/<talk>/stories/` or `projects/storytelling/stories/`.
- **Review:** paste the script section or give a rehearsal recording (uses public-speaking-coach's
  `review_take.py`); you get at most 3 fixes with line or timestamp.
- **Add a source:** share a link; Claude saves the video locally, transcribes it, reads the on-screen text, and
  writes `references/<name>-method.md` in the same format.
- **Inputs:** the story (text or recording), its purpose, setting and length; optional speaker profile.
- **Outputs:** marked story file, beat table, alternative Turn/Button; or a review; or a new reference file.

## Examples
**Example 1:** `احكيلي قصة الـ Task الشهرية بتاعة 2001 بطريقة Chappelle، 90 ثانية على stage`
Result: Setup/Escalation/Turn/Peak/Button table, questions for the missing details, and a marked Egyptian-Arabic version.

**Example 2:** `Review the opening story in my script`
Result: which beats are missing, labels to turn into dialogue, where the pause before the turn goes, the Button line.

**Example 3:** `Analyze this reel about how X tells stories and add it to the library`
Result: a new `references/x-method.md` and an updated library list.

## Layout
```
storytelling-techniques/
├── SKILL.md                       # rules, rewrite / review / add-source workflows, library index
├── README.md                      # this file
└── references/
    └── chappelle-method.md        # the 4 tools + 5 beats, examples, stage delivery, fit with the speaker profile
```

## Dependencies
- Optional: [speaking-style](../speaking-style) for the speaker profile; [public-speaking-coach](../public-speaking-coach) for rehearsal reviews
- For adding sources: ffmpeg, faster-whisper

## Changelog
- 2026-11-27: initial version with the Chappelle method
