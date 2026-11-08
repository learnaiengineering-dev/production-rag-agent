"""Reranking: fetch a few candidates with the first-stage search, then reorder them with a second, finer scorer.

  python run.py

Same returns policy and the same ten questions as folder 03c-chunking (Day 6). No API key, no downloads, no packages.

First stage  : TF-IDF keyword scoring over whole chunks (the same ~15 lines as Day 6).
Second stage : a deliberately simple stand-in reranker. It re-reads each candidate sentence by sentence and scores the
               best sentence by how much of the question's weight it covers. A real reranker (a cross-encoder model)
               reads the question and the text together and is much stronger; this stand-in only shows what the
               second stage DOES and how to measure it. It was written once, before the numbers below, and not tuned.
The document and the 10 questions are small and written by us, so this shows the mechanism, not a benchmark.
"""
import math, os, re
from collections import Counter

DOC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "policy.txt")).read()
CANDIDATES = 3      # how many first-stage results the reranker is allowed to reorder

# (question, phrases that must ALL be inside the chunk we put first for it to count as a hit)
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
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text.strip()):
        if cur and len(cur) + 1 + len(s) > size:
            out.append(cur); cur = s
        else:
            cur = f"{cur} {s}".strip()
    return out + [cur] if cur else out


STOP = set("a an the of to is are do i you we can if or and for it in on at by be my what how who does after when".split())
STRIP_ENDINGS = False   # round 1: exact words only. Round 2 turns this on (see the bottom of this file).


def tok(s):
    words = [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]
    if STRIP_ENDINGS:   # "items" -> "item", "returned" -> "return" (crude: drops a final "s" or "ed")
        words = [re.sub(r"(ed|s)$", "", w) if len(w) > 3 else w for w in words]
    return words


def first_stage(question, chunks, k):
    """TF-IDF cosine over whole chunks. Returns chunk indexes, best first."""
    docs = [Counter(tok(c)) for c in chunks]
    df = Counter(w for d in docs for w in d)
    idf = lambda w: math.log((1 + len(docs)) / (1 + df[w])) + 1
    q = Counter(tok(question))
    def score(d):
        num = sum(q[w] * d[w] * idf(w) ** 2 for w in q)
        den = math.sqrt(sum((v * idf(w)) ** 2 for w, v in d.items())) * math.sqrt(sum((v * idf(w)) ** 2 for w, v in q.items()))
        return num / den if den else 0
    return sorted(range(len(chunks)), key=lambda i: -score(docs[i]))[:k]


SENTENCES = re.split(r"(?<=[.!?])\s+", " ".join(DOC.split()))


def _sidf(w):
    df = sum(1 for s in SENTENCES if w in set(tok(s)))
    return math.log((1 + len(SENTENCES)) / (1 + df)) + 1


def rerank(question, chunks, candidates):
    """Second stage: score each candidate by its best sentence = share of the question's weight that sentence covers."""
    q = set(tok(question))
    total = sum(_sidf(w) for w in q) or 1
    def chunk_score(i):
        return max((sum(_sidf(w) for w in q & set(tok(s))) / total
                    for s in re.split(r"(?<=[.!?])\s+", " ".join(chunks[i].split()))), default=0)
    order = sorted(range(len(candidates)), key=lambda r: (-chunk_score(candidates[r]), r))   # ties keep the first-stage order
    return [candidates[r] for r in order]


def holds(chunk, must):
    return all(m in " ".join(chunk.split()) or m in chunk for m in must)


def run(chunks, k=CANDIDATES, reranker=None):
    """Returns (right chunk first before, after, in the candidate list at all, fixed by rerank, broken by rerank)."""
    reranker = reranker or rerank      # plug in your own: a function (question, chunks, candidate_indexes) -> indexes, best first
    before = after = ceiling = fixed_n = broke_n = 0
    detail = []
    for q, must in QUESTIONS:
        cands = first_stage(q, chunks, k)
        new = reranker(q, chunks, cands)
        b, a = holds(chunks[cands[0]], must), holds(chunks[new[0]], must)
        before += b; after += a
        ceiling += any(holds(chunks[i], must) for i in cands)
        fixed_n += (not b) and a; broke_n += b and (not a)
        detail.append((q, b, a, cands, new))
    return before, after, ceiling, fixed_n, broke_n, detail


