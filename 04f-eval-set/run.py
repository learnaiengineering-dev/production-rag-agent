"""Your first 20-question eval set, run against three small searches (the same ones as 04c-hybrid).

  python run.py

questions.csv has 20 questions: 5 exact part numbers, 5 in our own words, 5 part numbers typed oddly, 5 that name
only the pump model (HP-200 or HP-400). The set was written before any search was run on it and was not changed
afterwards. Each question has ONE expected part, and it passes when the search ranks that part first.
Parts and questions are made up and written by us, so this shows the method, not a benchmark.
"""
import os
from evalkit import load_questions, run, wilson, by_tag, compare, gate
from searches import search_keyword, search_meaning, search_hybrid

HERE = os.path.dirname(os.path.abspath(__file__))
Q = load_questions(os.path.join(HERE, "questions.csv"))
SYSTEMS = [("keyword", search_keyword), ("meaning", search_meaning), ("hybrid", search_hybrid)]
R = {name: run(fn, Q) for name, fn in SYSTEMS}
N = len(Q)


def main():
    tags = list(by_tag(R["keyword"]))
    print(f"{N} questions, {len(tags)} kinds. Each has one expected part; it passes when that part is ranked first.\n")
    print("The grid (one row per question):")
    print(f"  {'id':<4} {'kind':<11} {'kw':<5} {'mn':<5} {'hy':<5} | question")
    for i, q in enumerate(Q):
        cells = ["pass" if R[n][i]["passed"] else "FAIL" for n, _ in SYSTEMS]
        print(f"  {q['id']:<4} {q['tag']:<11} {cells[0]:<5} {cells[1]:<5} {cells[2]:<5} | {q['question']}")
    print("\nPass counts by kind (a rough 95% range for the overall rate is in the last row):")
    print(f"  {'kind':<14} | {'keyword':<8} | {'meaning':<8} | hybrid")
    for t in tags:
        cells = []
        for n, _ in SYSTEMS:
            k, m = by_tag(R[n])[t]; cells.append(f"{k}/{m}")
        print(f"  {t:<14} | {cells[0]:<8} | {cells[1]:<8} | {cells[2]}")
    tot, rng = [], []
    for n, _ in SYSTEMS:
        k = sum(r["passed"] for r in R[n]); lo, hi = wilson(k, N)
        tot.append(f"{k}/{N}"); rng.append(f"{round(lo * 100)}-{round(hi * 100)}%")
    print(f"  {'all':<14} | {tot[0]:<8} | {tot[1]:<8} | {tot[2]}")
    print(f"  {'rough range':<14} | {rng[0]:<8} | {rng[1]:<8} | {rng[2]}")
    for a, b in (("keyword", "hybrid"), ("keyword", "meaning")):
        fixed, broke, still = compare(R[a], R[b])
        ok, regress = gate(R[a], R[b])
        print(f"\nChange from {a} to {b}: fixed {len(fixed)} ({', '.join(fixed) or 'none'}), broke {len(broke)} ({', '.join(broke) or 'none'}), still failing {len(still)}.")
        print(f"  Example rule 'block if anything that passed before now fails': {'OK to ship' if ok else 'BLOCKED by ' + ', '.join(regress)}")
    print("\nWhat the hybrid search got wrong (question: wanted, got):")
    for r in R["hybrid"]:
        if not r["passed"]:
            print(f"  {r['id']} {r['question']} -> wanted {r['expected']}, got {r['got']}")


if __name__ == "__main__":
    main()
