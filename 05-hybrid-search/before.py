"""Before: vector search only.

Setup (once):  python -m venv .venv && .venv/bin/pip install sentence-transformers rank-bm25
"""
from sentence_transformers import SentenceTransformer
from data import CHUNKS, QUESTIONS

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chunk_vecs = model.encode(CHUNKS, normalize_embeddings=True)

first = {"part number": 0, "plain words": 0}
count = {"part number": 0, "plain words": 0}
for query, answer, kind in QUESTIONS:
    q = model.encode([query], normalize_embeddings=True)[0]
    order = list((chunk_vecs @ q).argsort()[::-1])
    rank = order.index(answer) + 1
    count[kind] += 1
    first[kind] += rank == 1
    print(f"rank {rank:>2} | {kind:<11} | {query}")
for kind in first:
    print(f"{kind}: right chunk first for {first[kind]} of {count[kind]} (vector search only)")
