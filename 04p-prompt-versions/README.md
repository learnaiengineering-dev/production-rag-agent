# 04p · Version prompts like code

A support prompt gets a "tidy up the wording" edit. The new version reads better, and it quietly drops the line that says *if the docs don't cover it, say "I don't know"*. This folder shows four habits that catch that before customers do:

1. **One file per version.** `prompts/support-answer/v1.txt`, `v2.txt`. Changes are reviewed as a diff.
2. **An eval gate.** The new version runs on the same 12 questions as the live one. If it scores lower, it doesn't go live.
3. **Version and hash in every log line.** When an answer looks wrong, you know which prompt wrote it.
4. **Released versions are locked by hash** (`prompts.lock.json`). Editing a live version in place is refused: make a new version instead. Rollback is one line: `"live": "v1"`.

```bash
python3 run.py                        # writes output.txt and logs/answers.jsonl
python3 -m unittest -v test_prompts   # 5 tests
```
No installs, no internet, no API key. Python 3.9+.

## Results (run 21 Nov 2026, `output.txt`)

| Version | Hash | All 12 | 8 the docs cover | 4 they don't |
|---|---|---|---|---|
| v1 (live) | 54af406f | 12 | 8 | 4 (said "I don't know") |
| v2 (tidied) | b65c7cb5 | 8 | 8 | 0 (guessed from the nearest doc) |

The gate blocked v2, and v1 stayed live. An in-place edit to v1 was refused with `hash ba904eaf, locked 54af406f`.

## What this is and isn't
The model is a rule-based stand-in (`answerer.py`): it follows the instructions that are in the prompt and nothing else, so dropping a line changes its behaviour every time. A real model is less predictable, which makes the eval gate more important, not less. The 6 help docs and 12 questions are made up, and 12 questions is a tiny eval set: use your own, and more of them.

The same habits work with any prompt store or tool: the point is that a prompt change is a code change, so it gets a diff, a test and a version.
