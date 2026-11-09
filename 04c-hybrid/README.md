# 04c-hybrid: keyword search, meaning search, and both together

Twenty made-up pump parts (all the text is invented) and 25 questions. Three searches: keyword, meaning, and a hybrid that merges the two rankings. How often is the right part ranked first?

```bash
python run.py
```

No API key, no downloads, no packages. It takes about a second and prints the same result every time.

## What is in the folder
- `parts.txt`: the 20 parts, one per line (`ID | text`). Near-twins on purpose: XR-4471-B and XR-4471-D, XR-4417-B, TK-0932 and TK-0392, and so on.
- `run.py`: the 25 questions (10 quote the part number exactly, 10 use our own words, 5 type the part number differently), the three searches, the fusion and the counts.
- `vectors.json`: 50 numbers for each word the demo uses, taken from pretrained GloVe vectors (see below). About 148 KB.
- `build_vectors.py`: the one-off script that made `vectors.json`. You do not need it to run the demo.
- `output.txt`: the output of the run on 9 Nov 2026 (Python 3.13, Linux sandbox).

## The three searches
- **Keyword:** TF-IDF over whole tokens. A part number such as XR-4471-B stays one token.
- **Meaning:** the average of the word vectors of the words in the text, compared by cosine similarity. A word it does not know is split on "-" and only the known pieces count. Numbers like 4471 are not in the vocabulary.
- **Hybrid:** reciprocal rank fusion with k = 60. Each part scores 1/(60 + position) in each list, and the scores add.

## Result (right part ranked first; top 3 in brackets)

| Question type | Keyword | Meaning | Hybrid |
|---|---|---|---|
| Part number typed exactly (10) | 10 (10) | 8 (8) | 10 (10) |
| No part number, our own words (10) | 7 (7) | 5 (8) | 6 (8) |
| Part number typed differently (5) | 1 (4) | 4 (4) | 2 (5) |
| All questions (25) | 18 (21) | 17 (20) | 18 (23) |

Question by question, hybrid was as good as the better of the two searches for 18 questions, better than both for 2, and worse than the better one for 5. No search put a near-identical part number first on the 10 exact questions.

## Read this before you quote the numbers
- The parts and the questions are made up and written by us, so the split between the three question types is by construction.
- The meaning search is averaged word vectors, a stand-in for an embedding model. It is not a modern embedding model and we did not test one. Do not read its scores as a verdict on real embeddings.
- Settings (k = 60, the tokenizer, the vectors) were fixed in advance and not tuned. The run was done once.
- A hit means the right part is ranked first. We did not test whether a model then answers correctly.
- This shows how the pieces fit together, not a benchmark.

## Credit
Word vectors: GloVe 6B, 50 dimensions (`glove-wiki-gigaword-50`), Jeffrey Pennington, Richard Socher and Christopher D. Manning, "GloVe: Global Vectors for Word Representation" (EMNLP 2014), Stanford NLP, Public Domain Dedication and License v1.0. `vectors.json` contains only the words this demo uses.
