"""A small, deterministic keyword retrieval over the pump-parts corpus, with one
config knob - min_token_len - so we can simulate a change that 'improves'
tokenisation and quietly breaks exact part-number lookups.

Reused corpus from Day 8 / Day 11. No model, no installs."""
import re

def load_parts(path="parts.txt"):
    parts = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        pid, _, text = line.partition("|")
        parts.append((pid.strip(), text.strip()))
    return parts

def tokens(text, min_token_len):
    # keep hyphenated ids whole; min_token_len drops short tokens (the "improvement")
    raw = re.findall(r"[a-z0-9][a-z0-9\-]*", text.lower())
    out = []
    for t in raw:
        pieces = [t] if min_token_len <= 1 else [p for p in t.split("-") if len(p) >= min_token_len]
        out.extend(pieces if min_token_len > 1 else [t])
    return out

def make_search(parts, min_token_len=1):
    """Return a system(question)->part_id. Overlap score; ties go to the
    lexicographically smallest id, so the result is deterministic."""
    doc = [(pid, set(tokens(pid + " " + text, min_token_len))) for pid, text in parts]
    def search(question):
        q = set(tokens(question, min_token_len))
        best_id, best_score = None, -1
        for pid, dt in doc:
            score = len(q & dt)
            if score > best_score or (score == best_score and (best_id is None or pid < best_id)):
                best_id, best_score = pid, score
        return best_id
    return search
