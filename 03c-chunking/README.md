# 03c-chunking: why retrieval returns the wrong chunk

One returns policy (1,370 characters), ten customer questions, three ways of cutting the text into chunks. How often does a keyword search put the right chunk first?

```bash
python run.py
```

No API key, no downloads, no packages: retrieval is plain TF-IDF keyword scoring written in about 15 lines. `python run.py` takes about a second and prints the same result every time.

## What is in the folder
- `policy.txt`: the document being searched.
- `run.py`: the ten questions (each with the words the right chunk must contain), the three chunking methods, the retrieval, and a size comparison.
- `output.txt`: the output from the run on 7 Nov 2026 (Python 3.13.18, Linux sandbox).

## Result at 300 characters

| Method | Chunks | Right chunk first | In top 3 | Facts cut in two |
|---|---|---|---|---|
| Fixed, no overlap | 5 | 6 of 10 | 8 of 10 | 1 |
| Fixed, 60 overlap | 6 | 8 of 10 | 10 of 10 | 0 |
| Whole sentences | 6 | 7 of 10 | 9 of 10 | 0 |

Across five sizes (150, 200, 300, 400, 600) and the three methods, 15 setups: the right chunk came first for 5 to 9 of 10 questions, none got all ten, a fact was cut in two in 2 of 15 setups, and overlap helped at 300 and 400 but changed nothing at 150, 200 or 600.

## Read this before you quote the numbers
- One small document and ten questions written by us. This shows the mechanism, not how your data will behave.
- Keyword scoring, not neural embeddings. Embeddings score differently, but a fact cut in half is cut in half for any retriever.
- A "hit" means every must-have phrase is inside the retrieved chunk. We did not test whether a model then answers correctly.
- Try it on your own text: replace `policy.txt`, rewrite `QUESTIONS` in `run.py`, and run it.
