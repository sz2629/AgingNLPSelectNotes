#!/usr/bin/env bash
# Run the musculoskeletal example on the fake notes in notes/.
set -euo pipefail
cd "$(dirname "$0")"
python3 select_notes.py --concept musculoskeletal --notes_dir notes/ --top_n 3
cat musculoskeletal_scores.csv
echo
cat musculoskeletal_top_n_file_ids.csv
echo
cat musculoskeletal_scores_with_evidence.csv
echo
cat musculoskeletal_top_n_with_evidence.csv
