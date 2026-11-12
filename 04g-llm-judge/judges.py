"""Two automated checks for open-ended answers, plus an agreement check against human labels.

The 'stand-in judge' here is NOT a language model. It is a small, transparent
term-overlap rule, used only to demonstrate the one thing you must do with ANY
judge, including a real LLM one: measure how often it agrees with your own human
labels before you trust its score. For what a real LLM judge can and cannot tell
you, see README.md (sources).
"""
import csv, re

STOP = {"the", "a", "an", "is", "are", "to", "of", "for", "it", "its",
        "and", "or", "on", "in", "be", "that", "this", "use", "need",
        "does", "do", "what", "which"}

def norm(text):
    text = text.lower()
    # keep letters, digits and hyphens (so part numbers stay intact)
    toks = re.findall(r"[a-z0-9][a-z0-9\-]*", text)
    return toks

def key_terms(reference):
    return [t for t in norm(reference) if t not in STOP]

def exact_match(answer, reference):
    """Strict: the answer string must equal the reference string."""
    return " ".join(norm(answer)) == " ".join(norm(reference))

def stand_in_judge(answer, reference, threshold=0.5):
    """Term-overlap proxy. Pass if the answer contains at least `threshold`
    of the reference's key terms. Transparent and deterministic. Not an LLM."""
    ref = key_terms(reference)
    if not ref:
        return True
    ans = set(norm(answer))
    covered = sum(1 for t in ref if t in ans)
    return covered / len(ref) >= threshold

def load_items(path):
    rows = list(csv.DictReader(open(path, newline="")))
    for r in rows:
        assert r["human"] in ("pass", "fail"), f"{r['id']}: human must be pass/fail"
    return rows

def agreement(verdicts, humans):
    """Compare a checker's pass/fail verdicts to the human labels.
    Returns accuracy, false-pass (checker pass, human fail) and
    false-fail (checker fail, human pass) counts."""
    n = len(humans)
    correct = fp = ff = 0
    for v, h in zip(verdicts, humans):
        hv = (h == "pass")
        if v == hv:
            correct += 1
        elif v and not hv:
            fp += 1
        else:
            ff += 1
    return {"n": n, "correct": correct, "acc": correct / n,
            "false_pass": fp, "false_fail": ff}
