#!/usr/bin/env bash
# One-command Rabet reel build.
#   pipeline.sh <reel_dir> <stage> [styles...]
# stages:  aroll   — cut tightened A-rolls from reel_spec.json (fast)
#          words   — Whisper large-v3 word timings per A-roll (GPU, ~20 s each)
#          matte   — refined speaker mattes for styles that need them (GPU via gpu_matte.py, ~2 min per 45 s per pass)
#          render  — reel data -> assemble -> check -> render (--sdr) -> loudnorm -> deliver/
#          all     — every stage in order
# Run from anywhere; heavy stages run sequentially on purpose (RAM).
set -e
# Windows paths (pwd -W) because Git Bash hands them to Windows Python; plain pwd elsewhere.
winpath() { (cd "$1" && (pwd -W 2>/dev/null || pwd)); }
SK=$(winpath "$(dirname "$0")/..")
# Python: $RABET_PY, else a project .venv next to the working dir, else python on PATH
PY=${RABET_PY:-$( [ -x .venv/Scripts/python.exe ] && echo .venv/Scripts/python.exe || ([ -x .venv/bin/python ] && echo .venv/bin/python) || echo python)}
REEL=$(winpath "$1"); STAGE=$2; shift 2
STYLES=${@:-s1 s2 s3}
style_field() { PYTHONIOENCODING=utf-8 $PY -c "import json,sys;d=json.load(open(r'$SK/scripts/styles.json'))['$1'];v=d$2;print('' if v is None else v)"; }

do_aroll()  { $PY $SK/scripts/build_aroll.py "$REEL/reel_spec.json" $STYLES; }
do_words()  { for s in $STYLES; do $PY $SK/scripts/transcribe_words.py "$REEL/media/aroll_$s.mp4" "$REEL/media/aroll_$s.words.json"; done; }
do_matte()  {
  for s in $STYLES; do
    hr=$(style_field $s "['matte'] and d['matte']['head_rows']" 2>/dev/null || true)
    [ -z "$hr" ] || [ "$hr" = "False" ] && continue
    full=$(style_field $s "['matte']['full']")
    $PY $SK/scripts/refine_matte.py "$REEL/media/aroll_$s.mp4" "$REEL/media/cutout_$s.webm" --head-rows $hr $([ "$full" = "True" ] && echo --full)
  done
}
do_render() {
  mkdir -p "$REEL/deliver"
  for s in $STYLES; do
    tpl=$(style_field $s "['template']"); P="$REEL/hf/$tpl"
    cut=""; [ -f "$REEL/media/cutout_$s.webm" ] && cut="$REEL/media/cutout_$s.webm"
    PYTHONIOENCODING=utf-8 $PY $SK/scripts/make_reel_data.py "$REEL/media/aroll_$s.words.json" "$REEL/media/aroll_$s.segments.json" "$REEL/beats_$s.json" "$REEL/reel-data_$s.js"
    $PY $SK/scripts/assemble.py "$SK/templates/$tpl" "$P" "$REEL/reel-data_$s.js" "$REEL/media/aroll_$s.mp4" $cut
    # full-length check exceeds its own deadline on 40 s+ reels -> check in 15 s ranges
    dur=$(PYTHONIOENCODING=utf-8 $PY -c "import json;d=json.loads(open('$REEL/reel-data_$s.js',encoding='utf-8').read().split('=',1)[1].rstrip().rstrip(';'));print(int(d['duration']+d['ctaDur'])+1)")
    for ((a=0; a<dur; a+=15)); do (cd "$P" && npx --yes hyperframes@0.8.163 check --no-proxy --range $a,$((a+15)) --samples 4 | tail -2 || true); done
    (cd "$P" && npx --yes hyperframes@0.8.163 render --fps 25 -q delivery --sdr -o render.mp4)
    name=$(basename "$REEL")_${tpl}
    ffmpeg -y -loglevel error -i "$P/render.mp4" -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 48000 -c:a aac -b:a 192k "$REEL/deliver/$name.mp4"
    ffmpeg -y -loglevel error -i "$REEL/deliver/$name.mp4" -vf "fps=1/2.5,scale=200:-1,tile=10x2" -frames:v 1 "$REEL/deliver/sheet_$tpl.jpg"
    echo "delivered $REEL/deliver/$name.mp4"
  done
}
case $STAGE in
  aroll) do_aroll ;; words) do_words ;; matte) do_matte ;; render) do_render ;;
  all) do_aroll; do_words; do_matte; do_render ;;
  *) echo "unknown stage $STAGE"; exit 2 ;;
esac
