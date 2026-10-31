# Ship a production RAG agent

One production problem at a time, each with code you can run. This repo goes with the
Learn AI Engineering video series (YouTube, Instagram, TikTok) and the guides at
[learnaiengineering.dev](https://learnaiengineering.dev).

| Fix | Problem | Folder |
|---|---|---|
| 01 | An LLM call hangs and the user waits forever | [01-timeouts](01-timeouts) |
| 02 | A batch of requests hits 429 even with retries | [02-rate-limits](02-rate-limits) |
| 03 | A blank screen while the answer is written, and streams that end early | [03-streaming](03-streaming) |

## 01 · Timeouts and retries

The official Python libraries wait a long time by default. As of 31 October 2026,
`anthropic` 2.3.0 and `openai` 3.41.0 both set `DEFAULT_TIMEOUT` to 600 seconds and
`DEFAULT_MAX_RETRIES` to 2 (see each package's `_constants.py`). One stuck call can
keep a user waiting for minutes.

`mock_server.py` is a local stand-in for an LLM API, so you can reproduce a hang
without an API key or real outage.

```bash
python -m venv .venv && .venv/bin/pip install anthropic
.venv/bin/python 01-timeouts/mock_server.py hang     # terminal 1
.venv/bin/python 01-timeouts/before.py               # terminal 2: waits (up to 600 s per attempt)
```

```bash
.venv/bin/python 01-timeouts/mock_server.py flaky    # first request hangs, then answers
.venv/bin/python 01-timeouts/after.py                # gives up after 5 s, retries, answers
```

What we saw on our machine (31 October 2026):

- `before.py` against `hang`: printed `timeout: 600 s, retries: 2` and was still waiting when we stopped it at 20 s.
- `after.py` against `flaky`: `5.6 s: Refunds take 5 business days.`
- `after.py` against `hang`: three attempts, then `Sorry, that took too long. Please try again.` after about 16 s.

Pick a timeout that fits how long a normal reply takes for your prompts. A long
generation needs a longer timeout, or streaming.

## 02 · Rate limits

`mock_server.py` allows 4 requests in flight. Over that, it answers `429` with `retry-after: 1`.
The SDK retries a 429 and honours `retry-after` (anthropic 2.3.0, `_base_client.py`), so every
rejected request comes back at the same moment.

```bash
.venv/bin/python 02-rate-limits/mock_server.py      # terminal 1
.venv/bin/python 02-rate-limits/before.py           # 20 requests at once
.venv/bin/python 02-rate-limits/after.py            # same 20, at most 4 in flight
```

What we saw (31 October 2026, two runs each): `before.py` answered 12 and 13 of 20, with the rest
failing with 429 (the server sent 33 rejections in run 1). `after.py` answered 20 of 20 with no 429s.
Both took 2.6 s.

## 03 · Streaming

`mock_server.py` writes a 59-word answer: first word after 0.4 s, then a word every 0.1 s.
`mock_server.py break` drops the connection halfway through a stream.

```bash
.venv/bin/python 03-streaming/mock_server.py        # or: mock_server.py break
.venv/bin/python 03-streaming/before.py             # waits for the whole answer
.venv/bin/python 03-streaming/after.py              # streams, then checks it finished
.venv/bin/python 03-streaming/naive_stream.py       # streams without the check
```

What we saw (31 October 2026, two runs each): `before.py` showed its first words after 6.2–6.3 s.
`after.py` showed first words after 0.4 s and all 59 after 6.5 s. With `break`, `naive_stream.py`
ended with 29 words and **no error raised**, while `after.py` noticed the missing `stop_reason` and
printed `Answer interrupted at 29 words. Retry?`. That's one result with one SDK version; check it
against your own stack.
