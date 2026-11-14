# 04h - Unit-testing code that calls an LLM

Day 13 of the series. A runnable demo of one idea: **don't unit-test the model -
test your code around it.** The model is slow, costs money and gives a different
answer each time, so you can't assert on it. But the code around the call - the
prompt you build, the reply you parse, the retry when it comes back wrong - is
plain Python, and plain Python is easy to test.

## What's here

A tiny "find the part number" helper (`llmbot.py`) that calls an LLM through an
**injected boundary**: the model is a function passed in, not imported. So a test
hands it a fake, and no network call ever happens.

```
def extract_part(message, llm, max_tries=2):   # llm is passed in
    ...
```

`test_llmbot.py` tests the four deterministic things around the call:

| What | Tested with |
|---|---|
| Building the prompt | a plain string check |
| Parsing the reply (good, messy, junk, missing field) | a fake reply |
| Retrying a bad reply, then succeeding | a scripted fake that fails once |
| Giving up cleanly after N tries | a scripted fake that always fails |

## Run it

```
python -m unittest -v        # 9 tests, no installs, no API key
```

(`pytest` discovers the same tests if you prefer it.)

Result kept in `output.txt`: **9 passed**, 0.00s, zero network calls.

## The bug the suite catches

`llmbot_buggy.py` is the same helper with one real bug: `extract_part` forgets to
retry - it calls the model once and returns whatever comes back. Run the two retry
tests against it:

```
python -m unittest -v test_bug_demo
```

Result kept in `output-with-bug.txt`: **2 tests go red** (one failure, one error).
That is the whole point - the fake model let the test force a bad first reply, so
the missing retry showed up on your laptop in milliseconds instead of in production.

## Plugging in a real model

Your real call wraps a client to match the boundary - one function, prompt in,
text out:

```
def real_llm(prompt):
    return my_client.responses.create(prompt).text   # the only place the network lives
answer = extract_part(message, real_llm)
```

Tests keep passing the fake; only this one adapter ever talks to the network, and
you cover it with a couple of mock tests, not with your whole suite.

## Honest caveats

- The "model" in the tests is faked on purpose. That is correct practice, not a
  shortcut: a unit test should never call a real model.
- This is unit testing, not evals. Whether the model's answers are any *good* is a
  separate job - that's the eval set (Day 11) and LLM-as-judge (Day 12).
- The helper is a small teaching example, not a library.
