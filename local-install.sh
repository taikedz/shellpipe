#!/usr/bin/env bash

set -euo pipefail

PYTHONPATH="${PYTHONPATH:-}"

main() {
    local libdir="$HOME/.local/usr/lib/python3"

    move_here
    ensure_target "$libdir"

    sync_files shellpipe "$libdir/shellpipe"

    ensure_bashrc_pythonpath "$libdir"
}

move_here() {
    cd "$(dirname "$0")"
}

ensure_target() {
    [[ -d "$1" ]] && return
        
    mkdir -p "$1"
}

ensure_bashrc_pythonpath() {
    (echo "$PYTHONPATH" | grep "$1") && return

    if [[ -n "$PYTHONPATH" ]]; then
        PYTHONPATH="$PYTHONPATH:"
    fi

    echo "export PYTHONPATH=\"$PYTHONPATH$1\"" >> "$HOME/.bashrc"

    echo ""
    echo "------ You need to reload your bashrc -------"
    echo "------      Or start a new shell      -------"
    echo ""
}

sync_files() {
    rsync -a "$1/" "$2/"
}

main "$@"
