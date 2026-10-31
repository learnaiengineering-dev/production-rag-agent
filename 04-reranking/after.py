"""After: fetch 6 candidates with vector search, then let a cross-encoder reorder them.

Setup (once):  python -m venv .venv && .venv/bin/pip install sentence-transformers
"""
from sentence_transformers import CrossEncoder, SentenceTransformer
from data import CHUNKS, QUESTIONS

CANDIDATES = 6
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
chunk_vecs = model.encode(CHUNKS, normalize_embeddings=True)

hits = 0
for question, answer in QUESTIONS:
    q = model.encode([question], normalize_embeddings=True)[0]
    top = list((chunk_vecs @ q).argsort()[::-1][:CANDIDATES])
    scores = reranker.predict([(question, CHUNKS[i]) for i in top])
    reranked = [top[i] for i in scores.argsort()[::-1]]
    rank = reranked.index(answer) + 1 if answer in reranked else None
    hits += rank == 1
    print(f"rank {rank if rank else 'not in the top ' + str(CANDIDATES):>2} for the right chunk | {question}")
print(f"\nright chunk first: {hits} of {len(QUESTIONS)} questions (vector search, then rerank the top {CANDIDATES})")
