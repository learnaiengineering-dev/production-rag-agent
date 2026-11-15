# 04i - Feedback that tells you why

Day 14 of the series. A tiny, runnable demo of one idea: a thumbs-down tells you
an answer was wrong, not **why**, so you can't fix anything from it. Capture a
reason you can **count** - an enum, plus which part was wrong - and the same
complaints point straight at the thing to fix.

## What it shows

20 answers, each with one piece of user feedback (`events.csv`).

**A thumbs-only system:** 8 of 20 got a thumbs-down (40%). Something is wrong 40%
of the time. What? No idea.

**A reason you can count:**

| count | reason | points at |
|---|---|---|
| 4 | missing_source | retrieval & citations |
| 2 | wrong_fact | the source data (or retrieval) |
| 1 | wrong_format | output parsing / schema |
| 1 | outdated | re-indexing / freshness |

Top reason: **missing_source, 4 of 8 downvotes** - so you look at retrieval and
citations first, not the prompt.

**Why the reason must be an enum, not free text:** the same 8 downvotes, stored as
the free text people actually type ("no source", "where is this from?", "didn't
cite anything"...), are **8 different strings** - nothing to count. As an enum they
collapse to **4 buckets** you can rank.

Raw output: `output.txt`. Deterministic, run once 2026-11-13.

## Run it

```
python3 run.py
```

No installs, no internet, no API key. Python 3.9+. Put your own feedback in
`events.template.csv`.

## The feedback record that works

Log, with every answer, a small record you can aggregate later:

- **rating** - up or down
- **reason** - one of a short, fixed list (the enum). This is the part people skip,
  and it's the part that makes feedback countable.
- **field** - which part was wrong (the citation, a number, the JSON, a date)
- **note** - optional free text, for colour, not for counting
- **trace id** - so a complaint links back to the exact run (that's Day 27)

## Honest caveats

- The feedback here is made up, to show the shape. Twenty events is a demo, not a
  user study - real volumes are larger and messier.
- An enum you pick is a judgement call. Start with four or five reasons, add one
  only when a real pattern needs it, and keep an "other" with a free-text box.
- This is about collecting *why*; acting on it is the rest of the series (retrieval,
  re-indexing, schema, tracing).
