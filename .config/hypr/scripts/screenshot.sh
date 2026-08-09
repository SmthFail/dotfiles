#!/usr/bin/env bash
set -euo pipefail

mode="${1:-area}"
dir="${XDG_PICTURES_DIR:-$HOME/Pictures}/screenshots"
mkdir -p "$dir"

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
file="$dir/screenshot-$timestamp.png"

copy_file() {
    wl-copy --type image/png < "$1" >/dev/null 2>&1
}

case "$mode" in
    area)
        geometry="$(slurp)"
        grim -g "$geometry" "$file"
        copy_file "$file"
        ;;
    full)
        grim "$file"
        copy_file "$file"
        ;;
    edit)
        geometry="$(slurp)"
        grim -g "$geometry" "$file"
        swappy -f "$file"
        ;;
    *)
        printf 'Usage: %s {area|full|edit}\n' "$0" >&2
        exit 2
        ;;
esac

printf '%s\n' "$file"
