#!/usr/bin/env bash
# Run the medication example on the fake notes in notes/.
set -euo pipefail
cd "$(dirname "$0")"
python3 select_notes.py --concept medication --notes_dir notes/ --top_n 3
cat medication_scores.csv
echo
cat medication_top_n_file_ids.csv
echo
cat medication_scores_with_evidence.csv
echo
cat medication_top_n_with_evidence.csv
