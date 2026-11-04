# Concept Note Selection

Scores every note in a directory for one concept and returns the notes most likely to contain it. Scoring uses rules for each concept: keywords and regular expressions.

> **Status:** `select_notes.py` supports `gait_and_balance` and `musculoskeletal`. Run the examples with `./run_gait_example.sh` and `./run_musculoskeletal_example.sh` (they use the fake notes in `notes/`).

## Usage

Run one concept at a time:

```bash
python select_notes.py --concept gait_and_balance --notes_dir notes/ --top_n 3
```

| Argument | Description |
| --- | --- |
| `--concept` | Concept to score, such as `gait_and_balance` |
| `--notes_dir` | Directory containing the notes, with each note identified by its note ID |
| `--top_n` | Number of highest-scoring note IDs to select |

## Input

A directory of notes, such as this fake test set (file format to be confirmed):

```text
notes/
├── 1.txt
├── 2.txt
├── 3.txt
├── 4.txt
├── 5.txt
├── 6.txt
├── 7.txt
└── 8.txt
```

## Output

While it runs, the script prints each matching note, its score and the matched phrases, then the top-n notes:

```text
gait_and_balance | 8 notes

Note 1 | score 7
  +2  unsteady gait
  +2  wide-based gait
  +2  loss of balance
  +1  walking without her walker

Note 3 | score 3
  +2  shuffling gait
  +1  reduced balance

TOP 3
  1. Note 1 | score 7
  2. Note 3 | score 3
  3. Note 5 | score 3

3 of 8 notes matched
```

A phrase shows `+2` when both a keyword and a regex match it. Notes with score 0 are not printed.

Each run also writes two CSV files. The values below are illustrative.

`gait_and_balance_scores.csv` has a score for every note:

```csv
note_id,score
1,5
2,0
3,3
4,1
5,2
```

`gait_and_balance_top_n_file_ids.csv` has the top-n note IDs, highest score first:

```csv
note_id
1
3
5
```

## Scoring

The proposed starting formula for each note is:

```text
score = keyword matches + regex matches
```

Weighting, repeated matches and tie handling are still open. Rules do not handle negation yet, so "no unsteady gait" counts as a match. Check for this when reviewing top-ranked notes.

## Concepts

Complete `gait_and_balance` first, then add the others in this order:

1. `gait_and_balance`
2. `musculoskeletal`
3. `sensory`
4. `cardiovascular`
5. `mental_health`
6. `laboratory_and_nutrition`
7. `medication_reconciliation_concern`
8. `deprescribing_discussion`

Definitions come from `Appendix_NLP_Feature_Definitions_20261028.docx`.

## Example rules: gait_and_balance

These are drafts to review.

### gait_abnormality

Documentation of an abnormal walking pattern, such as unsteady, shuffling, wide-based, or slowed gait.

- **Keywords:** unsteady gait, shuffling gait, wide-based gait, slow gait
- **Regex:**

```regex
\b(unsteady|shuffling|wide[- ]based|slow(ed)?|abnormal)\s+(gait|walk(ing)?)\b
```

### balance_impairment

Documentation of reduced ability to maintain postural stability while standing or moving, including unsteadiness or difficulty keeping balance.

- **Keywords:** poor balance, impaired balance, unsteadiness, loss of balance
- **Regex:**

```regex
\b(poor|impaired|reduced|loss of|difficulty (with|keeping|maintaining))\s+balance\b
```

### unsafe_ambulation

Documentation that the patient walks in a way that poses a safety risk, such as walking without needed assistance or against activity restrictions.

- **Keywords:** ambulating without assistance, unsafe ambulation, walking without walker
- **Regex:**

```regex
\b(walk|walks|walking|ambulat\w+)\s+(without|against)\s+(\w+\s+){0,2}(assist\w*|walker|cane|restrictions?|orders?)\b
```

## Example rules: musculoskeletal

These are drafts to review.

### frailty

A state of reduced physiological reserve and increased vulnerability to stressors, documented as frailty or reflected in features such as weakness, slowness, exhaustion, and low activity.

- **Keywords:** frail, frailty, exhaustion, low activity level
- **Regex:**

```regex
\b(clinical frailty scale|CFS)\s*(score\s*)?(of\s*|[:=]\s*)?[4-9]\b
\b(slow(ed)?|decreased|reduced)\s+(gait speed|walking speed|walk speed)\b
\b(low|decreased|reduced|minimal)\s+(physical\s+)?activity\b
```

Weakness is scored under its own sub-feature, so it is not repeated here.

### weakness

Documentation of reduced muscle strength or generalized weakness affecting function or mobility, including patient-described leg heaviness (legs feeling heavy or difficult to lift).

- **Keywords:** generalized weakness, muscle weakness, leg weakness, legs feel heavy
- **Regex:**

```regex
\b(generali[sz]ed|proximal|distal|muscle|leg|lower extremity|bilateral)\s+weakness\b
\b(legs?|arms?)\s+(feel(s|ing)?|felt)\s+(heavy|weak)\b
\b(difficult\w*|hard|trouble)\s+(\w+\s+){0,2}lift(ing)?\s+(\w+\s+)?(legs?|feet|foot)\b
\b[0-4][+-]?/5\s+(strength|power)\b
```

The last pattern catches reduced strength grades such as "4/5 strength"; normal "5/5 strength" does not match.

## Add a concept

1. Copy the sub-feature definitions from the feature doc.
2. Write keywords and regular expressions for each sub-feature.
3. Add fake notes with and without the concept.
4. Run the script and confirm that notes with the concept rank above notes without it.
