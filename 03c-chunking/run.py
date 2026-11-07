"""Why does retrieval return the wrong chunk? Same document, same questions, three ways to cut it up.

  python run.py

No API key and no downloads: retrieval here is plain TF-IDF keyword scoring, written in ~15 lines.
(A neural embedding model scores differently, but a fact cut in half is cut in half for any retriever.)
The document and the 10 questions are small and written by us, so this shows the mechanism,
not how your own data will behave.
"""
import math, re
from collections import Counter

import os
DOC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "policy.txt")).read()
SIZE = 300
OVERLAP = SIZE // 5

# (question, phrases that must ALL be inside the chunk we retrieve for it to count as a hit)
QUESTIONS = [
    ("How many days do I have to return a sale item?", ["14 days"]),
    ("Who pays return shipping for a faulty item?", ["cover the return shipping"]),
    ("How long until I get my refund after you receive the item?", ["5 business days"]),
    ("What happens to a gift card purchase refund?", ["store credit"]),
    ("Does store credit expire?", ["never expires"]),
    ("Can I return a personalised item?", ["personalised items"]),
    ("How do I start a return?", ["Orders page"]),
    ("What do I need to send for a faulty item?", ["photo of the fault"]),
    ("Can I exchange an item after the 30 day window?", ["30 day window", "not accepted"]),
    ("Can I return food or fuel canisters?", ["Perishable", "excluded"]),
]


def fixed(text, size, overlap):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


def by_sentence(text, size):
    """Pack whole sentences into a chunk until the next one would not fit."""
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text.strip()):
        if cur and len(cur) + 1 + len(s) > size:
            out.append(cur); cur = s
        else:
            cur = f"{cur} {s}".strip()
    return out + [cur] if cur else out


STOP = set("a an the of to is are do i you we can if or and for it in on at by be my what how who does after when".split())
tok = lambda s: [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]


def top(question, chunks, k=1):
    docs = [Counter(tok(c)) for c in chunks]
    df = Counter(w for d in docs for w in d)
    idf = lambda w: math.log((1 + len(docs)) / (1 + df[w])) + 1
    q = Counter(tok(question))
    def score(d):
        num = sum(q[w] * d[w] * idf(w) ** 2 for w in q)
        den = math.sqrt(sum((v * idf(w)) ** 2 for w, v in d.items())) * math.sqrt(sum((v * idf(w)) ** 2 for w, v in q.items()))
        return num / den if den else 0
    return sorted(range(len(chunks)), key=lambda i: -score(docs[i]))[:k]


def evaluate(name, chunks, quiet=False):
    hit1 = hit3 = cut = 0
    rows = []
    for q, must in QUESTIONS:
        whole = any(all(m in c for m in must) for c in chunks)     # is the fact in ONE chunk at all?
        cut += not whole
        ok1 = all(m in chunks[top(q, chunks, 1)[0]] for m in must)
        ok3 = any(all(m in chunks[i] for m in must) for i in top(q, chunks, 3))
        hit1 += ok1; hit3 += ok3
        rows.append((q, whole, ok1))
    if quiet:
        return hit1, hit3, cut
    print(f"{name}: {len(chunks)} chunks | answer in the top chunk: {hit1} of {len(QUESTIONS)} | in the top 3: {hit3} of {len(QUESTIONS)} | facts cut across two chunks: {cut}")
    return rows, chunks


if __name__ == "__main__":
    print(f"Document: {len(DOC)} characters, {len(QUESTIONS)} questions, chunk size {SIZE}\n")
    a, ca = evaluate(f"1. Fixed {SIZE} characters, no overlap   ", fixed(DOC, SIZE, 0))
    b, cb = evaluate(f"2. Fixed {SIZE} characters, {OVERLAP} overlap  ", fixed(DOC, SIZE, OVERLAP))
    c, cc = evaluate(f"3. Whole sentences, up to {SIZE} chars", by_sentence(DOC, SIZE))
    print("\nQuestions the fixed, no-overlap split got wrong:")
    for q, whole, ok in a:
        if not ok:
            print(f"  - {q}  ({'fact is split across two chunks' if not whole else 'fact is whole, but another chunk scored higher'})")
    print("\nOne example, in full (setup 1):")
    for q, whole, ok in a:
        if not ok and not whole:
            must = dict(QUESTIONS)[q]
            i = top(q, ca, 1)[0]
            b = next(k * SIZE for k in range(1, len(DOC) // SIZE + 1) if any(DOC.find(m) < k * SIZE < DOC.find(m) + len(m) for m in must if DOC.find(m) >= 0))
            print(f"  Question: {q}")
            print(f"  Chunk returned ({i + 1} of {len(ca)}) ends with:  \"...{ca[i][-40:].strip()}\"")
            print(f"  The cut falls here:  \"...{DOC[b - 30:b]}\" | \"{DOC[b:b + 30]}...\"".replace("\n", " "))
            break
    print("\nDoes the answer depend on the chunk size? (top-chunk hits out of 10 / facts cut in two)")
    print("  size | fixed, no overlap | fixed, 20% overlap | whole sentences")
    for size in (150, 200, 300, 400, 600):
        r1 = evaluate("", fixed(DOC, size, 0), True)
        r2 = evaluate("", fixed(DOC, size, size // 5), True)
        r3 = evaluate("", by_sentence(DOC, size), True)
        print(f"  {size:>4} | {r1[0]:>2} / {r1[2]:<2}            | {r2[0]:>2} / {r2[2]:<2}             | {r3[0]:>2} / {r3[2]:<2}")
