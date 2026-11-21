"""Day 21: version prompts like code.

A prompt is code: it changes behaviour, so it gets the same treatment.
  1. one file per version, reviewed as a diff
  2. an eval run before the new version goes live (a gate)
  3. every answer logged with the prompt's version and hash
  4. released versions locked by hash, so an in-place edit is refused
  5. rollback = change one line in the lock file

The model is a rule-based stand-in (answerer.py) so this runs with no API key.

    python3 run.py
No installs, no internet. Python 3.9+."""
import csv, difflib, json, os, shutil, tempfile
from registry import load
from answerer import answer

NAME = "support-answer"
from registry import read
docs = [json.loads(l) for l in read("docs.jsonl").splitlines()]
qs = list(csv.DictReader(read("questions.csv").splitlines()))


def evaluate(version):
    v, h, prompt = load(NAME, version)
    rows = []
    for q in qs:
        reply, doc = answer(prompt, q["question"], docs)
        ok = (doc is None) if q["expect"] == "dont_know" else (doc == q["expect"])
        rows.append({"prompt": NAME, "version": v, "hash": h, "question": q["question"],
                     "expect": q["expect"], "doc": doc, "ok": ok, "reply": reply})
    return rows


def score(rows, kind=None):
    rs = [r for r in rows if kind is None or (r["expect"] == "dont_know") == (kind == "out")]
    return sum(r["ok"] for r in rs), len(rs)


print("version prompts like code: support-answer v1 -> v2")
print("=" * 66)

print("\n1. the change, as a diff (the 'tidy up the wording' edit)\n")
a = read(f"prompts/{NAME}/v1.txt").splitlines()
b = read(f"prompts/{NAME}/v2.txt").splitlines()
for line in difflib.unified_diff(a, b, "v1.txt", "v2.txt", lineterm="", n=0):
    if not line.startswith("@@"):
        print("  " + line)

print(f"\n2. eval before release: {len(qs)} questions, 4 the docs don't cover\n")
res = {v: evaluate(v) for v in ("v1", "v2")}
print(f"  {'version':<9}{'hash':<10}{'all':>8}{'covered':>10}{'not covered':>14}")
for v, rows in res.items():
    s, n = score(rows); c, cn = score(rows, "in"); o, on = score(rows, "out")
    print(f"  {v:<9}{rows[0]['hash']:<10}{s:>4} of {n}{c:>5} of {cn}{o:>8} of {on}")
live, cand = score(res["v1"])[0], score(res["v2"])[0]
print(f"\n  gate: v2 scores {cand}, live v1 scores {live} -> "
      + ("RELEASE" if cand >= live else "BLOCKED, v1 stays live"))
print("\n  what v2 said to questions the docs don't cover:")
for r in res["v2"]:
    if r["expect"] == "dont_know":
        print(f"    {r['question']:<52} -> [{r['doc']}] guessed")

print("\n3. every answer is logged with the prompt's version and hash")
os.makedirs("logs", exist_ok=True)
with open("logs/answers.jsonl", "w") as f:
    for r in res["v1"][:2] + res["v2"][8:10]:
        f.write(json.dumps({k: r[k] for k in ("prompt", "version", "hash", "question", "doc")}) + "\n")
for line in read("logs/answers.jsonl").splitlines():
    print("  " + line.rstrip())

print("\n4. a released version can't change quietly")
tmp = tempfile.mkdtemp()
shutil.copytree(".", tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns("logs", "__pycache__"))
with open(os.path.join(tmp, "prompts", NAME, "v1.txt"), "a") as f:
    f.write("Be friendly.\n")  # an 'in-place' edit to the live version
try:
    load(NAME, root=tmp)
    print("  edited v1 loaded (this should not happen)")
except ValueError as e:
    print(f"  refused: {e}")
shutil.rmtree(tmp)

print("\n5. rollback is one line: prompts.lock.json -> \"live\": \"v1\"")
v, h, _ = load(NAME)
print(f"  live now: {NAME} {v} ({h})")
