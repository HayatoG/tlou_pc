#!/usr/bin/env bash
# The Last of Us Remastered launcher (pt_BR/en_US): game folder, languages, video, Play.
exec python3 "$(dirname -- "$(readlink -f -- "$0")")/port/launcher/tlou_launcher.py" "$@"
