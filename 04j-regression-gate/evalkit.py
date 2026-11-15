"""A tiny, reusable eval runner. Copy this file and questions.csv, then plug in your own system.

A question set is a CSV: id, tag, question, expected. A "system" is any function that takes a question (text) and
returns an answer (text). A question passes when check(got, expected) is true; the default is an exact match.
"""
import csv, math
from collections import OrderedDict


def load_questions(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    need = {"id", "tag", "question", "expected"}
    if not rows or not need <= set(rows[0]):
        raise ValueError("questions file needs the columns: id, tag, question, expected")
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("question ids must be unique")
    for r in rows:
        if not r["question"].strip() or not r["expected"].strip():
            raise ValueError(f"{r['id']}: every question needs a question and an expected answer")
    return rows


def run(system, questions, check=lambda got, expected: got == expected):
    out = []
    for q in questions:
        got = system(q["question"])
        out.append({**q, "got": got, "passed": bool(check(got, q["expected"]))})
    return out


def wilson(k, n, z=1.96):
    """A rough 95% range for a pass rate of k out of n (Wilson score interval)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def by_tag(results):
    tags = OrderedDict()
    for r in results:
        t = tags.setdefault(r["tag"], [0, 0])
        t[0] += r["passed"]; t[1] += 1
    return tags


def compare(before, after):
    """Question by question: what got fixed, what broke, what still fails."""
    fixed = [a["id"] for b, a in zip(before, after) if not b["passed"] and a["passed"]]
    broke = [a["id"] for b, a in zip(before, after) if b["passed"] and not a["passed"]]
    still = [a["id"] for b, a in zip(before, after) if not b["passed"] and not a["passed"]]
    return fixed, broke, still


def gate(before, after):
    """One example rule: block the change if any question that passed before now fails."""
    _, broke, _ = compare(before, after)
    return (len(broke) == 0, broke)
