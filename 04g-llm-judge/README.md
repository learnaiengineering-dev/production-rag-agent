# 04g - LLM-as-judge: measure it against your labels

Day 12 of the series. This is a tiny, runnable demo about **one habit**: before
you trust any judge of open-ended answers, measure how often it agrees with your
own human labels. It reuses the made-up pump-parts world from Day 8 and Day 11.

## What it shows

Twelve open-ended questions. Each has a short reference answer and a **human
pass/fail label we wrote by hand** (the ground truth). We run two automated
checkers and measure each one's agreement with those human labels:

| Checker | Agreement with humans | Where it went wrong |
|---|---|---|
| Exact string match | 6/12 (50%) | 6 false-fails (rejected correct paraphrases) |
| Stand-in judge (term overlap) | 11/12 (92%) | 1 false-pass (let a hedged, unreliable answer through) |

Raw output: `output.txt`. Run once on 2026-11-11, deterministic.

Exact match is too strict for open-ended answers, so people reach for a smarter
judge. The stand-in here does better, but it still passes a wrong answer when the
words line up. The point is not the 92% - it is that you only know those numbers
*because you measured the judge against labels you wrote*.

## Run it yourself

```
python3 run.py
```

No installs, no internet, no API key. Python 3.9+.

Then put your own rows in `items.template.csv` (id, question, answer, reference,
human) and point `run.py` at it.

## The honest caveats

- **The "stand-in judge" is not a language model.** It is a transparent
  term-overlap rule, here only to show the *agreement measurement* - the step you
  must do with any judge, including a real LLM one. We did not call a hosted model
  (the campaign runs on a $0 budget).
- **92% is not how good a judge is.** It is this rule's agreement on 12 easy,
  factual, hand-written items. On genuinely open-ended answers - explanations,
  essays, code review - counting shared words falls apart. That is *why* teams use
  an LLM judge, and why you then have to measure the LLM judge against labels too.
- Twelve items is a demo, not a benchmark. Twelve labels cannot certify a judge.
- The questions and labels were written before running and not changed.

## What a real LLM judge can and can't tell you (from the research)

A strong LLM used as a judge can approximate human preference surprisingly well.
In the paper that defined the field (Zheng et al., *Judging LLM-as-a-Judge with
MT-Bench and Chatbot Arena*, NeurIPS 2023), GPT-4 agreed with human experts at
**over 80%** - about the same rate two humans agree with each other (roughly 85%
vs 81% in one setup). That is the "can".

The same paper names what it **can't** be trusted to do out of the box:

- **Position bias** - it can prefer whichever answer is shown first. Fix: run it
  twice with the order swapped and only keep verdicts that survive the swap.
- **Verbosity bias** - it can prefer the longer answer even when length adds
  nothing. Watch answer length; don't let it stand in for quality.
- **Self-enhancement bias** - it can favour answers in a style like its own. Fix:
  hide which model wrote each answer; consider a different model as the judge.

So the rule for Day 12: a judge's score means nothing until you know how often it
agrees with your labels, and even a strong judge needs its order swapped, its
lengths watched, and its verdicts spot-checked.

Source: Zheng et al., 2023, arXiv:2306.05685 (NeurIPS 2023 Datasets & Benchmarks).
