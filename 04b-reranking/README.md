# 04b-reranking: a second look at the top results

Same returns policy (1,370 characters) and the same ten questions as `03c-chunking`. First stage: a fast keyword search fetches 3 candidates. Second stage: a reranker reorders only those 3. How often is the right chunk first, before and after?

```bash
python run.py
```

No API key, no downloads, no packages. It takes about a second and prints the same result every time.

## What is in the folder
- `policy.txt`: the document being searched.
- `run.py`: the ten questions, three ways of chunking, the first-stage search, a simple stand-in reranker, and the before-and-after counts. `run(chunks, reranker=your_function)` measures any reranker the same way: a function `(question, chunks, candidate_indexes)` that returns the indexes best first.
- `output.txt`: the output of the run on 8 Nov 2026 (Python 3.13.18, Linux sandbox).

## Result (right chunk ranked first, 150 questions = 10 questions x 15 chunkings)

| | Before reranking | After | Fixed | Made worse |
|---|---|---|---|---|
| Round 1: exact word matching | 108 | 103 | 3 | 8 |
| Round 2: strip a final "s" or "ed" in both stages | 114 | 128 | 16 | 2 |

The right chunk was in the top 3 for 141 of 150 in round 1 (143 in round 2), which is the most any reranker could reach. In the setup from Day 6 (300 characters, 60 overlap) the right chunk went from first for 8 of 10 questions to first for 8 (round 1) and 10 (round 2). With one candidate there is nothing to reorder.

## Read this before you quote the numbers
- The reranker is a deliberately simple stand-in that re-reads each candidate sentence by sentence. It is not a neural cross-encoder, and we did not test one.
- Round 1 was written before seeing any result. Round 2 was chosen after seeing round 1, on the same ten questions, so it is an illustration of the fix, not a clean test.
- One small document, questions written by us, keyword scoring instead of embeddings.
- A "hit" means every must-have phrase is inside the chunk put first. We did not test whether a model then answers correctly.
- Cost is the number of pairs scored (questions x candidates; 30 in the main setup). This stand-in is nearly free per pair, so nothing here measures the wait a real reranker model adds. Time yours.
- `04-reranking/` (an earlier draft that needs a model download) is a separate folder and was not run for these numbers.
