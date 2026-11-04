# Concept Note Selection

Scores every note in a directory for one concept and returns the notes most likely to contain it. Scoring uses rules for each concept: keywords and regular expressions.

> **Status:** `select_notes.py` supports `gait_and_balance`, `musculoskeletal`, `sensory`, `cardiovascular`, `mental_health`, `laboratory_and_nutrition` and `medication`. Run the examples with `./run_gait_example.sh`, `./run_musculoskeletal_example.sh`, `./run_sensory_example.sh`, `./run_cardiovascular_example.sh`, `./run_mental_health_example.sh`, `./run_laboratory_and_nutrition_example.sh` and `./run_medication_example.sh` (they use the fake notes in `notes/`).

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
├── ...
└── 20.txt
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

Note 5 | score 3
  +1  unsteadiness
  +1  ambulating without assistance
  +1  ambulating without assistance against orders

TOP 3
  1. Note 1 | score 7
  2. Note 3 | score 3
  3. Note 5 | score 3

3 of 8 notes matched
```

A phrase shows `+2` when both a keyword and a regex match it. Notes with score 0 are not printed.

Each run also writes four CSV files. The values below are illustrative.

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

Two more CSV files save the matched evidence next to each score, in the same `+count phrase` form as the terminal log, separated by `; `.

`gait_and_balance_scores_with_evidence.csv` has every note (evidence is empty when the score is 0):

```csv
note_id,score,evidence
1,7,+2 unsteady gait; +2 wide-based gait; +2 loss of balance; +1 walking without her walker
2,0,
3,3,+2 shuffling gait; +1 reduced balance
```

`gait_and_balance_top_n_with_evidence.csv` has the top-n notes, highest score first:

```csv
rank,note_id,score,evidence
1,1,7,+2 unsteady gait; +2 wide-based gait; +2 loss of balance; +1 walking without her walker
2,3,3,+2 shuffling gait; +1 reduced balance
3,5,3,+1 unsteadiness; +1 ambulating without assistance; +1 ambulating without assistance against orders
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
7. `medication` (`medication_reconciliation_concern` and `deprescribing_discussion`)

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

## Example rules: sensory

These are drafts to review.

### vision_impairment

Documentation of reduced visual function affecting daily activities, whether or not corrected by lenses.

- **Keywords:** vision impairment, visual impairment, low vision, blurry vision, blurred vision, legally blind, macular degeneration
- **Regex:**

```regex
\b(decreased|reduced|poor|impaired|declining|worsening)\s+(vision|visual acuity|eyesight)\b
\b(difficult\w*|trouble|unable to|can(no|')t)\s+(\w+\s+){0,2}(see(ing)?|read(ing)?)\b
\b20/([4-9]\d|[1-9]\d{2,})\b
```

The last pattern catches visual acuity of 20/40 or worse; 20/20 and 20/30 do not match.

### hearing_impairment

Documentation of reduced hearing affecting communication or daily activities, whether or not aided by hearing devices.

- **Keywords:** hearing loss, hard of hearing, hearing impairment, presbycusis
- **Regex:**

```regex
\b(decreased|reduced|poor|impaired|diminished)\s+hearing\b
\b(difficult\w*|trouble)\s+(\w+\s+){0,2}hear(ing)?\b
\bhearing\s+aids?\b
\bHOH\b
```

### numbness_neuropathy

Documentation of reduced, lost, or abnormal peripheral sensation, typically in the hands or feet, either reported by the patient (numbness, tingling, pins and needles, burning) or found on exam (diminished light touch, monofilament, vibration, or proprioception), including diagnosed peripheral neuropathy of any cause. Relevant to balance, gait, and fall risk.

- **Keywords:** numbness, tingling, pins and needles
- **Regex:**

```regex
\b((peripheral|diabetic|sensory)\s+)?(poly)?neuropath(y|ic)\b
\b(numb|burning)\s+(\w+\s+){0,2}(hands?|feet|foot|toes|fingers)\b
\b(decreased|diminished|reduced|absent|impaired|loss of)\s+(light touch|sensation|vibrat\w*( sense)?|proprioception|monofilament( sensation)?|pinprick)\b
\binsensate\b
```

