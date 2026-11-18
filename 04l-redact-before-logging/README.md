# 04l - Redact personal data before you log it

Day 17 of the series. Log every prompt "for debugging" and your log files fill up with
emails, phone numbers, card numbers and the odd API key - copied to every place your
logs go. The fix belongs at the point of writing: redact before the line hits the file.

## Run it

```
python3 run.py
```

No installs, no internet, no API key. Python 3.9+.

## What happens (`output.txt`, `logs/`)

12 made-up support messages, 16 personal items labelled by hand, logged three ways:

| Log | What's in it | Personal items still readable |
|---|---|---|
| `logs/raw.log` | the full prompt | 16 of 16 |
| `logs/redacted.log` | the prompt through `RedactFilter` | 5 of 16 |
| `logs/metadata.log` | message id and size, no text | 0 of 16 |

The redaction filter caught every email (4), phone number (4), card number (2) and API
key (1). It missed all 3 names and both street addresses: they have no fixed shape for a
pattern to match. It left the order number, part numbers and a year alone (5 of 5).

## The pieces

- `redact.py` - `redact()` (email, phone, card with a Luhn check, `sk-` keys) and
  `RedactFilter`, a `logging.Filter` you attach to a handler.
- `run.py` - writes the three logs and scores them against the labels.
- `messages.json` - the made-up messages and their labels.

## Using it on a real system

- Attach the filter to the handler, so nothing reaches the file unredacted - including
  third-party libraries that log through the same handler.
- Default to logging metadata (ids, sizes, timings, model, token counts) and keep the
  raw text out. If you need the text, log it somewhere with tighter access and a short
  retention period.
- Names and addresses need more than patterns: a named-entity model, or simply not
  logging free text.
- Logs aren't the only copy: traces, analytics events and error reports carry prompts too.

## Honest caveats

- Every name, number and address is made up; the cards are public test numbers. 12
  messages is a demo, not a benchmark - real text has formats these patterns will miss.
- The phone pattern is written for Australian numbers. Adjust it for yours.
- Redaction lowers risk; it doesn't make a log safe to share. Check what your privacy
  obligations require.
