# 03-streaming: show the answer as it arrives, then check it finished

A local mock API that writes like a model: first word after 0.4 s, then one word every 0.1 s, for a 59-word answer. No API key needed.

```bash
pip install anthropic
python 03-streaming/mock_server.py          # terminal 1
python 03-streaming/before.py               # waits for the whole answer
python 03-streaming/after.py                # streams it, then checks the ending
python 03-streaming/timeline.py             # when each word arrived, both ways
```

To see what happens when the connection drops halfway, stop the server and restart it in break mode:

```bash
python 03-streaming/mock_server.py break    # terminal 1: closes the connection after word 29
python 03-streaming/naive_stream.py         # a plain loop: ends quietly
python 03-streaming/after.py                # checks the ending: tells the user
```

## What we measured (5 Nov 2026, anthropic 2.4.0, Python 3.13.18, 5 runs each)

| Case | Result |
|---|---|
| `before.py` (wait for the whole answer) | first words on screen after 6.2 s |
| `after.py` (stream it) | first words 0.4 s, all 59 words 6.3 s |
| `naive_stream.py`, connection drops | `done: 29 words, no error raised` |
| `after.py`, connection drops | `Answer interrupted at 29 words. Retry?` |

All five runs of each case gave the same result. The raw output is in `output.txt`. Streaming does not make the answer finish sooner; it changes what the user sees while waiting.

## What this does not show

A mock that writes at a fixed pace, one machine, one version of the library, one 59-word answer. A real model varies in time to first word and in speed. The mock closes the connection cleanly; real network failures can look different, and some raise an error that your code should also handle.
