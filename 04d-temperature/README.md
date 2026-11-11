# 04d-temperature: temperature is not determinism

A toy sampler and a rounding test. No API key, no downloads, no packages.

```bash
python run.py
```

It takes about a second and prints the same result every time (everything is seeded).

## What it does
- **Part 1:** a toy "answer" built from three word choices with invented scores. Temperature divides the scores before one word is drawn. At temperature 0 the top word always wins. We run 20 answers at each of 0, 0.3, 0.7, 1.0 and 1.5 and count the different answers.
- **Part 2:** at temperature 0, the same 2,048 products are added up in 20 different orders using emulated 32-bit floats. Different orders round differently. With a clear lead between two words nothing flips. With a near-tie (a true gap equal to one standard deviation of the rounding noise, set in the code and not tuned) the winner flips sometimes.

## Result (output of the run on 11 Nov 2026)

| Temperature | Different answers in 20 runs | Most common answer |
|---|---|---|
| 0 | 1 | 20 of 20 |
| 0.3 | 9 | 9 of 20 |
| 0.7 | 11 | 3 of 20 |
| 1.0 | 18 | 3 of 20 |
| 1.5 | 15 | 3 of 20 |

Rounding test at temperature 0: the same word-A total came out as 15 different 32-bit values over 20 orders. Clear lead: the top word wins 20 of 20. Near-tie: it wins 16 of 20 and its rival wins 4 of 20.

## Read this before you quote the numbers
- This is a toy, not a language model. The word scores are invented, so none of the counts say how often a real model varies.
- More temperature means more variety, but 20 runs is a small sample (1.5 gave fewer different answers than 1.0). The run was done once with fixed seeds.
- The rounding test shows one cause only. The Thinking Machines Lab write-up ("Defeating Nondeterminism in LLM Inference", Sep 2025) traces most of the variation it measured on one open model to results depending on batch size, which changes with server load.
- We did not call any hosted model.

## Provider statements used in the posts (from their documentation)
- Anthropic SDK reference, temperature: even with a temperature of 0.0, the results will not be fully deterministic.
- OpenAI documentation: a seed gives "mostly" identical outputs, and determinism is not guaranteed.
- Anthropic's Sonnet 5.5 migration guide: temperature, top_p and top_k set to non-default values return an error, so on current Claude models you cannot set temperature to 0 at all.

## Trying it on a real model
The older `06-temperature/same_question.py` draft in this repo was not run for these numbers. Its Anthropic path sets `temperature=0` on `claude-sonnet-5-5`, which the migration guide says returns an error. Its Ollama path (a local model) does not have that problem, but we have not run it.
