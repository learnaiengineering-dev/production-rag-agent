"""Day 18: multi-tenant filtering - when Customer A sees Customer B's file.

Two made-up customers (Acme Pumps, Bayside Plumbing) share one index with a shared
product catalogue. 14 questions, 7 from each customer, each with the document that
should answer it. Three ways to search, top 3 results each:
  1. no tenant filter
  2. filter AFTER taking the top 3 (and the top 1)
  3. filter INSIDE the query (only this tenant's + shared documents are scored)

    python3 run.py
No installs, no internet, no API key. Python 3.9+."""
import csv
from search import load, search_unfiltered, search_post_filter, search

docs = load()
qs = list(csv.DictReader(open("questions.csv", encoding="utf-8")))
K = 3


def score(name, fn):
    leaks = top1_wrong = answered = 0
    examples = []
    for q in qs:
        res = fn(q)
        foreign = [d for d in res if d["tenant"] not in (q["tenant"], "shared")]
        leaks += bool(foreign)
        if res and res[0]["tenant"] not in (q["tenant"], "shared"):
            top1_wrong += 1
            examples.append((q, res[0]))
        answered += any(d["id"] == q["expected"] for d in res)
    return name, leaks, top1_wrong, answered, examples


rows = [score("no tenant filter", lambda q: search_unfiltered(docs, q["question"], K)),
        score("filter after top 3", lambda q: search_post_filter(docs, q["question"], q["tenant"], K)),
        score("filter in the query", lambda q: search(docs, q["question"], tenant=q["tenant"], k=K))]
one = [score("filter after top 1", lambda q: search_post_filter(docs, q["question"], q["tenant"], 1)),
       score("filter in the query", lambda q: search(docs, q["question"], tenant=q["tenant"], k=1))]
empty1 = sum(not search_post_filter(docs, q["question"], q["tenant"], 1) for q in qs)

print("multi-tenant filtering")
print("=" * 60)
print(f"{len(docs)} documents (6 Acme, 6 Bayside, 6 shared), {len(qs)} questions, top {K}\n")
print(f"{'search':<22}{'leaked':>8}{'wrong #1':>10}{'answered':>10}   (of {len(qs)})")
for name, leaks, top1, ans, _ in rows:
    print(f"{name:<22}{leaks:>8}{top1:>10}{ans:>10}")
print(f"\nwith only the top result (k=1):")
for name, leaks, top1, ans, _ in one:
    print(f"{name:<22}{leaks:>8}{top1:>10}{ans:>10}")
print(f"filter after top 1 left {empty1} of {len(qs)} questions with no result at all")
print("\nleaked   = another customer's document in the top 3")
print("wrong #1 = the top result belongs to another customer")
print("answered = the right document is in what the user gets\n")
print("examples with no filter (top result is the other customer's):")
for q, d in rows[0][4]:
    print(f"  {q['tenant']:<8} asks: {q['question']}")
    print(f"           gets {d['id']}: {d['text']}")
missed = [q for q in qs if not search_post_filter(docs, q["question"], q["tenant"], 1)]
print("\nfilter after top 1 - no leak, but these got nothing back:")
for q in missed:
    print(f"  {q['tenant']:<8} {q['question']}")
