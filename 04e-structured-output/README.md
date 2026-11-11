# 04e-structured-output: it parses, but is it valid?

A reusable checker (`parse_reply.py`) and 20 bad replies. No API key, no downloads, no packages.

```bash
python run.py
```

It takes about a second and prints the same result every time.

## What it does
`parse_reply.py` does three jobs on a model's reply, then tells you what to do next:
1. **Find it:** strip code fences and chatter, find the first balanced JSON value, notice a cut-off or more than one value.
2. **Parse it:** `json.loads`, with a trailing comma removed.
3. **Check it:** `validate()` against a small schema (category enum, priority 1 to 4, needs_human boolean, summary up to 140 characters) and return a readable list of errors. `retry_message(errors)` turns them into text you can send back to the model.

To use it, replace `SCHEMA` with your own. The repairs in `fix()` (lower-case, text number to integer, drop unknown field) are policy choices: delete any you don't want.

## Result (output of the run on 11 Nov 2026)

| Layer | json.loads works | Matches the schema (of 20) |
|---|---|---|
| json.loads on the raw reply | 11 | 1 |
| + pull the JSON out of the reply | 14 | 4 |
| + schema check and safe repairs | | 8 usable |

The other 12 are listed with the reason they need a retry. 10 of the 11 that parsed raw broke a schema rule.

## Read this before you quote the numbers
- The 20 replies in `replies.py` were **written by us** to show failure shapes. They are not from a real model, so these counts test the checker and say nothing about how often any model returns bad JSON.
- The schema is small and invented, and everything ran once.
- The checker validates a small subset of JSON Schema (type, enum, range, length, required, extra fields). For anything bigger, use a schema library.
- We did not call any hosted model or test any provider's structured-output feature.

## Provider statements used in the posts (from their documentation)
- Anthropic: structured outputs constrain a reply to a JSON schema, and the output may not match the schema when a response ends in a refusal or hits max_tokens.
- OpenAI: Structured Outputs ensure schema adherence, JSON mode ensures only valid JSON, and refusals can be detected in code.
- Features and limits change, so check the current documentation for your model.
