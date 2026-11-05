# 02b-retries: retries are extra requests

Send 20 requests at once to a local mock API that allows 4 in flight, and retry the 429s four different ways. No API key needed.

The mock server answers each request in 0.5 s and rejects anything over 4 in flight with a 429 and no `retry-after` header, so the client has to choose its own wait. The SDK's own retries are switched off (`max_retries=0`) so the policy is the only thing retrying. Each request may be retried up to 6 times.

```bash
pip install anthropic
python 02b-retries/mock_server.py            # terminal 1
python 02b-retries/run.py fixed 5            # terminal 2: wait 1 s every time, 5 runs
python 02b-retries/run.py backoff 5          # wait 0.5, 1, 2, 4, 8 s (same for every request)
python 02b-retries/run.py jitter 5           # same ceiling, random wait up to it
python 02b-retries/run.py capped 5           # jitter, and at most 4 requests in flight
```

## What we measured (3 Nov 2026, anthropic 2.4.0, Python 3.13.18, 5 runs each)

| Policy | Answered | Requests sent | Rejected (429) | Biggest burst of retries in 100 ms | Time |
|---|---|---|---|---|---|
| fixed 1 s | 20 of 20 | 60 | 40 | 16 | 4.6 s |
| backoff, no jitter | 20 of 20 | 60 | 40 | 16 | 8.1 s |
| backoff + jitter | 20 of 20 | 65 to 67 | 45 to 47 | 7 to 9 | 5.1 to 8.4 s |
| jitter + cap of 4 in flight | 20 of 20 | 20 | 0 | 0 | 2.5 to 2.6 s |

Fixed and backoff gave the same numbers in all 5 runs. Jitter is random, so its numbers change from run to run. The raw output is in `output.txt`.

## What this does not show

One mock server, one version of the library, one machine, 20 requests. A real API limits differently (often per minute, and it may send `retry-after`), so your numbers will differ. The time column mostly reflects the mock server's 0.5 s answers.
