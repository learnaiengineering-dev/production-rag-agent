"""The thing we are testing: three small searches over 20 made-up pump parts (same code as 04c-hybrid).

Keyword: TF-IDF over whole tokens. Meaning: average of pretrained GloVe word vectors (a stand-in for an embedding model).
Hybrid: reciprocal rank fusion (k = 60) of the two. No API key, no downloads, no packages.
"""
import json, math, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = [tuple(x.strip() for x in l.split("|", 1)) for l in open(os.path.join(HERE, "parts.txt")) if l.strip()]
VEC = json.load(open(os.path.join(HERE, "vectors.json")))   # only the words used here, from GloVe 6B 50d
IDS = [p[0] for p in PARTS]
TEXTS = [f"{pid} {body}" for pid, body in PARTS]

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
    return sorted(range(len(s)), key=lambda i: (-s[i], i))


_kw, _mn = Keyword(TEXTS), Meaning(TEXTS)
def search_keyword(q): return IDS[_kw.rank(q)[0]]
def search_meaning(q): return IDS[_mn.rank(q)[0]]
def search_hybrid(q): return IDS[fuse([_kw.rank(q), _mn.rank(q)])[0]]
