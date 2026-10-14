#!/usr/bin/env bash
# Quick bring-up check without a window: prepares the image and runs the CPU side only
# (--cpu-only, no GPU) for N seconds. Usage: scripts/tlou_quick.sh [seconds=20]; env passes through.
set -uo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd); port=$root/port; dump=$root/game/CUSA00552
lock=${GAME_LOCK:-/tmp/claude-1000/-home-hayatog-decomp/79f27d1d-d3f5-4a2e-a5f3-511e01385ae2/scratchpad/game.lock}
if [[ -z ${TLOU_LOCKED:-} ]]; then touch "$lock"; exec env TLOU_LOCKED=1 flock "$lock" "$0" "$@"; fi
(cd "$port/scripts" && python3 prepare.py "$dump" --out ../out >/dev/null &&
 python3 link_modules.py "$dump" --out ../out --modules libc.prx libSceFios2.prx >/dev/null &&
 python3 content_profile.py "$dump" --out ../out >/dev/null) || { echo "prepare failed" >&2; exit 1; }
mkdir -p "$port/user" "$port/out/logs"
log=$port/out/logs/quick-$(date +%Y%m%d-%H%M%S).log; ln -sfn "$log" "$port/out/last_quick.log"
(cd "$port/user" && exec "$port/out/tlg-probe" "$port/out/boot-linked.bin" --cpu-only --app0 "$dump" --user . \
    --content-profile "$port/out/content.bin" --timeout "${1:-20}") > "$log" 2>&1
echo "exit $?; log: $log"
