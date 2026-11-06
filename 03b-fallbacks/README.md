# 03b-fallbacks: a plan B for when the model is down

A local mock API with two pretend models. The main one (`claude-sonnet-5-5`) can be "down": it answers 529 overloaded after 0.3 s. The backup (`claude-haiku-5-5`) answers after 0.5 s. No API key needed.

```bash
pip install anthropic
python 03b-fallbacks/mock_server.py            # terminal 1: main model down
python 03b-fallbacks/run.py                    # terminal 2: 20 users, four ways to build it, 5 runs each
```

To see the other cases, stop the server and restart it:

```bash
python 03b-fallbacks/mock_server.py all-down   # both models down
python 03b-fallbacks/mock_server.py ok         # both models working
```

`fallback.py` is the pattern: one try on the main model, then one on the backup, then a plain message. It falls back only for outages (timeout, dropped connection, 429, 5xx), not for a 400 or 401.

## What we measured (6 Nov 2026, anthropic 2.4.0, Python 3.13.18, 20 users, 5 runs each)

| Case | Main model down | Both down | Healthy |
|---|---|---|---|
| Default settings, no backup (`none`) | 0 of 20 answered, error after about 2.2 s | 20 errors, about 2.2 s | 20 of 20, about 0.5 s |
| Retry first, then backup (`after_retries`) | 20 of 20, about 2.8 s | 20 errors, about 2.5 s | 20 of 20, about 0.5 s |
| Backup straight away (`first`) | 20 of 20, about 0.9 s | 20 errors, about 0.7 s | 20 of 20, about 0.5 s |
| Backup, then a plain message (`last_resort`, `fallback.py`) | 20 of 20, about 0.9 s | 20 plain messages, about 0.7 s | 20 of 20, about 0.5 s |

The counts were identical in all five runs of each case. The waits varied by about 0.1 s. The raw output is in `output.txt`.

## What this does not show

A mock with fixed delays, two pretend models, one machine, one version of the library, 20 users at once. A real outage can be slow instead of a quick 529, and it can hit the backup too. We did not measure answer quality; a backup model may write differently, cost differently, or be less capable.
