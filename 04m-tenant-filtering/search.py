"""A small keyword search over documents that belong to different customers (tenants).

Three ways to search, so run.py can compare them:
  search_unfiltered()  - no tenant filter at all
  search_post_filter() - take the top k, THEN drop other tenants' documents
  search()             - filter inside the query: only this tenant's and shared
                         documents are ever scored. tenant is required.
No model, no installs."""
import json, re

STOP = set(("a an and the of for to on in is it we do our what when where who how can are be your "
             "at or if but not any its").split())


def load(path="docs.jsonl"):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def terms(text):
    return {t for t in re.findall(r"[a-z0-9][a-z0-9\-%]*", text.lower()) if t not in STOP}


def _rank(docs, question, k):
    q = terms(question)
    scored = sorted(docs, key=lambda d: (-len(q & terms(d["text"])), d["id"]))
    return [d for d in scored if q & terms(d["text"])][:k]


def visible(doc, tenant):
    return doc["tenant"] in (tenant, "shared")


def search_unfiltered(docs, question, k=3):
    return _rank(docs, question, k)


def search_post_filter(docs, question, tenant, k=3):
    return [d for d in _rank(docs, question, k) if visible(d, tenant)]


def search(docs, question, *, tenant, k=3):
    """The safe one: tenant is keyword-only and has no default, so forgetting it is an error."""
    if not tenant:
        raise ValueError("tenant is required")
    return _rank([d for d in docs if visible(d, tenant)], question, k)
