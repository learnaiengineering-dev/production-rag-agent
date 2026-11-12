"""Day 12 run: how well does an automated checker agree with your human labels?

Reuses the pump-parts world from Day 8 and 11. Twelve open-ended questions,
each with a short reference answer and a human pass/fail label (the ground
truth we wrote). We run two automated checkers and measure how often each one
agrees with the human labels.

Deterministic, pure Python. No language model is called.
"""
from judges import load_items, exact_match, stand_in_judge, agreement

items = load_items("items.csv")
humans = [r["human"] for r in items]

em = [exact_match(r["answer"], r["reference"]) for r in items]
sj = [stand_in_judge(r["answer"], r["reference"]) for r in items]

def mark(b): return "pass" if b else "fail"

print("Day 12 - LLM-as-judge: measuring a judge against your labels")
print("=" * 64)
print("System under test: 12 open-ended answers, pump-parts help desk.")
print("Human = the label we wrote by hand (ground truth).")
print("Exact = strict string match. Stand-in = term-overlap rule (NOT an LLM).")
print()
print(f"{'id':<4}{'human':<7}{'exact':<7}{'stand-in':<9}note")
print("-" * 64)
for r, e, s in zip(items, em, sj):
    flag = []
    if e != (r["human"] == "pass"):
        flag.append("exact " + ("false-pass" if e else "false-fail"))
    if s != (r["human"] == "pass"):
        flag.append("stand-in " + ("false-pass" if s else "false-fail"))
    print(f"{r['id']:<4}{r['human']:<7}{mark(e):<7}{mark(s):<9}{'; '.join(flag)}")

print()
a_em = agreement(em, humans)
a_sj = agreement(sj, humans)
print("Agreement with the human labels (12 items):")
print(f"  exact match : {a_em['correct']}/{a_em['n']} = {a_em['acc']*100:.0f}%  "
      f"(false pass {a_em['false_pass']}, false fail {a_em['false_fail']})")
print(f"  stand-in    : {a_sj['correct']}/{a_sj['n']} = {a_sj['acc']*100:.0f}%  "
      f"(false pass {a_sj['false_pass']}, false fail {a_sj['false_fail']})")
print()
print("Reading it:")
print("- Exact match fails most correct paraphrases: high false-fail.")
print("- The stand-in judge agrees more, but still lets wrong answers pass")
print("  (false-pass) when they happen to contain the right words.")
print("- Whatever the judge, the only number that matters first is its")
print("  agreement with YOUR labels. A judge you have not measured is a guess.")
