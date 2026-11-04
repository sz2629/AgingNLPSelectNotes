# Concept Note Selection

Scores every note in a directory for one concept and returns the notes most likely to contain it. Scoring uses rules for each concept: keywords and regular expressions.

> **Status:** Planned. `select_notes.py` has not been built yet. The command, file names and scoring below are draft proposals.

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
└── 5.txt
```

## Output

Each run writes two CSV files. The values below are illustrative.

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

## Add a concept

1. Copy the sub-feature definitions from the feature doc.
2. Write keywords and regular expressions for each sub-feature.
3. Add fake notes with and without the concept.
4. Run the script and confirm that notes with the concept rank above notes without it.
