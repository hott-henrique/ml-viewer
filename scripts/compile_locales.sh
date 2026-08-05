#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/compile_locales.py" --locales-dir "$ROOT/src/application/locales"
