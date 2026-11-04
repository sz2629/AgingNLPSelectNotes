#!/usr/bin/env bash
# Run the laboratory and nutrition example on the fake notes in notes/.
set -euo pipefail
cd "$(dirname "$0")"
python3 select_notes.py --concept laboratory_and_nutrition --notes_dir notes/ --top_n 3
cat laboratory_and_nutrition_scores.csv
echo
cat laboratory_and_nutrition_top_n_file_ids.csv
echo
cat laboratory_and_nutrition_scores_with_evidence.csv
echo
cat laboratory_and_nutrition_top_n_with_evidence.csv
