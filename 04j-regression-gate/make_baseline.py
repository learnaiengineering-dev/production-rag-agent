"""Generate the committed baseline: the pass/fail of each question under the
known-good config. Run once, commit baseline.json, and the gate compares every
future change against it."""
import json
from evalkit import load_questions, run
from retrieve import load_parts, make_search

GOOD_CONFIG = {"min_token_len": 1}  # the config we trust today

parts = load_parts()
qs = load_questions("questions.csv")
system = make_search(parts, **GOOD_CONFIG)
results = run(system, qs)
baseline = {"config": GOOD_CONFIG,
            "results": [{"id": r["id"], "passed": r["passed"]} for r in results]}
json.dump(baseline, open("baseline.json", "w"), indent=1)
passed = sum(r["passed"] for r in results)
print(f"baseline written: {passed}/{len(results)} pass under {GOOD_CONFIG}")
