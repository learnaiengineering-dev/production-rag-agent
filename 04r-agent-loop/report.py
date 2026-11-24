"""Re-score the saved runs (runs.jsonl) on the question run.py doesn't ask: did the agent do the job?

For each prompt (A = 7 rules, B = 7 rules + one line about tools), count:
  - runs where a refund was allowed, and runs where it issued one
  - "said but didn't": the reply tells the customer a refund is happening or done, but issue_refund was never called
Nothing is re-run.

    python3 report.py          # prints and writes report.txt
"""
import json, re
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
reqs = {r["id"]: r for r in json.loads((HERE / "requests.json").read_text())}
runs = OrderedDict()
for line in (HERE / "runs.jsonl").read_text().splitlines():
    e = json.loads(line)
    runs.setdefault(e["run"], []).append(e)

# a reply that tells the customer money is moving: "we will process a refund of $80", "please wait while we issue"
PROMISE = re.compile(r"\b(we will|we'll|will be|we can|i will|i'll|let me|please wait)\b[^.]*\b(process|issu|refund)", re.I)
# replies that hand the refund to a manager are not promises
ESCALATE = re.compile(r"(?<!no )(requires|needs?|need to have) (a )?manager|(?<!no )manager('s)? (approval|review|will|must)|contact a manager", re.I)

stats = {v: {"runs": 0, "allowed": 0, "issued": 0, "issued_when_allowed": 0, "said": []} for v in "AB"}
for rid, evs in runs.items():
    v, req_id, _ = rid.split("-")
    req = reqs[req_id]
    refunded = any(e["event"] == "tool_call" and e["name"] == "issue_refund" for e in evs)
    answer = next((e["text"] for e in evs if e["event"] == "answer"), "")
    allowed = bool(req["allowed_refunds"])
    s = stats[v]
    s["runs"] += 1; s["allowed"] += allowed; s["issued"] += refunded; s["issued_when_allowed"] += refunded and allowed
    said = (bool(PROMISE.search(answer)) and "$" in answer and not refunded
            and not ESCALATE.search(answer) and not answer.rstrip().endswith("?"))
    if said:
        s["said"].append((rid, answer))

lines = ["did it do the job? (same saved runs, nothing re-run)", "=" * 60]
for v, label in (("A", "A: the 7 rules from Day 22"), ("B", "B: the 7 rules + 'nothing happens until you call a tool'")):
    s = stats[v]
    lines += [label,
              f"  runs where a refund was allowed: {s['allowed']} of {s['runs']}",
              f"  runs where it issued a refund: {s['issued']} of {s['runs']} ({s['issued_when_allowed']} of them where one was allowed)",
              f"  runs where it said a refund was happening but never issued one: {len(s['said'])}"]
    for rid, ans in s["said"]:
        lines.append(f"    {rid}: \"{ans[:150]}\"")
    lines.append("")
lines += ["note: R05 (refund $50 of a $120 order) counts as 'allowed' here, as in 04q, but the demo's policy tool",
          "flags any order over $100 for a manager, so sending it to a manager is also a correct reading."]
(HERE / "report.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
