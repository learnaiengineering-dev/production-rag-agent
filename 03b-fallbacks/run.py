"""What do 20 users get when the main model is down? Four ways to build it.

  python mock_server.py             # terminal 1 (main model down)
  python run.py                     # terminal 2
  python mock_server.py all-down    # then run again: both models down

  none           the SDK's default retries, no fallback
  after_retries  default retries on the main model, then the backup model
  first          one try on the main model, then the backup model right away
  last_resort    like "first", plus a plain message if the backup is down too (fallback.py)
"""
import asyncio, statistics, sys, time
import anthropic
from anthropic import AsyncAnthropic
import fallback
from fallback import MAIN, BACKUP, is_outage

USERS, RUNS = 20, 5
client = AsyncAnthropic(base_url="http://127.0.0.1:8787", api_key="demo")   # default max_retries=2
ASK = dict(max_tokens=100, messages=[{"role": "user", "content": "How do returns work?"}])


async def one_user(policy):
    start = time.monotonic()
    try:
        if policy == "last_resort":
            who, _ = await fallback.answer(client, **ASK)
        elif policy == "none":
            await client.messages.create(model=MAIN, **ASK)
            who = "main"
        else:
            main = client if policy == "after_retries" else client.with_options(max_retries=0)
            try:
                await main.messages.create(model=MAIN, **ASK)
                who = "main"
            except anthropic.APIError as e:
                if not is_outage(e):
                    raise
                await client.with_options(max_retries=0).messages.create(model=BACKUP, **ASK)
                who = "backup"
    except anthropic.APIError:
        who = "message" if policy == "last_resort" else "error"
    return who, time.monotonic() - start


async def main():
    for policy in ("none", "after_retries", "first", "last_resort"):
        for run in range(1, RUNS + 1):
            results = await asyncio.gather(*[one_user(policy) for _ in range(USERS)])
            who = [w for w, _ in results]
            waits = [t for _, t in results]
            answered = who.count("main") + who.count("backup")
            print(f"{policy} run {run}: {answered} of {USERS} answered "
                  f"(backup {who.count('backup')}, friendly message {who.count('message')}, error {who.count('error')}), "
                  f"typical wait {statistics.median(waits):.1f} s, slowest {max(waits):.1f} s")

asyncio.run(main())
