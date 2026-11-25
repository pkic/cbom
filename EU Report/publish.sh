#!/usr/bin/env bash
# Emit the submittable copy of the report. Invoke as: bash publish.sh ["version label"]
set -euo pipefail
cd "$(dirname "$0")"
python3 publish.py "$@"
