"""The regression gate. Runs the current retrieval over the eval set, compares it
to the committed baseline, and BLOCKS (exits 1) if any question that passed
before now fails. This is what you wire into CI.

    python3 run_gate.py            # current (good) config -> passes
    python3 run_gate.py --regress  # a change that breaks exact ids -> blocks
"""
import json, sys
from evalkit import load_questions, run, compare
from retrieve import load_parts, make_search

# a "change" someone might ship: raise the min token length to 'reduce noise'
CURRENT_CONFIG = {"min_token_len": 3} if "--regress" in sys.argv else {"min_token_len": 1}

baseline = json.load(open("baseline.json"))
qs = load_questions("questions.csv")
before = [{"id": b["id"], "passed": b["passed"]} for b in baseline["results"]]

system = make_search(load_parts(), **CURRENT_CONFIG)
after = [{"id": r["id"], "passed": r["passed"]} for r in run(system, qs)]

fixed, broke, still = compare(before, after)
passed_now = sum(a["passed"] for a in after)

print("retrieval regression gate")
print("=" * 48)
print(f"baseline config : {baseline['config']}")
print(f"current config  : {CURRENT_CONFIG}")
print(f"pass: baseline {sum(b['passed'] for b in before)}/{len(before)}"
      f"  ->  current {passed_now}/{len(after)}")
print(f"fixed: {fixed or '-'}")
print(f"broke: {broke or '-'}")
print()
if broke:
    print(f"BLOCKED: {len(broke)} question(s) passed before and fail now: {', '.join(broke)}")
    print("A change can improve things or leave them the same - it must not break what worked.")
    sys.exit(1)
print("OK: nothing that passed before is failing now. Safe to merge.")
sys.exit(0)
