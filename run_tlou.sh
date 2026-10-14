#!/usr/bin/env bash
# Runs The Last of Us Remastered from a terminal with the launcher settings: ./run_tlou.sh [seconds]
exec python3 "$(dirname -- "$(readlink -f -- "$0")")/port/launcher/tlou_run.py" "$@"
