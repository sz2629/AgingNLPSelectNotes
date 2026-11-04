"""Score every note in a directory for one concept and save the top-n note IDs.

score = keyword matches + regex matches (case-insensitive, every occurrence counts).
"""
import argparse
import csv
import re
from pathlib import Path

# Rules per concept -> sub-feature -> keywords and regexes.
# Definitions come from Appendix_NLP_Feature_Definitions_20261028.docx.
CONCEPTS = {
    "gait_and_balance": {
        "gait_abnormality": {
            "keywords": ["unsteady gait", "shuffling gait", "wide-based gait", "slow gait"],
            "regex": [r"\b(unsteady|shuffling|wide[- ]based|slow(ed)?|abnormal)\s+(gait|walk(ing)?)\b"],
        },
        "balance_impairment": {
            "keywords": ["poor balance", "impaired balance", "unsteadiness", "loss of balance"],
            "regex": [r"\b(poor|impaired|reduced|loss of|difficulty (with|keeping|maintaining))\s+balance\b"],
        },
        "unsafe_ambulation": {
            "keywords": ["ambulating without assistance", "unsafe ambulation", "walking without walker"],
            "regex": [r"\b(walk|walks|walking|ambulat\w+)\s+(without|against)\s+(\w+\s+){0,2}(assist\w*|walker|cane|restrictions?|orders?)\b"],
        },
    },
}


def score_note(text, rules):
    score = 0
    for sub in rules.values():
        for kw in sub["keywords"]:
            score += len(re.findall(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE))
        for rx in sub["regex"]:
            score += sum(1 for _ in re.finditer(rx, text, re.IGNORECASE))
    return score


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--concept", required=True, choices=CONCEPTS)
    p.add_argument("--notes_dir", required=True)
    p.add_argument("--top_n", type=int, default=3)
    args = p.parse_args()

    rules = CONCEPTS[args.concept]
    files = sorted(Path(args.notes_dir).glob("*.txt"),
                   key=lambda f: (not f.stem.isdigit(), int(f.stem) if f.stem.isdigit() else 0, f.stem))
    scores = [(f.stem, score_note(f.read_text(encoding="utf-8", errors="ignore"), rules)) for f in files]

    with open(f"{args.concept}_scores.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["note_id", "score"])
        w.writerows(scores)

    # Highest score first; ties keep note ID order (sort is stable).
    top = sorted(scores, key=lambda s: -s[1])[: args.top_n]
    with open(f"{args.concept}_top_n_file_ids.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["note_id"])
        w.writerows([[nid] for nid, _ in top])


if __name__ == "__main__":
    main()
