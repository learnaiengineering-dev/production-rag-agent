# 04m - Multi-tenant filtering: when Customer A sees Customer B's file

Day 18 of the series. Put every customer's documents in one index, forget the tenant
filter once, and the search happily returns the best match - from someone else's
contract. Nothing errors. The answer is just another customer's data.

## Run it

```
python3 run.py                 # the comparison
python3 -m unittest -v         # the test that guards it
```

No installs, no internet, no API key. Python 3.9+.

## What happens (`output.txt`, `test-output.txt`)

Two made-up customers, Acme Pumps and Bayside Plumbing, share one index with a shared
product catalogue: 18 documents, 14 questions (7 per customer), each with the document
that should answer it.

| Search | Another customer's doc in the top 3 | Top result is another customer's | Right answer returned |
|---|---|---|---|
| No tenant filter | 12 of 14 | 7 of 14 | 14 of 14 |
| Filter after the top 3 | 0 | 0 | 14 of 14 |
| Filter after the top 1 | 0 | 0 | 7 of 14 (the other 7 get nothing) |
| Filter inside the query | 0 | 0 | 14 of 14 |

Example with no filter: Bayside asks "Can we return unused parts for a refund?" and gets
Acme's returns policy (60 days, full refund). Bayside's own policy is 30 days, store credit.
Wrong answer, and another customer's contract terms in the same breath.

Filtering after retrieval stops the leak but costs answers: the top results were spent on
documents the user can't see. Filter inside the query, so only this tenant's and shared
documents are ever scored.

## The pieces

- `search.py` - `search(docs, question, *, tenant)`: tenant is keyword-only with no default,
  so forgetting it is a `TypeError`, not a quiet leak. Plus the two unsafe versions for comparison.
- `test_tenant.py` - asks every question as every tenant and fails if any result belongs to
  another tenant; also checks that a missing tenant raises.
- `run.py`, `docs.jsonl`, `questions.csv`.

## Using it on a real system

- Put the tenant id in each chunk's metadata and use your vector store's metadata filter in the
  query itself, not on the results afterwards.
- Take the tenant from the authenticated session on the server, never from the request body or
  the prompt.
- Make the filter impossible to forget: one search function that requires it, and a test like
  `test_tenant.py` in CI (Day 15's gate).
- For stricter separation, a separate index or namespace per tenant.

## Honest caveats

- Two made-up customers, 18 documents, questions I wrote: a demo, not a benchmark.
  Keyword search stands in for embeddings; the filtering logic is the same.
- The leak rates here come from how similar the two customers' documents are. Real corpora
  differ, but one leaked answer is enough to matter.
