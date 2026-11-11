"""Structured output that parses: what does each layer of checking catch?

  python run.py

No API key, no downloads, no packages. The 20 replies in replies.py were WRITTEN BY US to show failure shapes.
This measures our checking code, not a model: it says nothing about how often a real model gets these wrong.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_reply import extract_json, validate, parse_reply, retry_message
from replies import REPLIES


def layer0(text):                      # naive: json.loads on the raw reply, then trust it
    try:
        obj = json.loads(text)
    except Exception:
        return False, False
    return True, not validate(obj)


def layer1(text):                      # extract JSON from the reply, then json.loads (no checking, no repair)
    js, problem = extract_json(text)
    if problem:
        return False, False
    try:
        obj = json.loads(js)
    except Exception:
        return False, False
    return True, not validate(obj)


def main():
    rows = []
    for name, text in REPLIES:
        p0, v0 = layer0(text)
        p1, v1 = layer1(text)
        obj, notes, errs = parse_reply(text)
        rows.append((name, p0, v0, p1, v1, obj is not None, notes, errs))
    n = len(rows)
    print(f"{n} replies we wrote (not from a real model). Pass = a usable dict that matches the schema.\n")
    print("  layer                                          | json.loads works | matches the schema")
    print(f"  1  json.loads on the raw reply                 | {sum(r[1] for r in rows):>2} of {n}          | {sum(r[2] for r in rows):>2} of {n}")
    print(f"  2  + pull the JSON out of the reply            | {sum(r[3] for r in rows):>2} of {n}          | {sum(r[4] for r in rows):>2} of {n}")
    print(f"  3  + schema check and safe repairs             |                  | {sum(r[5] for r in rows):>2} of {n}")
    left = [r for r in rows if not r[5]]
    print(f"  4  the other {len(left)}: send the errors back and ask again (retry)\n")
    print("Reply by reply:  raw = json.loads works / schema ok on the raw reply;  final = usable after layer 3\n")
    print(f"  {'reply':<30} raw parses  raw valid  final  what happened")
    for name, p0, v0, p1, v1, ok, notes, errs in rows:
        what = ("; ".join(notes) if ok and notes else "as it was") if ok else "RETRY: " + "; ".join(errs)
        print(f"  {name:<30} {'yes' if p0 else 'no':<11} {'yes' if v0 else 'no':<10} {'yes' if ok else 'no':<6} {what}")
    print("\nExample retry message for 'category is refund':\n")
    ex = next(r for r in rows if r[0] == "category is refund")
    print(retry_message(ex[7]))
    parsed_not_valid = sum(1 for r in rows if r[1] and not r[2])
    print(f"\nReplies where json.loads worked on the raw text but the schema check failed: {parsed_not_valid} of {n}")


if __name__ == "__main__":
    main()
