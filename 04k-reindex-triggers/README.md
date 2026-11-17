# 04k - Re-index triggers: when knowledge goes stale

Day 16 of the series. Your assistant can quote last month's policy with total
confidence. The source document changed; the index didn't. Nothing errors.

The fix is a trigger, not a timetable: keep a **content hash** for every document
you index. Before you trust the index, compare those hashes with the source. Anything
that changed, appeared or disappeared gets re-indexed or deleted - and only that.

## Run it

```
python3 run.py
```

No installs, no internet, no API key. Python 3.9+.

## What happens (`output.txt`)

| Step | Result |
|---|---|
| Index built from `parts_v1.txt` (last month) | 20 documents |
| Source today (`parts.txt`) | 1 changed (`WD-8800`), 1 replaced (`BN-1105` -> `BN-1106`) |
| Before re-indexing | "standard warranty" -> 24 months (source says 36). "outlet hose" -> `BN-1105`, which no longer exists. Both flagged STALE. |
| Content-hash check | changed `WD-8800`, added `BN-1106`, removed `BN-1105`, 18 unchanged |
| Sync | 2 re-indexed, 1 deleted, 18 left alone |
| After | Both answers match the source. A second check finds nothing to do. |

## The pieces

- `index.py` - `content_hash()`, `changes()` (changed / added / removed) and `sync()`.
- `run.py` - the before-and-after above.
- `parts_v1.txt` / `parts.txt` - the corpus from Days 8, 11 and 15, before and after the edits.

## Using it on a real system

- Store the hash next to each chunk or document in your vector store's metadata.
- Run the check when content changes (a webhook, a commit, a CMS publish) and on a
  schedule as a safety net. The check is cheap; re-embedding is the expensive part.
- Deletes matter as much as edits: a removed document that is still in the index is a
  stale answer waiting to happen.
- Re-run your eval set (Day 11) after a large sync - and wire it into the gate (Day 15).

## Honest caveats

- The edits are examples written for the demo (the warranty change is made up for
  this toy corpus). Keyword search stands in for embeddings; the trigger logic is the same.
- The hash is per document. If you chunk, hash per chunk or re-chunk the changed document.
- A hash tells you the text changed, not whether the change matters. Re-index anyway.
