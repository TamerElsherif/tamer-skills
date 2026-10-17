#!/usr/bin/env bash
# Ship one rendered reel: copy it + its thumbnail to the output folder, build the cover version
# (thumbnail as a 1.2 s intro + whoosh) and upload both videos to Postiz.
#   finish.sh <reel_dir> <NN> <template> <Title-With-Dashes>
#   e.g. finish.sh projects/ep2-reels/reels/clip06 06 s3-bold Can-You-Make-Money
# Output folder: $RABET_OUTPUT_DIR, else "output_dir" in ~/.rabet-reels.json.
set -e
SK=$(cd "$(dirname "$0")/.." && pwd)
PY=${RABET_PY:-python}
R=$1; NN=$2; TPL=$3; TITLE=$4
O=${RABET_OUTPUT_DIR:-$($PY -c "import sys;sys.path.insert(0,r'$SK/scripts');import config;print(config.load().get('output_dir',''))")}
[ -n "$O" ] || { echo "set RABET_OUTPUT_DIR or output_dir in ~/.rabet-reels.json"; exit 2; }
mkdir -p "$O"
base="Reel${NN}_${TITLE}"
cp "$R/deliver/$(basename "$R")_${TPL}.mp4" "$O/$base.mp4"
cp "$R/thumb.png" "$O/Reel${NN}_thumbnail.png"
$PY "$SK/scripts/add_cover.py" "$O/$base.mp4" "$O/Reel${NN}_thumbnail.png" "$O/${base}_cover.mp4" 1.2 "$SK/assets/whoosh.mp3"
$PY "$SK/scripts/postiz_upload.py" "$O/$base.mp4" "$O/${base}_cover.mp4"
