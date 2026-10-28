---
name: rabet-reels
description: Produce 9:16 reels + thumbnails (and 16:9 YouTube episode thumbnails, titles and descriptions) from Rabet (رابط) Podcast episodes — Egyptian Arabic mixed with English, B2B tech audience — and schedule them on Postiz. Use when the user asks to cut, style, caption, or thumbnail a Rabet clip, references the Rabet clip sheet, a "Final Clip ID", says "make the next reel", or wants reels drafted/scheduled across LinkedIn, YouTube Shorts, Facebook, Instagram and TikTok, or asks for a full-episode YouTube thumbnail, title, description, chapters or hashtags. Data-driven: a reel is a reel_spec.json + one beats file per style; scripts and HyperFrames templates do the rest.
---

# Rabet Reels

> v1.0 (2026-10-28): reel ends checked past the end (`tail_check.py`, rule 18) after a partner review found five reels cut mid-thought; fixing shipped reels (§9). v0.9 (2026-10-28): episode thumbnails (`make_episode_thumbs.py`) + YouTube description recipe (§8); Facebook link in the first comment (rule 17). v0.7 (2026-10-23): surgical cuts (`cutsafe.py`, rule 13) and an edge check before delivery. v0.4 (2026-10-17): Whisper + mattes on the RTX 5050. v0.3 (2026-10-16): Episode 2 clips 05–12 shipped from this pipeline (HQ multicam master, Postiz campaign).
> Per-user settings (output folder, Postiz URL/token, channel ids) live in `~/.rabet-reels.json` — copy
> `config.example.json`. Never hard-code them in the skill.
> **ONE reel per sheet topic** — never three variants. **Style: always S1 Clean** (user decision, 24 Oct 2026 —
> S2 Split / S3 Bold only if the user asks). Pick the thumbnail by content + B2B audience (T1–T3 are user-approved).

### Style / thumbnail choice
| Content | Style | Thumb |
|---|---|---|
| Calm advice, checklists, "how we work" | S1 Clean (side stacks) | T1 big two-line question/claim |
| Step-by-step teaching, frameworks, lists | S2 Split (panels; no matte → fastest, most robust) | T3 editorial quote |
| Punchy / contrarian / quotable framework | S3 Bold (box groups) | T2 cinematic BG + cutout |
The style column is kept for reference only: every reel now ships in S1 Clean. Alternate guests across a campaign so the feed doesn't repeat.

## 0. Inputs

| Input | Where |
|---|---|
| Clip list | The user's clip sheet (Google Sheet "Reels", link from the user; Drive `read_file_content`). Columns: Final Clip ID, Member, Eps, up to 3 start/end ranges, Topic, flags, Status, Reel Link |
| Episodes | HQ episode master from the user (multicam, cuts between cameras). If sheet times come from an earlier cut, find the constant offset by audio cross-correlation (Ep 2: +51.36 s) |
| Output | `output_dir` from `~/.rabet-reels.json`: `ReelNN_<Title>.mp4` + `_cover.mp4` + `ReelNN_thumbnail.png` |
| Brand | The user's brand-identity folder · named photos of hosts and guests |
| Names | Ep 3 titles: تامر الشريف — IT & AI Transformation Expert · حسام عزت — Software Engineering Advocate · هيثم فؤاد — Founder - prodXeed. Use the name the user gives, not photo file names (Ep 2 guest: «م. خالد ناصر الدين — مستشار التسويق الإستراتيجي»; host: هيثم فؤاد). The episode is «الحلقة الثانية» — check the episode number before writing captions |

## 1. Rules (from the user — do not regress)