Normal exam wording such as "sensation intact to light touch" does not match.

## Example rules: cardiovascular

These are drafts to review.

### dizziness

Patient-reported sensation of lightheadedness, faintness, or spinning that may signal orthostatic change, arrhythmia, or increased fall risk. Includes symptomatic hypotension, in which low or falling blood pressure is accompanied by symptoms such as lightheadedness or near-syncope.

- **Keywords:** dizziness, dizzy, lightheadedness, lightheaded, vertigo, presyncope, symptomatic hypotension
- **Regex:**

```regex
\blight-headed(ness)?\b
\bnear[- ]syncop(e|al)\b
\b(feel(s|ing)?|felt)\s+(faint|woozy)\b
\b(room|head|everything)\s+((is|was)\s+)?spinning\b
\b(orthostatic|postural)\s+hypotension\b
\b(blood pressure|BP)\s+(drops?|dropped|fell|falls)\b
```

"Orthostatic vitals normal" does not match; only orthostatic or postural hypotension does.

## Example rules: mental_health

These are drafts to review.

### anxiety

A mood state marked by persistent worry, nervousness, or fear that may affect function, sleep, or engagement with care.

- **Keywords:** anxiety, anxious, nervousness, panic attacks
- **Regex:**

```regex
\b(excessive|persistent|constant)\s+worry(ing)?\b
\bworr(y|ies|ied|ying)\s+(a lot|constantly|all the time)\b
\bGAD-?7\s*(score\s*)?(of\s*|[:=]\s*)?([5-9]|1\d|2[01])\b
```

The last pattern catches a GAD-7 score of 5 or more (mild anxiety or worse).

### depression

A mood disorder marked by persistent sadness, hopelessness, and loss of interest or pleasure, with cognitive, behavioral, and physical symptoms such as fatigue, poor concentration, and changes in appetite or sleep.

- **Keywords:** depression, depressed, hopelessness, anhedonia
- **Regex:**

```regex
\bMDD\b
\b(feel(s|ing)?|felt)\s+(sad|hopeless|down|worthless)\b
\b(loss of|lost|little|decreased)\s+interest\b
\bPHQ-?9\s*(score\s*)?(of\s*|[:=]\s*)?([5-9]|1\d|2[0-7])\b
\bPHQ-?2\s*(score\s*)?(of\s*|[:=]\s*)?[3-6]\b
```

The PHQ patterns catch a positive screen: PHQ-9 of 5 or more, PHQ-2 of 3 or more. "PHQ-2 score 0" does not match. Fatigue, concentration, appetite and sleep are left out because they are not specific to depression; sleep is scored under `sleep_disturbance`.

### sleep_disturbance

Documentation of disrupted sleep, such as insomnia, difficulty falling or staying asleep, or poor sleep quality.

- **Keywords:** insomnia, sleep disturbance, trouble sleeping
- **Regex:**

```regex
\b(difficult\w*|trouble|problems?)\s+(\w+\s+){0,2}(falling|staying)\s+asleep\b
\b(poor|disrupted|interrupted|fragmented|restless)\s+sleep\b
\b(wakes?|waking|woke|awakens?|awakening)\s+(up\s+)?(\w+\s+){0,2}(at night|overnight|during the night|too early)\b
\bsleep(s|ing)?\s+(only\s+)?[1-4]\s+hours\b
```

### sleep_apnea

Documentation of sleep apnea or repeated pauses in breathing during sleep.

- **Keywords:** sleep apnea, CPAP, BiPAP
- **Regex:**

```regex
\bOSA\b
\b(stops?|stopped|pauses?|paused)\s+breathing\b
\b(apneic|apnea)\s+(episodes|events|spells)\b
\bAHI\s*(of\s*|[:=]\s*)?([5-9]|[1-9]\d+)\b
```

The last pattern catches an apnea-hypopnea index of 5 or more, the usual threshold for sleep apnea.

