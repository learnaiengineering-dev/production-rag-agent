"""One-off helper (you do not need to run it): rebuilds vectors.json, the GloVe vectors for the words used in this folder.

  Download glove-wiki-gigaword-50.gz (the Stanford GloVe 6B 50-dimension vectors) and run:
  python build_vectors.py glove-wiki-gigaword-50.gz

GloVe: Pennington, Socher and Manning, 2014. Released under the Public Domain Dedication and License v1.0.
"""
import gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
text = open(os.path.join(HERE, "parts.txt")).read() + open(os.path.join(HERE, "run.py")).read()
want = set()
for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()):
    want.add(w); want.update(w.split("-"))
vec = {}
with gzip.open(sys.argv[1], "rt", encoding="utf8") as f:
    next(f)
    for line in f:
        w, rest = line.split(" ", 1)
        if w in want: vec[w] = [round(float(x), 3) for x in rest.split()]
json.dump(vec, open(os.path.join(HERE, "vectors.json"), "w"), separators=(",", ":"), sort_keys=True)
print(len(vec), "words kept of", len(want), "wanted")
