#!/usr/bin/env bash
# The Last of Us Remastered: prepares the image, runs the game for N seconds and, optionally, presses buttons
# from a script and saves screenshots (raw BGRA display dumps converted to PNG).
# Usage: scripts/tlou_run.sh [seconds=120] [shots_dir] [press_script]
#   press_script: lines "<second> <buttons...>" (e.g. "40 cross", "60 options"); each press lasts 0.3 s.
# Only one game instance may run at a time on this machine: the script waits for any other.
set -uo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
port=$root/port
seconds=${1:-120}; shots=${2:-}; script=${3:-}
dump=$root/game/CUSA00552
# One game instance at a time on this machine (shared lock with the other agents' runs).
lock=${GAME_LOCK:-/tmp/claude-1000/-home-hayatog-decomp/79f27d1d-d3f5-4a2e-a5f3-511e01385ae2/scratchpad/game.lock}
if [[ -z ${TLOU_RUN_LOCKED:-} ]]; then
    touch "$lock"; exec env TLOU_RUN_LOCKED=1 flock "$lock" "$0" "$@"
fi
(cd "$port/scripts" &&
 python3 prepare.py "$dump" --out ../out >/dev/null &&
 python3 link_modules.py "$dump" --out ../out --modules libc.prx libSceFios2.prx >/dev/null &&
 python3 content_profile.py "$dump" --out ../out >/dev/null) || { echo "prepare failed" >&2; exit 1; }
mkdir -p "$port/user" "$port/out/logs"
log=$port/out/logs/tlou-$(date +%Y%m%d-%H%M%S).log
ln -sfn "$log" "$port/out/last_run.log"
export TLOU_PIPELINE_BINARIES=0 TLOU_READBACKS=${TLOU_READBACKS:-2} TLOU_EAGER_READBACK=${TLOU_EAGER_READBACK:-0} TLOU_WRITE_MERGE=${TLOU_WRITE_MERGE:-0} TLOU_GC_BUDGET_MB=${TLOU_GC_BUDGET_MB:-3500} TLOU_UPSCALER=off TLOU_JITTER=0 \
       TLOU_OBJECT_MOTION=0 TLOU_FRAME_STATS=1 TLOU_LANGUAGE=${TLOU_LANGUAGE:-1}
pad=$port/out/pad_input.txt; : > "$pad"; export TLOU_PAD_FILE=$pad
if [[ -n $shots ]]; then
    mkdir -p "$shots"; export TLOU_FRAME_DUMP_TRIGGER=$shots/trigger TLOU_DUMP_DIR=$shots
fi
export TLOU_APP_NAME="The Last of Us Remastered" TLOU_APP_ID=tlou-pc
(cd "$port/user" && exec "$port/out/tlg-probe" "$port/out/boot-linked.bin" --app0 "$dump" --user . \
    --content-profile "$port/out/content.bin" --timeout "$seconds") > "$log" 2>&1 &
game=$!
start=$(date +%s)
if [[ -n $script && -f $script ]]; then
    while read -r at buttons; do
        [[ -z $at || $at == \#* ]] && continue
        while (( $(date +%s) - start < at )); do sleep 0.2; done
        kill -0 "$game" 2>/dev/null || break
        if [[ $buttons == shot ]]; then [[ -n $shots ]] && touch "$shots/trigger"; continue; fi
        echo "$buttons" > "$pad"; sleep 0.3; : > "$pad"
        echo "[$(( $(date +%s) - start ))s] $buttons"
    done < "$script"
fi
wait "$game"; code=$?
if [[ -n $shots ]]; then
    python3 - "$shots" <<'EOF'
import sys, re
from pathlib import Path
import numpy as np
from PIL import Image
# TLOU's display buffer is A2R10G10B10 (10 bits per channel), not 8-bit BGRA.
for raw in Path(sys.argv[1]).glob('display_*.raw'):
    m = re.search(r'_(\d+)x(\d+)\.raw$', raw.name); w, h = int(m[1]), int(m[2])
    d = np.fromfile(raw, dtype='<u4')
    if d.size >= w * h:
        d = d[:w * h].reshape(h, w)
        rgb = np.stack([((d >> s) & 1023) >> 2 for s in (20, 10, 0)], -1).astype('uint8')
        Image.fromarray(rgb).save(raw.with_suffix('.png'))
EOF
fi
echo "exit $code; log: $log"