def report(round_name, show_candidates_table):
    N = len(QUESTIONS)
    chunks = fixed(DOC, 300, 60)
    b, a, c, f, w, detail = run(chunks)
    print(f"=== {round_name} ===\n")
    print(f"Chunks: fixed 300 characters, 60 overlap ({len(chunks)} chunks), {CANDIDATES} candidates")
    print(f"  right chunk first, before rerank : {b} of {N}")
    print(f"  right chunk first, after rerank  : {a} of {N}")
    print(f"  right chunk in the {CANDIDATES} candidates   : {c} of {N}  (the most a reranker can reach)")
    print(f"  fixed by rerank: {f} | made worse by rerank: {w}")
    print(f"  pairs the reranker had to score  : {N * CANDIDATES} ({N} questions x {CANDIDATES} candidates)\n")
    print("Rank table, question by question (position of the right chunk; '-' = not in the candidates):")
    for q, bb, aa, cands, new in detail:
        must = dict(QUESTIONS)[q]
        pos = lambda lst: next((str(j + 1) for j, i in enumerate(lst) if holds(chunks[i], must)), "-")
        print(f"  before {pos(cands):>1} -> after {pos(new):>1} | {q}")
    if show_candidates_table:
        print("\nHow many candidates should the reranker see? (right chunk first, out of 10; chunks: fixed 300, 60 overlap)")
        print("  candidates | before | after | in candidates | pairs scored")
        for k in (1, 2, 3, 5, len(chunks)):
            bb, aa, cc, _, _, _ = run(chunks, k)
            print(f"  {k:>10} | {bb:>6} | {aa:>5} | {cc:>13} | {N * k:>12}")
    print("\nDoes it help for every way of cutting? (right chunk first, out of 10: before -> after reranking the top 3)")
    print("  size | fixed, no overlap | fixed, 20% overlap | whole sentences")
    tot_b = tot_a = tot_c = tot_f = tot_w = 0
    for size in (150, 200, 300, 400, 600):
        row = []
        for ch in (fixed(DOC, size, 0), fixed(DOC, size, size // 5), by_sentence(DOC, size)):
            bb, aa, cc, ff, ww, _ = run(ch)
            row.append(f"{bb:>2} -> {aa:>2}")
            tot_b += bb; tot_a += aa; tot_c += cc; tot_f += ff; tot_w += ww
        print(f"  {size:>4} | {row[0]:<17} | {row[1]:<18} | {row[2]}")
    print(f"\nAcross the 15 setups (150 questions in total):")
    print(f"  right chunk first before reranking : {tot_b}")
    print(f"  right chunk in the top 3 at all    : {tot_c}  (the most any reranker could reach)")
    print(f"  right chunk first after reranking  : {tot_a}")
    print(f"  fixed by the reranker: {tot_f} | made worse by the reranker: {tot_w}")


if __name__ == "__main__":
    print(f"Document: {len(DOC)} characters, {len(QUESTIONS)} questions. First stage fetches {CANDIDATES} candidates; the reranker reorders them.\n")
    report("Round 1: exact words only (written once, before seeing any result)", True)
    # Round 1 made some answers worse. Looking at why: "item" does not match "items" and "return" does not match "returned",
    # in the first stage and in the reranker. Round 2 changes only that, in both stages. It was decided AFTER seeing the
    # round 1 results, on the same ten questions, so read it as an illustration of the fix, not as a clean test.
    STRIP_ENDINGS = True
    print()
    report("Round 2: same code, but word endings ('s', 'ed') stripped in both stages (changed after seeing round 1)", False)
