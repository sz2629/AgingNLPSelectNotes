#!/usr/bin/env bash
# Run the gait_and_balance example on the fake notes in notes/.
set -euo pipefail
cd "$(dirname "$0")"
python3 select_notes.py --concept gait_and_balance --notes_dir notes/ --top_n 3
cat gait_and_balance_scores.csv
echo
cat gait_and_balance_top_n_file_ids.csv
echo
cat gait_and_balance_scores_with_evidence.csv
echo
cat gait_and_balance_top_n_with_evidence.csv
