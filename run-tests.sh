#!/usr/bin/env bash

set -euo pipefail

HERE="$(dirname "$0")"

EPP="${PYTHONPATH:-}" # Existing python path
[[ -z "$EPP" ]] || EPP=":$EPP"

PYTHONPATH="$HERE$EPP"

cd "$HERE"


for item in tests/test_*.py ; do
    echo "--- Running $item ---"
    python3 "$item"
done
