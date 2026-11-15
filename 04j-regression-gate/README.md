# 04j - A regression gate for retrieval

Day 15 of the series. Day 11 gave you an eval set. This wires it into CI so a
change can't **quietly** make retrieval worse. The rule: a change may improve
things or leave them the same - it must not break what worked.

## What it does

A keyword retrieval runs over the pump-parts corpus (reused from Day 8 and 11)
against 12 questions. `baseline.json` is the committed pass/fail under the config
we trust today. The gate runs the current code, compares it to the baseline, and
**exits non-zero if any question that passed before now fails** - which turns a CI
check red and blocks the merge.

## Run it

```
python3 run_gate.py            # current (good) config  -> exit 0, "safe to merge"
python3 run_gate.py --regress  # a change that breaks exact ids -> exit 1, "BLOCKED"
```

No installs, no internet, no API key. Python 3.9+.

## The two runs (kept here)

| Run | Pass | Gate | Exit |
|---|---|---|---|
| Good change (`output-pass.txt`) | 12/12 | OK, safe to merge | 0 |
| Regression (`output-block.txt`) | 10/12 | BLOCKED: g01, g10 broke | 1 |

The regression is a realistic one: raising the minimum token length to "reduce
noise" drops the short suffix that tells the twin parts apart, so `XR-4471-D`
and `XR-4417-D` start resolving to their `-B` twins. A human reviewer would
likely wave that change through. The gate catches it.

## Wiring it into CI

`.github/workflows/retrieval-gate.yml` runs `run_gate.py` on every pull request.
A non-zero exit fails the check, and a branch protection rule turns that into a
blocked merge.

## Honest caveats

- Toy corpus and a hand-written question set, reused from earlier days - a demo,
  not a benchmark. Real gates run on a larger set.
- The gate's rule here is the strict one ("nothing that passed may fail"). Some
  teams allow a small, reviewed budget of regressions; that's a policy choice.
- A gate is only as good as its eval set. It protects the questions you wrote,
  nothing more - keep adding the failures you find (Day 14).
