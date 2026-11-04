#!/usr/bin/env bash
# Run the cardiovascular example on the fake notes in notes/.
set -euo pipefail
cd "$(dirname "$0")"
python3 select_notes.py --concept cardiovascular --notes_dir notes/ --top_n 3
cat cardiovascular_scores.csv
echo
cat cardiovascular_top_n_file_ids.csv
