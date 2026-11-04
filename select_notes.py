"""Score every note in a directory for one concept and save the top-n note IDs.

score = keyword matches + regex matches (case-insensitive, every occurrence counts).

Outputs (in the current directory):
  <concept>_scores.csv          one row per note: score, per-sub-feature counts, matched text
  <concept>_evidence.csv        one row per match: sub-feature, rule, matched text, context
  <concept>_top_n_file_ids.csv  top-n note IDs, highest score first
While running, each note's text (matches marked [[like this]]), matches and score are printed.
Use --quiet to turn that off, or --hide_zero to skip notes with no matches.
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
    "musculoskeletal": {
        "frailty": {
            "keywords": ["frail", "frailty", "exhaustion", "low activity level"],
            "regex": [
                r"\b(clinical frailty scale|CFS)\s*(score\s*)?(of\s*|[:=]\s*)?[4-9]\b",
                r"\b(slow(ed)?|decreased|reduced)\s+(gait speed|walking speed|walk speed)\b",
                r"\b(low|decreased|reduced|minimal)\s+(physical\s+)?activity\b",
            ],
        },
        "weakness": {
            "keywords": ["generalized weakness", "muscle weakness", "leg weakness", "legs feel heavy"],
            "regex": [
                r"\b(generali[sz]ed|proximal|distal|muscle|leg|lower extremity|bilateral)\s+weakness\b",
                r"\b(legs?|arms?)\s+(feel(s|ing)?|felt)\s+(heavy|weak)\b",
                r"\b(difficult\w*|hard|trouble)\s+(\w+\s+){0,2}lift(ing)?\s+(\w+\s+)?(legs?|feet|foot)\b",
                r"\b[0-4][+-]?/5\s+(strength|power)\b",
            ],
        },
    },
}


CONTEXT_CHARS = 40


def find_matches(text, rules):
    """Return every keyword/regex match as a dict, in text order."""
    matches = []
    for sub_name, sub in rules.items():
        patterns = [("keyword", kw, r"\b" + re.escape(kw) + r"\b") for kw in sub["keywords"]]
        patterns += [("regex", rx, rx) for rx in sub["regex"]]
        for rule_type, rule, rx in patterns:
            for m in re.finditer(rx, text, re.IGNORECASE):
                lo, hi = max(0, m.start() - CONTEXT_CHARS), min(len(text), m.end() + CONTEXT_CHARS)
                context = (text[lo:m.start()] + "[[" + m.group(0) + "]]" + text[m.end():hi]).replace("\n", " ")
                matches.append({
                    "sub_feature": sub_name,
                    "rule_type": rule_type,
                    "rule": rule,
                    "matched_text": m.group(0),
                    "start": m.start(),
                    "end": m.end(),
                    "context": ("..." if lo > 0 else "") + context + ("..." if hi < len(text) else ""),
                })
    return sorted(matches, key=lambda m: (m["start"], m["end"]))


def score_note(text, rules):
    return len(find_matches(text, rules))


def highlight(text, matches):
    """Mark matched spans with [[ ]], merging overlapping matches."""
    spans = []
    for m in matches:
        if spans and m["start"] <= spans[-1][1]:
            spans[-1][1] = max(spans[-1][1], m["end"])
        else:
            spans.append([m["start"], m["end"]])
    out, pos = [], 0
    for lo, hi in spans:
        out += [text[pos:lo], "[[", text[lo:hi], "]]"]
        pos = hi
    return "".join(out + [text[pos:]])


def print_note(note_id, text, matches, sub_names):
    print("=" * 70)
    print(f"Note {note_id} | score = {len(matches)}")
    print("-" * 70)
    print(highlight(text, matches).strip())
    if matches:
        print("-" * 70)
        for m in matches:
            print(f"  + {m['sub_feature']:<20} {m['rule_type']:<8} {m['matched_text']!r}")
        counts = ", ".join(f"{s}={sum(m['sub_feature'] == s for m in matches)}" for s in sub_names)
        print(f"  by sub-feature: {counts}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--concept", required=True, choices=CONCEPTS)
    p.add_argument("--notes_dir", required=True)
    p.add_argument("--top_n", type=int, default=3)
    p.add_argument("--quiet", action="store_true", help="do not print notes and matches")
    p.add_argument("--hide_zero", action="store_true", help="do not print notes with score 0")
    args = p.parse_args()

    rules = CONCEPTS[args.concept]
    sub_names = list(rules)
    files = sorted(Path(args.notes_dir).glob("*.txt"),
                   key=lambda f: (not f.stem.isdigit(), int(f.stem) if f.stem.isdigit() else 0, f.stem))

    score_rows, evidence_rows = [], []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        matches = find_matches(text, rules)
        if not args.quiet and (matches or not args.hide_zero):
            print_note(f.stem, text, matches, sub_names)
        score_rows.append({
            "note_id": f.stem,
            "score": len(matches),
            **{s: sum(m["sub_feature"] == s for m in matches) for s in sub_names},
            "matched_text": " | ".join(f"{m['sub_feature']}: {m['matched_text']}" for m in matches),
        })
        evidence_rows += [{"note_id": f.stem, **m} for m in matches]

    with open(f"{args.concept}_scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["note_id", "score", *sub_names, "matched_text"])
        w.writeheader()
        w.writerows(score_rows)

    with open(f"{args.concept}_evidence.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["note_id", "sub_feature", "rule_type", "rule",
                                           "matched_text", "start", "end", "context"])
        w.writeheader()
        w.writerows(evidence_rows)

    # Highest score first; ties keep note ID order (sort is stable).
    top = sorted(score_rows, key=lambda r: -r["score"])[: args.top_n]
    with open(f"{args.concept}_top_n_file_ids.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["note_id"])
        w.writerows([[r["note_id"]] for r in top])

    if not args.quiet:
        print("=" * 70)
        print(f"Top {args.top_n} for {args.concept}: "
              + ", ".join(f"{r['note_id']} (score {r['score']})" for r in top))
        print(f"Wrote {args.concept}_scores.csv, {args.concept}_evidence.csv, "
              f"{args.concept}_top_n_file_ids.csv")


if __name__ == "__main__":
    main()
