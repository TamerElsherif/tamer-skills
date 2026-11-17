# Comic / webtoon playbook

## When to use
- Short scenarios that must work **without audio** (intranet, posters, mobile reading, printed handouts).
- Physical-security and etiquette topics (tailgating, clear desk, visitor handling) and quick "spot the mistake" stories.
- Avoid for multi-step procedures (screencast-sim) or abstract mechanisms (doodle).

## Duration / size
| Variant | Panels | Read time | Motion comic |
|---|---|---|---|
| Strip | 3–4 | 20–40 s | 30–60 s |
| Page set | 6–8 | 1–2 min | 1.5–2.5 min |
| Webtoon episode (9:16) | 9–12 | 2–3 min | 2–3 min |

## Beat structure (6–8 panels)
| # | Beat | Panels | Layout |
|---|---|---|---|
| 1 | Title card | — | `title` scene |
| 2 | Situation (wide) | 1 | `1+2` first panel or `3-row` row 1 |
| 3 | Pressure / temptation | 1–2 | |
| 4 | Wrong move + consequence | 1–2 | |
| 5 | Rewind: right move | 2–3 | new page, same set |
| 6 | Rule | — | `do_dont` / `checklist` |
| 7 | Check | — | `quiz` |

## Layout picks
| Layout | Aspect | Use |
|---|---|---|
| `3-row` | 9:16 | webtoon scroll, one beat per row |
| `1+2` | 9:16 / 16:9 | establishing shot + two reactions |
| `2x2` | 16:9 / 1:1 | classic 4-panel gag |
| `3` / `2` | 16:9 | horizontal strip |
| `1` | any | splash / reveal |

## Panel craft
- Vary shot size: wide (s 0.8, people small) → medium (s 1.0) → close (s 1.3, one person).
- Balloon text ≤ 12 words; caption box top-left (top-right in RTL).
- `sfx_word` for one onomatopoeia per page max ("CLICK", "BUZZ") — it is on-screen text; translate it.
- Keep the same set across a rewind so the contrast is obvious.

## Do / Don't
| Do | Don't |
|---|---|
| One action per panel | Two events in one panel |
| Show consequence, then rewind | Moralise in long captions |
| Diverse, neutral personas | Real people, brands, uniforms of real firms |
| Translate captions, balloons, sfx words | Leave English sfx in Arabic pages |

## Worked example (`templates/example.storyboard.json`)
"The Friendly Tailgater" (9:16): page 1 `3-row` (courier with boxes → "hold the door?" → inside, "Too easy." + CLICK);
page 2 `1+2` rewind (learner points to reception → manager confirms → cheer); `do_dont`; `outro`.
