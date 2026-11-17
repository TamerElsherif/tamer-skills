# Template guide (enums.templates → when + required props)

Props are validated by `schemas/storyboard.schema.json` (`allOf` per template). Cues: list items reveal on cue(i)
in order unless the props carry explicit `cue` fields. `*` = required.

| Template | Use for | Key props (* required) | Cues |
|---|---|---|---|
| title | lesson/part opener | *title, kicker, sub, part, icon | — |
| section | module/part divider | *title, n, sub, icon | — |
| bullets | 2–6 rules/points | *title, *items[{*text, sub, icon, tone}] ≤6, kicker, side_broll, dark | 1 per item |
| icon_grid | categories, types, examples | *title, *items[{*icon, *label, sub, tone}] ≤6, cols | 1 per item |
| steps | ordered procedure ≤ 6 | *title, *steps[{*label, sub, icon}], danger | 1 per step |
| process_flow | branching process / approvals | *title, *nodes[{*id,*label,kind}], edges[{from,to,label}] | nodes in order |
| timeline | dates, sequence of events | *title, *events[{when, *label, sub}] | 1 per event |
| do_dont | mistakes vs right way | *title, *dont[], *do[], dont_head, do_head | dont items, then do items |
| comparison | A vs B (not good/bad) | *left{head,items}, *right{head,items}, title | left then right |
| stat | one striking number | *value (number), *label, prefix, suffix, source, icon | count-up on cue 0 |
| definition | a term | *term, *def, note, icon | def cue0, note cue1 |
| statement | one sentence/quote | *text, accent, sub, icon, light | — |
| table | ≤ 6 rows reference data | *columns, *rows | — |
| checklist | recap, readiness check | *title, *items ≤ 7 | 1 per item |
| quiz | knowledge check in video | *quiz_item (quiz.json id), q, options, answer (index), why | answer cue0 |
| flashcard | term ↔ meaning | *front, *back, icon | flip cue0 |
| outro | close + action | *line, title, tips[], evidence_line | — |
| broll | full-bleed stock clip | *shot (broll_shots id), chips ≤ 2, dim | — |
| broll_panel | clip + frosted list | *shot, *title, *items ≤ 5, side | 1 per item |
| image | generated illustration | *image (generated_images id), caption, chips | — |
| email_mock | phishing/emails | *email{*from,*subject,*body[],from_addr,to,attachment,button,signature,external}, callouts[{*cue,*target,*label,tone}] | callouts |
| chat_mock | SMS/Teams/WhatsApp-style | *messages[{*text, me, warn, cue}], device, title, callouts | messages/callouts |
| browser_mock | websites, fake logins | *url, bad, page, brand, heading, lines, callouts[{cue,label,target}] | callouts |
| mfa_prompt | MFA fatigue/push | app, place, count_to, caption | — |
| popup | warnings, scareware, toasts | *title, *body, cta, tone, icon | — |
| code_mock | config/code/logs | *lines, title, filename, highlight[{cue,line,label}] | highlights |
| screencast | simulated app walkthrough | *app{*kind, title, fields[]}, *actions[{*cue,*do,target,value,label}] | actions |
| cartoon | story scene with personas | *set, *people[{*cast,pose,expr,x,y,s,holding}] ≤5, beats[{cue,cast,pose,expr,move_to,camera}], bubbles[{cue,who,text}], overlay | beats/bubbles |
| whiteboard | doodle/ink build-up | *items[{*cue,*kind,text,icon,cast,x,y,…}], title | items |
| comic | 1–4 panels | *panels[{*set,*people,caption,bubbles[{who,text}],sfx_word,cue}], layout | panel cues |
| mindmap | concept map | *root, *nodes[{*id,*label,*parent,*cue}], focus[{cue,node}] | nodes |
| decision | branching choice | *prompt, *choices[{*id,*label,*next,correct}] 2–4, video_choice | — |

## Picking rules
- Match the beat (scriptwriter `beat`/`template:` hint) first; then vary: never 3 identical templates in a row.
- Explainers: alternate b-roll/broll_panel with boards every 8–20 s; mock-ups for anything the learner will see on a screen.
- Story formats: `cartoon`/`comic` for story beats, info templates for teaching beats; a persona present on teaching boards via
  `overlay` or the next cartoon scene keeps continuity.
- Numbers: one hero number → `stat`; several → `table`/`bullets`. Prefer the exact source figure; `source` prop names the doc.
- ≤ 6 items per board (checklist 7). More → split into two scenes ("Rules 1/2", "Rules 2/2").
- Text sizes: title ≤ 60 chars, item ≤ 70 chars (≥ 24 px at 1080p); write labels, not sentences.
- Mock-ups: fictional senders/domains (northwind-co.example, contoso-style invented names), never real brands or people.
- Icons: names from `kit/Icons` (lucide subset, e.g. mail lock key shield phone alert user users invoice calendar camera
  smartphone file upload check x flag clock globe laptop money card link). Unknown names fall back to a dot in the kit.
- Vertical (9:16): ≤ 4 items per board, larger type, cartoon `s` 1.2–1.5, avoid `table`/`comparison`.