1. **Hook in the first 1–3 s** (H1 bold claim cold-open / H2 quoted misconception / H3 open question). Never invent claims.
2. **Graphics never cover the speaker's face.** Place them beside, above, below, or *behind* the speaker. Anything that touches the head goes on the **behind layer** (between plate and matte). Keep it identifiable: lay side graphics in the clear wall zone (S1: x 40–420, y 300–850, above the mic — the matte includes the mic).
3. **Rabet logo**: ~130 px (videos) / ~175 px (thumbnails), placed high (top ≈ 120–150 px).
4. **Matte edges must be clean** (no halo/slop around the head) → always `refine_matte.py` (head-crop matte + choke), never the raw full-frame matte.
5. SFX only, no music. Full-episode CTA «الحلقة كاملة على YouTube» + the channel link `youtube.com/@RabetPodcast` (beats `ytUrl` overrides); no «مع …» guest line (user, 2026-10-23). Name card once, early, below/beside the face, **timed on a shot where the named speaker is on screen** (check `media/shots.json`).
6. Mixed script: English terms in Latin (glossary), every "marketing" form → Latin `Marketing` («بالـ Marketing»).
7. Tighten pauses; alternate framing (1.0 ↔ 1.08) on every join; punch-in + impact at the turn.
8. **RTL**: never start a line/headline with an English word; big wrapped headlines carry no English (bidi reorders it) — put English in its own box or mid-line. Captions/posts: RLM (U+200F) at each Arabic line start.
9. **Complete ideas only (start and end).** A reel ends on the end of a sentence/idea, never on the first words of the next one (Ep 2 reel 05 ended on «السوق ده Market Research» before the outro — cut before it). It also starts on a sentence start, not on a stammer or a trailing «ف/كده/أو». Before rendering, read the last 5 s and the first 3 s of the A-roll transcript; move `range` ends to a word boundary from the wide transcript (end ≥ last word's end, < next word's start).
10. **Hooks are a complete micro-idea.** Never end a hook on «أو / و / ف…» or start it with «كده / فالحقيقة», and never let it run into the next sentence. Hook range = first word's start → last word's end; check that no next word starts before the hook end (even 0.05 s of it is audible). The story after the hook must not read as the hook continuing: every template plays a **brand wipe** over the hook→story cut (`#hookwipe`, automatic when `hookEnd > 0`) — keep the `@hookEnd` whoosh with it.
11. **Effects sit under the voice.** SFX only, no music; `assemble.py` multiplies every cue by `sfxGain` (house default **0.6**; per-reel `content.sfxGain`, or `RABET_SFX_GAIN`). Don't raise individual `vol` values to compensate.
12. S3 palette is **cool**: deep navy grid (aqua lines) → near-black grid (orange lines) at the turn. Orange = accent only.
13. **Surgical cuts: never cut inside a word.** Sheet times are whole seconds and Whisper word edges drift 50–300 ms, so neither is a cut point. Every in/out, jump cut and removed pause goes through `scripts/cutsafe.py`. It places each cut in a real acoustic gap: full-band and high-frequency level both dip, so a final "s" counts as speech. Outs use the first gap after the last kept word that follows real speech. Ins use the last gap before the first kept word. Use `on_grid` for the frame. `build_aroll.py` does this automatically.
    - Never pick the deepest dip. A deeper pause after the next word swallows that word (teaser v2: «costs» was cut at 54.44; the real gap was 54.57).
    - When cutsafe raises `CutError`, the words run together. End at another phrase break; don't force the cut.
    - Cut audio exactly at the gap, not trimmed to the frame grid.
    - Never drop a short leftover part; keep that pause instead.
    - Before delivery, run the isolated edge check: transcribe every kept part on its own with 1 s of silence around it, and confirm its first and last words are whole (`scripts/edge_check.py <source> <cuts.json | aroll_<style>.segments.json>`).
    - Don't cut inside a sentence unless the dropped part is redundant or off-topic.
    - When a speaker's last word runs straight into the next speaker's first word (no gap), `safe_out` prints "kept" and leaves the cut **inside** the word (Ep 3 Reel23 ended on «كا-» of «كاش» before Hossam's «طيب»). Never ship a "kept" end: find the gap with `tail_check.py` and set it in `exact_ends`.
    - Check **both** edges. An end in continuous speech can make `safe_out` find "the first gap" inside the next word, and `safe_in` reaches up to 0.5 s back, which can pull in the previous speaker's last word. When the edge check hears a fragment, set the measured time in the spec: `exact_ends` / `exact_starts` (`build_aroll.py` uses those values as given).
14. **Cover versions only** (user, 2026-10-23): ship `ReelNN_<Title>_cover.mp4` (thumbnail as a 1.2 s intro) + `ReelNN_thumbnail.png`; no plain copy. Stories get the cover version too.
15. **S1 Clean is the default style** (user preferred it over S2 Split for Ep 3). When speakers fill the 9:16 frame there is no free wall: put **short stacks (≤ 3 lines) on the shirt**, `front: true`, `top ≈ 930`, `stackLeft 150`, `stackWidth 780`, and `nameClear: true` so no stack shares the name card's moment. The hook **hero word sits above the head** (`#hero` top 40 px, 170 px; `heroTop` / `heroSize` knobs), never mostly hidden behind it.
16. **Keep every reel's final transcript** (from its corrected captions, body only) for the Reels sheet's `Transcript` column.
17. **No YouTube link in Facebook / LinkedIn post text** (user, 2026-10-26: links cut the reach). The text ends with «الحلقة كاملة على YouTube، اللينك في أول كومنت 👇» (before the hashtags) and the link becomes the **first comment** («الحلقة كاملة على YouTube:» + link). Existing posts: rebuild from the current server text and tags, create the replacement, then delete the old one with the same date, state, media and later comments.
18. **Listen past the end before building** (partner review, 2026-10-28: 5 of 13 Haitham reels in Ep 3 ended early). Sheet ends are whole seconds picked by ear, and the episode transcript **drops words** (Haitham's section), so a snapped end can be mid-sentence. For every range end, run `scripts/tail_check.py <source> <end>`. It runs its own Whisper pass and shows 15 s past the end, plus the real pauses with the words on each side. Extend the end while the next words continue the thought: «علشان / عشان / لكن / بس / ف… / على مستوى…», the second half of «X ولا Y», or a parallel «طب بالنسبة لـ…» that answers the same question. Stop at a speaker change, a new question or a new topic. Then `--cut T` checks both sides in isolation: the before part ends on the whole last word, the after part starts on the next word.
    Partner time stamps may come from the **low-quality** episode file (Ep 3: 13.4 s shorter, −6.36 s at 10 min, not constant). Map them by transcribing the same line in both files.
    After the render, the reel's **last caption** must be the last spoken word. A wide-transcript word that straddles the final cut can vanish, and a phantom next word («على») can show instead (Reel32). Compare with the cut's own transcript and use `own_words` when it's clean.

## 2. Fast path for the next reel (≈ 15 min hands-on + ~25 min machine time)

```
projects/<episode>-reels/reels/clipNN/
  reel_spec.json     # source, range [abs s], drop_ranges, hooks per style   (copy clip05's)
  beats_s1.json      # anchors (word-based), content texts, sfx              (copy + edit)
  beats_s2.json
  beats_s3.json
  extra/             # reel-specific files copied into assets (e.g. SDR B-roll)
```
1. Read the sheet row → set `range` (extend a few s to include the set-up question / finish the sentence) and per-style `hook` ranges (find candidates in the wide transcript).
2. `bash .claude/skills/rabet-reels/scripts/pipeline.sh <reel_dir> aroll` → check segment list; add `drop_ranges` for breaths/fillers.
3. `pipeline.sh <reel_dir> words` (GPU large-v3, ~20 s per A-roll) — then `pipeline.sh <reel_dir> matte` in the background.
4. Write the beats files: anchors reference **words** (`{"word":"Sales"}`, `{"word":"الناس","n":2}`, `{"word":"X","in":"hook"}`, `{"after":"id","offset":0.4}`, `{"time":0.6}`). `make_reel_data.py` fails loudly on a missing anchor.
5. Snapshot-check (assemble then `npx hyperframes snapshot --at … --no-proxy`), fix, then `pipeline.sh <reel_dir> render` → `deliver/`.
6. Pull frames from the **rendered** MP4 (`deliver/sheet_<tpl>.jpg`) before calling it done.
7. Thumbnail: `thumb.json` → `python scripts/make_thumb.py thumb.json thumb.png`.
8. Ship: `scripts/finish.sh <reel_dir> NN <tpl> <Title>` = copy to `output_dir` + `add_cover.py` (1.2 s thumb intro + whoosh) + `postiz_upload.py`.
9. Posts: captions JSON (one entry per reel id; fields listed in `postiz_payload.py`; humanize, Egyptian Arabic + English terms) →
   `postiz_payload.py <captions> NN uploads.json <clean> <cover> YYYY-MM-DD payload.json [draft|schedule]` → `postiz_drafts.py payload.json NN posts.csv`.

### Multicam auto-framing (HQ master)
`reel_spec` crop `auto-vertical` / `auto-split`: `shots.py` finds camera cuts (scene>0.25) and the face x per shot (Haar, OpenCV **4.x** — 5.x has no CascadeClassifier); `build_aroll.py` splits pieces at cuts and crops each with the face at 60 % (vertical) / 55 % (split). Multi-range clips: `"ranges": [[a,b],[c,d]]`.
S1 placement knobs (beats `content`): `stackLeft`/`stackWidth` (all stacks) and per-stack `left`/`width`/`top`/`front:true` (front = drawn over the body, use only below the face, e.g. top ≈ 930 on the shirt). Haitham sits large and left: `stackLeft 22, stackWidth 292, zoom [1,1.04]`, no `hero`. Snapshot every stack's peak before rendering.
Overlays animated with GSAP `xPercent`/`x` must not also carry a CSS `transform` (GSAP adds its own on top: the hook wipe once parked on screen and covered the whole story). Position them only through `tl.set(...)` at t=0. A render needs several GB of free temp space on C: (S3 ≈ 4 GB of captured frames); a full disk fails at "capture_disk".
Caption chunks shorter than the pop-in tween used to stick on screen forever in S3 ("ghost" glyphs over later captions; snapshots don't show it). Fixed in the template; if you see overlapping caption glyphs in a render, look for caps with `e - s < 0.12`.
S1 stack lines never wrap (template shrinks the font to fit 400 px) — a wrapped mixed line pushes English to a line start.
S1 opt-in knobs (content): `titlePlate` (dark plate behind stack titles — light shirts), `capTop` (caption y, default 1260), `capWide` (wider caption pill for long English runs). Spec `exact_starts` / builder `hook_start_exact`: measured cut starts that cutsafe must not move. A lone «الـ» caption chunk always merges into the next one.
Transcripts: GPU large-v3 sometimes **drops words** in a cut A-roll (Ep 2 reels 10/11 lost «SaaS / Customer Success / scale-ups»). If captions miss words or anchors fail, caption from the wide transcript (`wide_words`); words that start in a cut gap snap to the next piece, and «ال -development» / «ن -implement» forms are normalised to «الـ Development».
Multicam layout: cut-ins of the other person put their head higher (top ≈ y 590 of 1920). Keep S3 groups ending above ≈ y 560: max 3 lines (sizes ≤ 80 after a 120+ headline), merge list items («الأوتوبيس · الترام») or split a long list into two groups. Check every reaction shot in the sheet.
Beats extras: `extra_words` (inject words into segments), `wide_words {"file","offset"}` (use the wide transcript when the cut-A-roll transcript is poor).

## 3. What each piece does

| File | Role |
|---|---|
| `scripts/build_aroll.py` | speech islands via silencedetect → drop tiny/filler/`drop_ranges` → pad/merge → hook + body → every edge moved into a real word gap (`cutsafe.py`) → quieter neighbouring frame, 12 ms fades |
| `scripts/cutsafe.py` | surgical cut points: full-band + high-frequency gap finder (`Env.snap_in/snap_out/safe_in/safe_out/on_grid/pauses`); raises `CutError` when words run together |
| `scripts/tail_check.py` | pre-build check of a range end/start: own Whisper pass 15 s past it (source times), real pauses with the words around them, `--cut T` isolated before/after check (rule 18) |
| `scripts/edge_check.py` | pre-delivery check: transcribes every kept part on its own and lists its words with offsets, so a clipped edge word shows |
| `scripts/transcribe_words.py` | Whisper large-v3 on GPU (float16) word timings in output time; prints the device and warns on CPU fallback |
| `scripts/glossary.json` | Whisper spelling fixes, English phrase map, `break_before` / `break_after` / `no_end` caption rules — **grow it every reel** |
| `scripts/make_reel_data.py` | captions (phrase-aware chunks ≤3 words, segment-by-midpoint +0.1 s bias, stretched-word pauses), joins, anchors → `reel-data.js` |
| `scripts/gpu_matte.py` | GPU speaker mask: same u2net_human_seg model + pre/post-processing as `hyperframes remove-background`, via onnxruntime-gpu (~10× faster); lossless gray `.mkv` |
| `scripts/refine_matte.py` | head-crop matte (finer detail) [+ full-body matte], 2× erosion + feather, original RGB re-attached, reuses existing passes |
| `scripts/assemble.py` | stamps template (`{{DURATION}}`, `{{AROLL_DUR}}`, SFX `<audio>` lanes, B-roll window), audio-only `vo.wav`, copies assets/extra |
| `scripts/pipeline.sh` + `styles.json` | one-command stages; style → template + matte needs |
| `templates/s1-clean` | plate cam / **behind layer** / cut-out cam / front; hero word behind head; myth cards+strike; order chips; triangle diagram; checklist; pulses |
| `templates/s2-split` | cream board scenes: question · myth cards+quote+stamp · RTL timeline · triangle+lens · checklist · base link; speaker panel; seam captions + progress rail |
| `templates/s3-bold` | generic **box groups** (`groups[]`: lines with style/anchor/anim, exits), x-marks, pulses, polaroid B-roll, flip; speaker cut-out with white outline |
| `scripts/shots.py` | camera-cut detection + face x per shot (cached `media/shots.json`) |
| `scripts/make_thumb.py` + `templates/thumb` | parametric thumbnail (T1/T2/T3 via thumb.json: l1/l2/l1html, kicker, stamp, bg, cutout) |
| `scripts/add_cover.py` | thumbnail as 1.2 s intro (platforms with no cover setting) |
| `scripts/postiz_upload.py` / `postiz_payload.py` / `postiz_drafts.py` | media upload (public API) → 12-post payload per reel → posts via the Postiz MCP endpoint (JSON-RPC; needs a curl User-Agent or Cloudflare 403s) |
| `scripts/config.py` + `config.example.json` | per-user settings loader (`~/.rabet-reels.json`): output folder, Postiz URL/token, channel ids |
| `scripts/finish.sh` | ship one reel: copy to `output_dir`, build the cover version, upload both to Postiz |
| `scripts/make_episode_thumbs.py` | 16:9 YouTube episode thumbnails A/B/C (1280×720) for 2–3 guests from a spec JSON (§8) |
| `templates/thumbs` | T1 cut-out+bold · T2 cinematic · T3 minimal (1080×1920, key content in centre 4:5) |

Beats `content` keys per template are read directly by the template script — open the template's `<script>` to see every supported key.

## 4. Brand

navy `#10335A` · deep `#0B2340` · teal `#1AAAC1` · aqua `#07C3BE` · orange `#FF6600` · cream `#FDF9F5` · teal text on cream `#0E7487` (WCAG). Logo motif = 3 nodes + links; 3-part ideas close into the Rabet triangle. Fonts self-hosted in `assets/fonts` (Alexandria variable, Lalezar; Archivo Black is bundled by HyperFrames). No coloured glow shadows.

## 5. Machine facts / gotchas (this PC)

- Whisper runs on the RTX 5050 (CTranslate2, float16; ~20 s per 40 s A-roll incl. model load). CTranslate2 is built for CUDA 12: `cublas64_12.dll` + `cublasLt64_12.dll` (pip `nvidia-cublas-cu12`) must sit in `.venv/Lib/site-packages/ctranslate2/` — re-copy from `nvidia/cublas/bin` after any ctranslate2/faster-whisper reinstall. If the script prints `WARNING: GPU failed`, that's why. Never run two large-v3 jobs or transcribe during a render (RAM).
- `hyperframes remove-background` is CPU-only on Windows (onnxruntime-node has no CUDA backend; `--device cuda` + `HYPERFRAMES_CUDA=1` silently runs on CPU while logging "CUDA"). `refine_matte.py` therefore uses `gpu_matte.py` (onnxruntime-gpu + pip `nvidia-cudnn-cu12` etc., ~0.1 s/frame) and falls back to HyperFrames only if that fails. Matte only styles that need it; S1 needs head region only.
- **Stock B-roll may be HDR** (iPhone PQ). One HDR clip → whole render dims, alpha lost, 10+ min. Tone-map to BT.709 and always render with `--sdr`.
- Never point an `<audio>` at an `.mp4` — use the WAV `assemble.py` makes (mp4 audio sources were drawn as a picture layer).
- `snapshot` needs `--no-proxy` (alpha WebM proxy hangs); templates set `media.autoProxy: false`.
- Google-font auto-embed fetched only the Latin subset of Alexandria → self-host fonts.
- English words inside RTL captions: one LTR run per English phrase; caption lines are flex rows with a gap (inline spacing collapsed).
- Generated ffmpeg sources need explicit `d=`; `geq` per-frame is very slow → render masks once as PNG.
- Paid image gen `flux_image` (fal) 403'd on 2026-10-16 — ask before switching provider.
- Torn-paper edge is a `clip-path` polygon — upgrade to a real torn-paper PNG some day.
- Render times: S2 ≈ 1.5–2 min / 45 s, S1 ≈ 3–4 min, S3 ≈ 4–6 min (alpha cut-out + outline filter).
- ffmpeg 8 removed `-filter_complex_script` → `-/filter_complex <file>`.
- `pipeline.sh` runs under Git Bash but calls Windows Python: it passes `pwd -W` paths, never `/d/...`. Python = `$RABET_PY`, else `./.venv`, else `python`.
- Full `hyperframes check` times out on 60 s+ reels → check in 15 s ranges (`--range a,b --samples 4`).
- Mattes: ~10 fps on GPU (a 45 s pass ≈ 2 min); the final VP9-alpha encode stays on CPU (NVENC has no alpha). Captures ~20–25 min for S1/S3 and are the bottleneck now: headless Chrome gets the Intel iGPU (Windows hybrid graphics), and `render --gpu` (NVENC) gave no speed-up (encode is ~10 % of a render) — don't add it.

- **A-roll memory:** trimming many pieces from one long 4K input made ffmpeg buffer every later piece (19 GB commit, crashes). `build_aroll.py` now gives each piece its own seeked input.
- **Render cache:** HyperFrames caches extracted frames in `%TEMP%` (GBs per reel, C: filled up). Point `TEMP`/`TMP` at a D: folder for batch renders and clear `hyperframes-extract-cache-*` after each reel. Two parallel render chains need **separate** temp folders (one chain's cleanup kills the other's render).
- **Whisper on short cuts** sometimes hallucinates (English "translations", other scripts) or mishears English as Arabic letters. Compare the cut's own transcript with the episode transcript and use the better one (`wide_words`), map the glitches in `fixes`, and prefer `contains` anchors for words Whisper spells differently between runs.
- **Captions:** adjacent English words are merged into one caption token (separate LTR spans display reversed, «Point Pain»); a chunk never ends on a prefix («الـ», «بالـ») and the hook never shares a chunk with the body (`make_reel_data.py`).

## 6. Postiz (self-hosted or cloud)
- Default to **drafts** (`draft`) for user review; switch to `schedule` only when the user says so. URL/token from `~/.rabet-reels.json` (`postiz_token_file` may hold the `claude mcp add … Bearer …` line); never print the token.
- To change existing posts (new video, wording, draft→schedule): create the replacements first, check them (`GET /api/public/v1/posts` → `state` QUEUE/DRAFT), then `DELETE /api/public/v1/posts/<id>` the old ones (it replies `{"error":true}` but deletes).
- Per reel: LinkedIn host (+link comment) 09:30 · YT brand 17:00 · YT host 18:00 · FB brand 19:30 · FB host 20:00 · IG brand 20:30 · IG host 21:00 · TikTok 21:30 (+ link comments on FB/IG, engagement question on FB) · 4 stories (IG/FB ×2, clean video) 22:00 Cairo. Egypt DST ends last Thu of Oct (UTC+3 → +2); `postiz_payload.py` handles it.
- Ep 3 states (user, 2026-10-24): LinkedIn Tamer + both Facebook posts stay **DRAFT** for review; YouTube, Instagram, TikTok and the stories are **scheduled**. Postiz can't flip a draft in place: create scheduled copies, then delete the drafts they replace.
- Feeds/Shorts/TikTok get the **cover** video; stories get the clean one (Ep 3: cover only, see rule 14). YouTube thumbnail setting fails validation in Postiz → cover video + manual Studio thumbnail. Comments can't be pinned via Postiz (manual). `ask_postiz` fails (no OpenAI key on server).

## 7. Zernio (brand LinkedIn page + brand TikTok)
Postiz has no LinkedIn **page** or Rabet TikTok integration, so those two channels go through the **Zernio** MCP connector.
Every reel scheduled on Postiz also gets 2 Zernio posts at the same date. Account ids, timezone and slots are in
`~/.rabet-reels.json` → `zernio` (Rabet: LinkedIn page "Rabet Podcast", TikTok "rabetpodcast").
- Call `call_tool` → `posts_create_post` (the simple `posts_create` only schedules "N minutes from now" and has no first comment).
  Arguments: `content`, `media_items: [{url, type: "video"}]`, `platforms: [{platform, accountId, platformSpecificData}]`,
  `scheduled_for: "YYYY-MM-DDTHH:MM:SS"` + `timezone: "Africa/Cairo"` (Zernio handles Egypt DST).
  Add `is_draft: true` to save a draft that keeps its date (Ep 3: all Zernio posts are drafts). To replace a video, create the new draft, then `posts_delete` the old one.
- **Media:** the reel's **cover** video. Its Postiz upload URL is public, so pass it straight in `media_items` (no re-upload).
- **LinkedIn page (09:30 Cairo):** use the brand-voice caption (`facebook_brand`), drop the link lines, end with «الحلقة كاملة على YouTube، اللينك في أول كومنت.» and put the link in `platformSpecificData.firstComment` (LinkedIn suppresses links in captions). Don't use the host's `linkedin` caption: it has first-person opinions.
- **TikTok (21:30 Cairo):** `content` = TikTok title line + TikTok caption; `tiktok_settings`: `privacyLevel PUBLIC_TO_EVERYONE`, `allowComment/allowDuet/allowStitch true`, `commercialContentType none`, `contentPreviewConfirmed true`, `expressConsentGiven true`, `videoCoverTimestampMs 500` (inside the 1.2 s thumbnail intro). Test with `dry_run: true` (TikTok only); LinkedIn: `validate_post`.
- ⚠️ A `scheduled_for` already in the past **publishes immediately**. Check the Cairo time first and move a passed slot.
- To replace a Zernio post: `posts_delete` (scheduled posts only) and create the new one. Log ids in `_campaign/zernio_scheduled.csv`.

## 8. Full episode: YouTube thumbnail, title, description

**Thumbnails** (user-approved style, Ep 2 and Ep 3): `python scripts/make_episode_thumbs.py spec.json` → `<prefix>.jpg/.png`, `_B`, `_C` in `out`.
- A: navy grid, guest cut-outs left with a white outline, «الحلقة …» chip + logo, l1 (cream Lalezar) + l2 (orange tilted box) + kicker bar.
- B: cream board, navy slanted block with an outlined episode number, guests clipped to the block, l1 navy + l2 orange + English chips.
- C: like A with a huge aqua English word between l1 and l2.
- Cut-outs: pick a 4K frame per guest where they look toward camera/right, `npx hyperframes@0.8.163 remove-background`. Mics stay in; table/cup remnants hide under the name chips. Order guests back→front (the front one is the rightmost head); tune `left/top/width` until no head touches the text (≈ x < 700) and check the contact sheet.
- RTL rule 8 applies: no line starts with English; English words sit mid-line or in their own element.

**Title**: 3–5 options under 100 chars, each pairing with one thumbnail, ending `| رابط بودكاست - الحلقة N`. B2B, insightful, a question or tension, no clickbait claims.

**Description** (Egyptian Arabic + English terms, humanized):
1. Two-sentence hook naming the tension, then who talks about what.
2. Guests/hosts: name | title, LinkedIn link on the next line (ask the user for any profile link you don't have; Ep 3: Tamer, Haitham, Hossam).
3. «محاور الحلقة:» chapters from the reel/clip source times (`ep*_defs.py` / sheet), first line `00:00`, ascending, ≥ 10 s apart.
   The times are for the master **without** a teaser; if the upload has the teaser, shift every chapter by the teaser length (Ep 3: +58 s, ffprobe both masters) and add `00:00 التيزر`. Give both lists if unsure which file goes up.
4. Channel CTA `https://www.youtube.com/@RabetPodcast`, then ~12 hashtags (#رابط_بودكاست #بودكاست_تقني #الذكاء_الاصطناعي #RabetPodcast + topic tags) and a comma list for the tags field.
Save as `Ep<N>_YouTube_Title_Description.txt` next to the thumbnails.

## 9. Fixing a shipped reel (re-cut after review)
1. Find the right edge with `tail_check.py` and put the new end in the reel definition (`ranges` + `range_end_exact`; and `hook_end_exact` when the hook ends on the same word). Rebuild A-roll → words → beats → render → ship. Thumbnails stay.
2. A re-transcribed cut can spell English terms in Arabic letters («إجزام», «زومبي فيتشرز»), which breaks word anchors. Add `fixes`; don't move anchors.
3. Check the rendered file: transcribe its last 12 s (the speaker's last word, then the CTA) and pull a frame before the CTA.
4. **Drive:** the Drive connector can't upload content. Copy the file into the synced `G:/My Drive/<upload folder>`, find the new file id with `search_files`, then `update_file parentId` into the reels folder. Files owned by the other Google account can't be trashed from the connector, so rename them `OLD_…` and tell the user. A full C: drive (Drive caches uploads there) fails the copy with "No space left"; `pip cache purge` frees GBs. New file ⇒ new link: update the sheet's Reel Link (S) and Transcript (U) (`export_transcripts.py`).
5. **Zernio:** `call_tool posts_update_post {post_id, media_items:[{url, type:"video"}]}` swaps the video in place and keeps text, mentions, first comment, tags and date. No delete/recreate needed.
6. **Postiz:** media can't be edited in place. Rebuild every post of the reel from its current server text, tags, date, state and settings, take the comments from the reel's payload (Facebook: link comment first), create it, then delete the old post (`video_swap.py` pattern). The public API allows ≈ 30 calls/hour, so run it paced in the background (`PACE=125`, about 4 h for 5 reels).

