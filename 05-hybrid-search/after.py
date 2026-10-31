"""After: run keyword search (BM25) and vector search, then merge the two rankings
with reciprocal rank fusion.

Setup (once):  python -m venv .venv && .venv/bin/pip install sentence-transformers rank-bm25
"""
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from data import CHUNKS, QUESTIONS

K = 60  # the usual reciprocal-rank-fusion constant


def tokens(text):
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


bm25 = BM25Okapi([tokens(c) for c in CHUNKS])
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chunk_vecs = model.encode(CHUNKS, normalize_embeddings=True)


def fused_order(query):
    kw = list(bm25.get_scores(tokens(query)).argsort()[::-1])
    q = model.encode([query], normalize_embeddings=True)[0]
    vec = list((chunk_vecs @ q).argsort()[::-1])
    score = {i: 0.0 for i in range(len(CHUNKS))}
    for ranking in (kw, vec):
        for pos, i in enumerate(ranking):
            score[i] += 1 / (K + pos + 1)
    return sorted(score, key=score.get, reverse=True)


first = {"part number": 0, "plain words": 0}
count = {"part number": 0, "plain words": 0}
for query, answer, kind in QUESTIONS:
    rank = fused_order(query).index(answer) + 1
    count[kind] += 1
    first[kind] += rank == 1
    print(f"rank {rank:>2} | {kind:<11} | {query}")
for kind in first:
    print(f"{kind}: right chunk first for {first[kind]} of {count[kind]} (keyword + vector, fused)")
