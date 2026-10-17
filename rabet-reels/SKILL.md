---
name: rabet-reels
description: Produce 9:16 reels + thumbnails from Rabet (رابط) Podcast episodes — Egyptian Arabic mixed with English, B2B tech audience — and schedule them on Postiz. Use when the user asks to cut, style, caption, or thumbnail a Rabet clip, references the Rabet clip sheet, a "Final Clip ID", says "make the next reel", or wants reels drafted/scheduled across LinkedIn, YouTube Shorts, Facebook, Instagram and TikTok. Data-driven: a reel is a reel_spec.json + one beats file per style; scripts and HyperFrames templates do the rest.
---

# Rabet Reels

> v0.4 (2026-10-17): Whisper + mattes on the RTX 5050. v0.3 (2026-10-16): Episode 2 clips 05–12 shipped from this pipeline (HQ multicam master, Postiz campaign).
> Per-user settings (output folder, Postiz URL/token, channel ids) live in `~/.rabet-reels.json` — copy
> `config.example.json`. Never hard-code them in the skill.
> **ONE reel per sheet topic** — never three variants. Pick the style by content (below) and the
> thumbnail by content + B2B audience. All three styles and T1–T3 thumbnails are user-approved.

### Style / thumbnail choice
| Content | Style | Thumb |
|---|---|---|
| Calm advice, checklists, "how we work" | S1 Clean (side stacks) | T1 big two-line question/claim |
| Step-by-step teaching, frameworks, lists | S2 Split (panels; no matte → fastest, most robust) | T3 editorial quote |
| Punchy / contrarian / quotable framework | S3 Bold (box groups) | T2 cinematic BG + cutout |
Alternate guests and styles across a campaign so the feed doesn't repeat.

## 0. Inputs

| Input | Where |
|---|---|
| Clip list | The user's clip sheet (Google Sheet "Reels", link from the user; Drive `read_file_content`). Columns: Final Clip ID, Member, Eps, up to 3 start/end ranges, Topic, flags, Status, Reel Link |
| Episodes | HQ episode master from the user (multicam, cuts between cameras). If sheet times come from an earlier cut, find the constant offset by audio cross-correlation (Ep 2: +51.36 s) |
| Output | `output_dir` from `~/.rabet-reels.json`: `ReelNN_<Title>.mp4` + `_cover.mp4` + `ReelNN_thumbnail.png` |
| Brand | The user's brand-identity folder · named photos of hosts and guests |
| Names | Use the name the user gives, not photo file names (Ep 2 guest: «م. خالد ناصر الدين — مستشار التسويق الإستراتيجي»; host: هيثم فؤاد). The episode is «الحلقة الثانية» — check the episode number before writing captions |

## 1. Rules (from the user — do not regress)

1. **Hook in the first 1–3 s** (H1 bold claim cold-open / H2 quoted misconception / H3 open question). Never invent claims.
2. **Graphics never cover the speaker's face.** Place them beside, above, below, or *behind* the speaker. Anything that touches the head goes on the **behind layer** (between plate and matte). Keep it identifiable: lay side graphics in the clear wall zone (S1: x 40–420, y 300–850, above the mic — the matte includes the mic).
3. **Rabet logo**: ~130 px (videos) / ~175 px (thumbnails), placed high (top ≈ 120–150 px).
4. **Matte edges must be clean** (no halo/slop around the head) → always `refine_matte.py` (head-crop matte + choke), never the raw full-frame matte.
5. SFX only, no music. Full-episode CTA «الحلقة كاملة على YouTube». Name card once, early, below/beside the face, **timed on a shot where the named speaker is on screen** (check `media/shots.json`).
6. Mixed script: English terms in Latin (glossary), every "marketing" form → Latin `Marketing` («بالـ Marketing»).
7. Tighten pauses; alternate framing (1.0 ↔ 1.08) on every join; punch-in + impact at the turn.
8. **RTL**: never start a line/headline with an English word; big wrapped headlines carry no English (bidi reorders it) — put English in its own box or mid-line. Captions/posts: RLM (U+200F) at each Arabic line start.
9. S3 palette is **cool**: deep navy grid (aqua lines) → near-black grid (orange lines) at the turn. Orange = accent only.

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
Caption chunks shorter than the pop-in tween used to stick on screen forever in S3 ("ghost" glyphs over later captions; snapshots don't show it). Fixed in the template; if you see overlapping caption glyphs in a render, look for caps with `e - s < 0.12`.
S1 stack lines never wrap (template shrinks the font to fit 400 px) — a wrapped mixed line pushes English to a line start.
Multicam layout: cut-ins of the other person put their head higher (top ≈ y 590 of 1920). Keep S3 groups ending above ≈ y 560: max 3 lines (sizes ≤ 80 after a 120+ headline), merge list items («الأوتوبيس · الترام») or split a long list into two groups. Check every reaction shot in the sheet.
Beats extras: `extra_words` (inject words into segments), `wide_words {"file","offset"}` (use the wide transcript when the cut-A-roll transcript is poor).

## 3. What each piece does

| File | Role |
|---|---|
| `scripts/build_aroll.py` | speech islands via silencedetect → drop tiny/filler/`drop_ranges` → pad/merge → hook + body → frame-snapped cut, 12 ms fades |
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

## 6. Postiz (self-hosted or cloud)
- Default to **drafts** (`draft`) for user review; switch to `schedule` only when the user says so. URL/token from `~/.rabet-reels.json` (`postiz_token_file` may hold the `claude mcp add … Bearer …` line); never print the token.
- To change existing posts (new video, wording, draft→schedule): create the replacements first, check them (`GET /api/public/v1/posts` → `state` QUEUE/DRAFT), then `DELETE /api/public/v1/posts/<id>` the old ones (it replies `{"error":true}` but deletes).
- Per reel: LinkedIn host (+link comment) 09:30 · YT brand 17:00 · YT host 18:00 · FB brand 19:30 · FB host 20:00 · IG brand 20:30 · IG host 21:00 · TikTok 21:30 (+ link comments on FB/IG, engagement question on FB) · 4 stories (IG/FB ×2, clean video) 22:00 Cairo. Egypt DST ends last Thu of Oct (UTC+3 → +2); `postiz_payload.py` handles it.
- Feeds/Shorts/TikTok get the **cover** video; stories get the clean one. YouTube thumbnail setting fails validation in Postiz → cover video + manual Studio thumbnail. Comments can't be pinned via Postiz (manual). `ask_postiz` fails (no OpenAI key on server).
