# 04f-eval-set: your first 20-question eval set

A CSV of 20 questions, a 62-line runner (`evalkit.py`) and three small searches to test. No API key, no downloads, no packages.

```bash
python run.py
```

It takes about a second and prints the same result every time.

## Use it for your own system
1. Copy `evalkit.py` and `questions.template.csv` (rename it `questions.csv`).
2. Write 20 rows: `id, tag, question, expected`. Write the expected answer before you run anything. Tag the kinds of question, and include hard ones on purpose.
3. A system is any function that takes a question (text) and returns an answer (text):

```python
from evalkit import load_questions, run, compare, gate
qs     = load_questions("questions.csv")
before = run(old_system, qs)
after  = run(new_system, qs)
fixed, broke, still = compare(before, after)
ok, regressions = gate(before, after)   # one example rule: block if anything that passed before now fails
```

The default check is an exact match. For text answers pass your own, for example `run(system, qs, check=lambda got, exp: exp.lower() in got.lower())`.

## What is in the folder
- `questions.csv`: the 20 questions (5 exact part numbers, 5 in our own words, 5 part numbers typed oddly, 5 that name only the pump model). Written before any search was run on them and not changed afterwards.
- `evalkit.py`: the reusable runner: `load_questions` (checks the file), `run`, `compare`, `gate`, `wilson` (a rough 95% range for a pass rate), `by_tag`.
- `searches.py`: the three searches from `04c-hybrid` (keyword, meaning, hybrid), unchanged.
- `parts.txt`, `vectors.json`: the 20 made-up pump parts and the word vectors, copied from `04c-hybrid`.
- `run.py`: runs all three on the 20 questions and prints the grid. `output.txt`: its output on 11 Nov 2026.
- `questions.template.csv`: a blank starting point.

## Result (output of the run on 11 Nov 2026)

| Kind (5 each) | Keyword | Meaning | Hybrid |
|---|---|---|---|
| Exact part number | 5 | 5 | 5 |
| Our own words | 3 | 0 | 3 |
| Typed oddly | 3 | 1 | 2 |
| Near twin | 5 | 2 | 3 |
| **All 20** | **16** | **8** | **13** |
| Rough 95% range | 58-92% | 22-61% | 43-82% |

From keyword to hybrid: fixed none, broke 3 (q14, q19, q20), 4 questions fail in both (q08, q10, q11, q12). The example rule blocks that change because three questions that passed now fail.

## Read this before you quote the numbers
- The parts and the questions are made up and written by us. Different questions give a different picture: the `04c-hybrid` test (25 other questions) had keyword and hybrid level at 18 of 25. Nothing here says keyword beats hybrid in general.
- 20 questions is a start. One question is 5 points of pass rate, and the keyword and hybrid ranges overlap, so the score alone cannot rank them. The grid, which names the questions that changed, is the useful part.
- The meaning search is averaged word vectors, a stand-in for an embedding model. It is not a modern embedding model and we did not test one.
- A pass means the expected part is ranked first. We did not test whether a model then answers correctly.
- Everything ran once. We called no hosted model.

## Credit
Word vectors: GloVe 6B, 50 dimensions (`glove-wiki-gigaword-50`), Jeffrey Pennington, Richard Socher and Christopher D. Manning, "GloVe: Global Vectors for Word Representation" (EMNLP 2014), Stanford NLP, Public Domain Dedication and License v1.0. `vectors.json` contains only the words this demo uses.