## Example rules: laboratory_and_nutrition

These are drafts to review.

### malnutrition

Documentation of malnutrition or inadequate nutritional intake, including unintended weight loss, low intake, or clinical signs of undernutrition.

- **Keywords:** malnutrition, malnourished, undernutrition, undernourished, cachexia, unintentional weight loss, unintended weight loss, poor appetite
- **Regex:**

```regex
\b(poor|decreased|reduced|low|minimal|inadequate)\s+(oral\s+|PO\s+|food\s+|caloric\s+|nutritional\s+)?intake\b
\b(lost|losing|loss of)\s+\d+(\.\d+)?\s*(lbs?|pounds|kg)\b
\b(decreased|reduced|loss of)\s+appetite\b
\b(muscle|temporal|fat)\s+wasting\b
\balbumin\s*(of\s*|[:=]\s*)?([0-2](\.\d+)?|3(\.[0-4]\d*)?)(?!\.?\d)
\bBMI\s*(of\s*|[:=]\s*)?(1[0-7](\.\d+)?|18(\.[0-4]\d*)?)(?!\.?\d)
```

The last two patterns catch albumin below 3.5 g/dL and BMI below 18.5. "Albumin 4.1" and "BMI 24.6" do not match.

## Example rules: medication

These are drafts to review.

### medication_reconciliation_concern

Documentation of a discrepancy or problem identified during medication reconciliation, such as a missing, duplicate, or conflicting medication.

- **Keywords:** medication discrepancy, therapeutic duplication, duplicate therapy
- **Regex:**

```regex
\b(medication|med|drug|dose|dosing)\s+(discrepanc(y|ies)|errors?|mismatch(es)?)\b
\bdiscrepanc(y|ies)\s+(\w+\s+){0,3}(medications?|meds?|list|doses?|dosing|pharmacy)\b
\b(duplicate|duplicated)\s+(\w+\s+){0,2}(medications?|meds?|prescriptions?|bottles?|orders?)\b
\b(not|no longer)\s+(on|in)\s+(\w+\s+){0,2}(medication|med)\s+list\b
\b(missing|omitted)\s+from\s+(\w+\s+){0,2}(medication|med)\s+list\b
\bnever\s+(filled|picked up|started)\b
\bconflicting\s+(\w+\s+){0,2}(medications?|meds?|lists?|instructions|doses|prescriptions?)\b
\b(does not|doesn't|did not)\s+match\s+(\w+\s+){0,3}(medications?|meds?|pharmacy|list|bottles?)\b
```

A routine "Medications reviewed, no changes" does not match.

### deprescribing_discussion

Documentation of a discussion about stopping or reducing a medication to lower risk or pill burden, including any mention that a medication has been stopped or discontinued. Excludes temporary deprescription for a procedure (a medication held before and resumed after surgery, endoscopy, imaging, or another procedure).

- **Keywords:** deprescribe, deprescribing, pill burden, polypharmacy, Beers criteria
- **Regex:**

```regex
\b(discontinued|tapered off|weaned off)\b
\b(was|were|has been|have been|is being)\s+stopped\b
\b(stop|stopping|discontinue|discontinuing|taper|tapering|wean|weaning|cut back on)\s+(\w+\s+){0,3}(medications?|meds?|pills?)\b
\b(reduce|reduced|reducing|decrease|decreased|decreasing|lower|lowered|lowering)\s+(the\s+|his\s+|her\s+)?(\w+\s+)?(dose|dosage)\b
\bdose\s+(was\s+)?(reduced|decreased|lowered|halved)\b
```

The rules leave out "hold" and "held", so "aspirin held before colonoscopy and resumed" does not match. They cannot tell a procedure hold from a lasting stop, though: "discontinue aspirin 7 days before surgery" still matches. Check for this when reviewing top-ranked notes.

## Add a concept

1. Copy the sub-feature definitions from the feature doc.
2. Write keywords and regular expressions for each sub-feature.
3. Add fake notes with and without the concept.
4. Run the script and confirm that notes with the concept rank above notes without it.
