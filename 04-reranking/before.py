"""Before: take the top result straight from vector search.

Setup (once):  python -m venv .venv && .venv/bin/pip install sentence-transformers
"""
from sentence_transformers import SentenceTransformer
from data import CHUNKS, QUESTIONS

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chunk_vecs = model.encode(CHUNKS, normalize_embeddings=True)

hits = 0
for question, answer in QUESTIONS:
    q = model.encode([question], normalize_embeddings=True)[0]
    scores = chunk_vecs @ q
    order = scores.argsort()[::-1]
    rank = int(list(order).index(answer)) + 1
    hits += rank == 1
    print(f"rank {rank:>2} for the right chunk | {question}")
print(f"\nright chunk first: {hits} of {len(QUESTIONS)} questions (vector search only)")
