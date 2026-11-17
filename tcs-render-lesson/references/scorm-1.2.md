# SCORM 1.2 packaging (target LMS: Tandrik — plain SCORM 1.2)

## Package layout
```
imsmanifest.xml
shared/scorm12.js            # asset resource "res-shared" (API adapter)
M1L1/index.html (+ media/, lesson.json)   # one SCO per lesson, depends on res-shared
M1L2/...
```
Organisation = course title → one item per curriculum module → one item per rendered lesson (SCO). Modules without a
rendered lesson are skipped; rendered lessons not in the curriculum are appended (warning). Titles follow the curriculum
primary language (`title_ar` when Arabic) unless `--lang` is given. XSD files are not bundled (most LMSs don't need them);
add `imscp_rootv1p1p2.xsd`, `imsmd_rootv1p2p1.xsd`, `adlcp_rootv1p2.xsd` at the zip root if an LMS insists.

## Runtime data model used
| Element | Written when |
|---|---|
| `LMSInitialize("")` | lesson load |
| `cmi.core.lesson_status` | `incomplete` on first launch; `passed`/`failed` when all scored items answered (quiz + assess sims) vs `pass_mark`; `completed` on the last page for lessons without scored items. Never downgraded from `passed`. |
| `cmi.core.score.raw/min/max` | raw = % of points (0–100), min 0, max 100 |
| `cmi.suspend_data` | JSON `{c: cursor, a: answers, k: checklist, p: branch path, b: branch score, d, v, x}`; trimmed to ≤ 4096 chars |
| `cmi.core.lesson_location` | current scene id |
| `cmi.core.exit` | `suspend` until complete, then `""` |
| `cmi.core.session_time` | on unload (HHHH:MM:SS.SS) |
| `LMSCommit` / `LMSFinish` | after each change / on pagehide |

Resume: when `cmi.core.entry` ≠ `ab-initio`, suspend_data restores the scene, answers and branch path.
Without an LMS API the lesson runs standalone and bookmarks to localStorage.
`adlcp:masteryscore` = quiz `pass_mark` (LMSs may set pass/fail from it too).

## Checks
1. `scripts/scorm_check.py pkg.zip` → manifest structure, ids, every file/href/dependency exists, SCO pages call
   LMSInitialize/LMSFinish/LMSSetValue/LMSCommit, no absolute paths. Must print `OK`.
2. `tests/test_runtime.py pkg.zip` → drives SCO M1L1 in a mock LMS (navigation, branching, quiz, score, resume).
3. Upload to the LMS sandbox (SCORM Cloud or Tandrik staging) before delivery; check status/score in the LMS report.

## Troubleshooting
| Symptom | Fix |
|---|---|
| Status stays "incomplete" | the learner must answer every scored item (final Knowledge check → "Your results") |
| Fonts differ in LMS | Google Fonts blocked → system fallbacks (Inter/Cairo stacks); bundle fonts if required |
| Score not stored | LMS opens SCO in a new window without `opener` API → enable "same window / frame" launch |
| Multi-SCO course shows one lesson | LMS flattens organisations → upload one zip per lesson (`--lesson-dir` single lesson) |
