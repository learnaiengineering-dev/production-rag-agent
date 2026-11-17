"""Day 16: when knowledge goes stale.

1. The index was built from last month's documents (parts_v1.txt).
2. The source has moved on (parts.txt): one document changed, one was replaced.
3. Before re-indexing, answers still quote the old text.
4. A content-hash check finds exactly what changed; re-index only that.
5. Ask again.

    python3 run.py
No installs, no internet, no API key. Python 3.9+."""
from index import load_parts, build, changes, sync, search, content_hash

QUESTIONS = ["How long does the standard warranty last?",
             "Which outlet hose should I order?"]

source = load_parts("parts.txt")


def ask(index, label):
    print(label)
    for q in QUESTIONS:
        pid, text = search(index, q)
        fresh = pid in source and content_hash(source[pid]) == index[pid]["hash"]
        state = "fresh" if fresh else ("STALE: removed from the source" if pid not in source
                                       else "STALE: the source has changed")
        print(f"  Q: {q}")
        print(f"     -> {pid}: {text}")
        print(f"     [{state}]")
    print()


index = build(load_parts("parts_v1.txt"))
print("re-index triggers")
print("=" * 48)
print(f"index built from parts_v1.txt: {len(index)} documents")
print(f"source today (parts.txt):      {len(source)} documents")
print()
ask(index, "BEFORE re-indexing")

changed, added, removed, unchanged = changes(index, source)
print("content-hash check")
print(f"  changed  : {changed or '-'}")
print(f"  added    : {added or '-'}")
print(f"  removed  : {removed or '-'}")
print(f"  unchanged: {unchanged}")
touched = sync(index, source)
print(f"  re-indexed {len(changed) + len(added)}, deleted {len(removed)}, left {unchanged} alone"
      f" (a full rebuild would redo all {len(source)})")
print()
ask(index, "AFTER re-indexing")

left = changes(index, source)
print("check again:", "nothing has changed since the last sync" if not any(left[:3]) else left)
