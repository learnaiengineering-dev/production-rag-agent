"""A tiny keyword index that remembers a content hash for every document, so it can
tell which documents changed since it was built. No model, no installs.

The trigger logic is the point: the same hashes work for a vector index, where
"re-index" means re-embedding only the documents that changed."""
import hashlib, json, re


def load_parts(path):
    parts = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            pid, _, text = line.partition("|")
            parts[pid.strip()] = text.strip()
    return parts


def content_hash(text):
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def tokens(text):
    return sorted(set(re.findall(r"[a-z0-9][a-z0-9\-]*", text.lower())))


def entry(pid, text):
    return {"hash": content_hash(text), "text": text, "tokens": tokens(pid + " " + text)}


def build(parts):
    return {pid: entry(pid, text) for pid, text in parts.items()}


def changes(index, parts):
    """Compare the index with the source. Returns (changed, added, removed, unchanged)."""
    changed = sorted(p for p in parts if p in index and index[p]["hash"] != content_hash(parts[p]))
    added = sorted(p for p in parts if p not in index)
    removed = sorted(p for p in index if p not in parts)
    unchanged = len(parts) - len(changed) - len(added)
    return changed, added, removed, unchanged


def sync(index, parts):
    """Re-index only what changed. Returns the list of documents it touched."""
    changed, added, removed, _ = changes(index, parts)
    for p in changed + added:
        index[p] = entry(p, parts[p])
    for p in removed:
        del index[p]
    return changed + added + removed


def search(index, question):
    """Best keyword overlap; ties go to the smallest id, so results are deterministic."""
    q = set(tokens(question))
    best = max(sorted(index), key=lambda p: len(q & set(index[p]["tokens"])))
    return best, index[best]["text"]


def save(index, path):
    json.dump(index, open(path, "w"), indent=1)


def load(path):
    return json.load(open(path))
