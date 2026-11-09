"""Hybrid search: keyword search + meaning search, fused. Where does each one fail on part numbers?

  python run.py

20 made-up pump parts and 25 questions. No API key, no downloads, no packages.

Keyword search : TF-IDF over whole tokens. A part number like XR-4471-B stays ONE token.
Meaning search : the average of pretrained GloVe word vectors (50 numbers per word, Stanford NLP, public domain),
                 compared by cosine. A stand-in for an embedding model: it knows that "dripping" and "leaking" are
                 close, but it has never seen a part number. A word it does not know is split on "-" and only the known
                 pieces count.
Hybrid         : reciprocal rank fusion (k = 60, the usual default): each part scores 1/(60 + rank) in each list, summed.
Fixed in advance and not tuned. Parts and questions are small and written by us, so this shows the mechanism, not a benchmark.
"""
import json, math, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = [tuple(x.strip() for x in l.split("|", 1)) for l in open(os.path.join(HERE, "parts.txt")) if l.strip()]
VEC = json.load(open(os.path.join(HERE, "vectors.json")))   # only the words used here, from GloVe 6B 50d
IDS = [p[0] for p in PARTS]

# (kind, question, right part)
QUESTIONS = [
    ("id", "What torque for the gland bolts on XR-4471-D?", "XR-4471-D"),
    ("id", "Is XR-4417-B brass or stainless?", "XR-4417-B"),
    ("id", "What does the flashing red light on LM-7720-C mean?", "LM-7720-C"),
    ("id", "At what pressure does TK-0932 cut off?", "TK-0932"),
    ("id", "How often should I clean BN-1150?", "BN-1150"),
    ("id", "Does XR-4471-B fit the HP-400?", "XR-4471-B"),
    ("id", "Can I add WD-8808 six weeks after buying?", "WD-8808"),
    ("id", "What rating does the hose BN-1105 have?", "BN-1105"),
    ("id", "How long does the battery in HF-6100 last?", "HF-6100"),
    ("id", "Do I recalibrate HF-6016 after changing the impeller?", "HF-6016"),
    ("words", "My HP-200 is dripping near the shaft. What do I replace?", "XR-4471-B"),
    ("words", "The pump hums but no water comes out.", "ZP-2201"),
    ("words", "My HP-400 stops and flashes red, and the motor feels hot.", "LM-7720-C"),
    ("words", "How do I protect the pump from freezing weather?", "ZP-2210"),
    ("words", "The pump keeps running even though the tank is empty.", "TK-0392"),
    ("words", "My HP-200 makes a rattling sound and barely pushes any water.", "XR-4417-B"),
    ("words", "How do I cut down on vibration from the base?", "QS-3380"),
    ("words", "What happens when the pressure gets too high, and how do I get going again?", "TK-0932"),
    ("words", "How long am I covered if something breaks?", "WD-8800"),
    ("words", "Do I need an electrician to connect the HP-400 to power?", "VR-5010"),
    ("messy", "torque for xr 4471 d gland bolts", "XR-4471-D"),
    ("messy", "xr4417b material", "XR-4417-B"),
    ("messy", "lm7720c red light", "LM-7720-C"),
    ("messy", "tk 0932 cutoff pressure", "TK-0932"),
    ("messy", "BN1150 cleaning interval", "BN-1150"),
]
KINDS = {"id": "part number typed exactly", "words": "no part number, own words", "messy": "part number typed differently"}

