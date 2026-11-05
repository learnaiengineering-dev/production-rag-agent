"""Send 20 requests at once, and retry 429s with one of three policies.

    python 02b-retries/run.py fixed     # wait 1 s every time
    python 02b-retries/run.py backoff   # wait 0.5, 1, 2, 4, 8 s: doubling, same for everyone
    python 02b-retries/run.py jitter    # same ceiling, but each client picks a random wait up to it
    python 02b-retries/run.py capped    # jitter, plus at most 4 requests in flight (Day 2's fix)

The SDK's own retries are switched off (max_retries=0) so the policy is the only thing retrying.
"""
import asyncio, contextlib, json, os, random, sys, time
from anthropic import AsyncAnthropic, RateLimitError

POLICIES = {
    "fixed":   lambda n: 1.0,
    "backoff": lambda n: min(8.0, 0.5 * 2 ** n),
    "jitter":  lambda n: random.uniform(0, min(8.0, 0.5 * 2 ** n)),
}
POLICIES["capped"] = POLICIES["jitter"]
REQUESTS, MAX_RETRIES = 20, 6
POLICY = sys.argv[1]
limit = None
client = AsyncAnthropic(base_url="http://127.0.0.1:8787", api_key="demo", max_retries=0)


async def ask(i, wait, counts, t0):
    async with (limit if POLICY == "capped" else contextlib.nullcontext()):
        return await ask_with_retries(i, wait, counts, t0)


async def ask_with_retries(i, wait, counts, t0):
    for attempt in range(MAX_RETRIES + 1):
        counts["sent"] += 1
        counts["all_times"].append((round(time.monotonic() - t0, 3), attempt))
        if attempt > 0:
            counts["retry_times"].append(time.monotonic() - t0)
        try:
            await client.messages.create(model="claude-sonnet-5-5", max_tokens=50,
                                         messages=[{"role": "user", "content": f"Summarise ticket {i}"}])
            return True
        except RateLimitError:
            counts["429"] += 1
            if attempt < MAX_RETRIES:
                await asyncio.sleep(wait(attempt))
    return False


async def one_run(policy):
    counts = {"sent": 0, "429": 0, "retry_times": [], "all_times": []}
    start = time.monotonic()
    results = await asyncio.gather(*(ask(i, POLICIES[policy], counts, start) for i in range(REQUESTS)))
    return sum(results), counts, time.monotonic() - start


def biggest_burst(times, window=0.1):
    """The most retries sent inside any 100 ms window."""
    times = sorted(times)
    return max((sum(1 for u in times if t <= u < t + window) for t in times), default=0)


async def main():
    global limit
    limit = asyncio.Semaphore(4)
    policy = POLICY
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    for r in range(1, runs + 1):
        ok, c, secs = await one_run(policy)
        if os.environ.get("TIMES_JSON") and r == 1:   # optional: save when every request was sent (for charts)
            json.dump({"policy": policy, "answered": ok, "sent": sorted(c["all_times"]), "seconds": round(secs, 2)}, open(os.environ["TIMES_JSON"], "w"))
        print(f"{policy} run {r}: {ok} of {REQUESTS} answered, {c['sent']} requests sent, {c['429']} rejected with 429, "
              f"biggest burst of retries {biggest_burst(c['retry_times'])} in 100 ms, {secs:.1f} s")

asyncio.run(main())