STOP = set("a an the of to is are do i you we can if or and for it in on at by be my what how does when after even though about".split())
tok = lambda s: [w for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", s.lower()) if w not in STOP]


class Keyword:
    def __init__(self, texts):
        self.docs = [Counter(tok(t)) for t in texts]
        df = Counter(w for d in self.docs for w in d)
        self.idf = lambda w: math.log((1 + len(self.docs)) / (1 + df[w])) + 1
    def rank(self, q):
        qc = Counter(tok(q))
        def score(d):
            num = sum(qc[w] * d[w] * self.idf(w) ** 2 for w in qc)
            den = math.sqrt(sum((v * self.idf(w)) ** 2 for w, v in d.items())) * math.sqrt(sum((v * self.idf(w)) ** 2 for w, v in qc.items()))
            return num / den if den else 0
        return sorted(range(len(self.docs)), key=lambda i: (-score(self.docs[i]), i))


def embed(text):
    v, n = [0.0] * 50, 0
    for w in tok(text):
        for piece in ([w] if w in VEC else w.split("-")):
            if piece in VEC:
                v = [a + b for a, b in zip(v, VEC[piece])]; n += 1
    return [a / n for a in v] if n else v


def cos(a, b):
    d = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / d if d else 0


class Meaning:
    def __init__(self, texts): self.vecs = [embed(t) for t in texts]
    def rank(self, q):
        qv = embed(q)
        return sorted(range(len(self.vecs)), key=lambda i: (-cos(qv, self.vecs[i]), i))


def fuse(lists, k=60):
    s = Counter()
    for lst in lists:
        for r, i in enumerate(lst): s[i] += 1 / (k + r + 1)
    return sorted(range(len(s) or 0), key=lambda i: (-s[i], i)) if s else []


def lev(a, b):
    p = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        c = [i]
        for j, y in enumerate(b, 1): c.append(min(p[j] + 1, c[-1] + 1, p[j - 1] + (x != y)))
        p = c
    return p[-1]


def evaluate():
    texts = [f"{pid} {body}" for pid, body in PARTS]
    kw, mn = Keyword(texts), Meaning(texts)
    out = {k: {"keyword": [0, 0], "meaning": [0, 0], "hybrid": [0, 0]} for k in KINDS}
    sib = {"keyword": 0, "meaning": 0, "hybrid": 0}     # wrong first pick was a near-identical part number (id questions)
    detail = []
    for kind, q, right in QUESTIONS:
        ri = IDS.index(right)
        lists = {"keyword": kw.rank(q), "meaning": mn.rank(q)}
        lists["hybrid"] = fuse([lists["keyword"], lists["meaning"]])
        row = [kind, q, right]
        for name, lst in lists.items():
            pos = lst.index(ri) + 1
            out[kind][name][0] += pos == 1; out[kind][name][1] += pos <= 3
            if kind == "id" and pos != 1 and lev(IDS[lst[0]], right) <= 2: sib[name] += 1
            row.append(pos)
        detail.append(tuple(row))
    return out, sib, detail


if __name__ == "__main__":
    out, sib, detail = evaluate()
    print(f"{len(PARTS)} parts, {len(QUESTIONS)} questions. Right part ranked first (top 3 in brackets).\n")
    print(f"  {'question type':<34} | {'keyword':<9} | {'meaning':<9} | hybrid")
    tot = {"keyword": [0, 0], "meaning": [0, 0], "hybrid": [0, 0]}
    for k, label in KINDS.items():
        n = sum(1 for x in QUESTIONS if x[0] == k)
        cells = []
        for name in ("keyword", "meaning", "hybrid"):
            a, b = out[k][name]; tot[name][0] += a; tot[name][1] += b
            cells.append(f"{a}/{n} ({b})")
        print(f"  {label + ' (' + str(n) + ')':<34} | {cells[0]:<9} | {cells[1]:<9} | {cells[2]}")
    N = len(QUESTIONS)
    print(f"  {'all questions (' + str(N) + ')':<34} | " + " | ".join(f"{tot[n][0]}/{N} ({tot[n][1]})".ljust(9) for n in ("keyword", "meaning", "hybrid")).rstrip())
    print(f"\nExact part-number questions where the first pick was a near-identical part number (e.g. XR-4471-B for XR-4471-D):")
    print(f"  keyword {sib['keyword']} | meaning {sib['meaning']} | hybrid {sib['hybrid']}  (out of 10)")
    same = better = worse = 0
    for kind, q, right, a, b, c in detail:
        best = min(a, b)
        same += c == best; better += c < best; worse += c > best
    print(f"\nHybrid compared with the better of keyword and meaning, question by question (position of the right part):")
    print(f"  as good: {same} | better than both: {better} | worse: {worse}  (out of {N})")
    print("\nPosition of the right part, question by question (1 = first):")
    print(f"  {'type':<6} {'kw':>3} {'mn':>3} {'hy':>3} | question")
    for kind, q, right, a, b, c in detail:
        print(f"  {kind:<6} {a:>3} {b:>3} {c:>3} | {q}")
