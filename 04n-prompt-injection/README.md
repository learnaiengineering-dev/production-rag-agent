# 04n - Prompt injection: when a web page tells your agent what to do

Day 19 of the series. Give an agent a browsing tool and an email tool, ask it to summarise
some supplier pages, and one of those pages can carry an instruction of its own - in an HTML
comment, in white 1-pixel text, in an image's alt text, or in a plain polite sentence. A
person reading the page never sees most of it. The model reads all of it.

OWASP lists this as LLM01:2025 Prompt Injection, including *indirect* injection from
external content such as websites and files, and notes that injected text doesn't have
to be visible to a person.

## Run it

```
python3 run.py
```

No installs, no internet, no API key. Python 3.9+. Nothing is emailed or deleted: the
tools are simulated, every address is `.example`, and the pages are local files.

## The agent is a stand-in, on purpose

`agent.py` is not a model. It obeys every instruction it reads - the worst case. Real
models sometimes refuse and sometimes don't, and OWASP notes that techniques like RAG and
fine-tuning don't fully prevent it. So the demo tests protections that hold whatever the
model does.

## What happens (`output.txt`)

8 supplier pages, 4 with a hidden instruction. Task: summarise the seal kit prices.

| Setup | Risky actions that ran | Held for a person | Pages summarised |
|---|---|---|---|
| No protection | 4 (3 emails out, 1 file deleted) | 0 | 8 of 8 |
| Keyword filter (known injection phrases) | 3 | 0 | 7 of 8 |
| Approval gate on risky tools | 0 | 4 | 8 of 8 |
| Least privilege (summariser gets read-only tools) | 0 | 0 (4 refused: no such tool) | 8 of 8 |

The keyword filter caught only the page that said "ignore previous instructions". It
missed the white text, the alt text and the polite sentence, and it threw away the one
page it did catch, price and all.

## Using it on a real system

- Give each agent only the tools its job needs. A summariser doesn't need to send email.
- Put risky actions - anything that sends data out, changes or deletes, spends money -
  behind a person's approval, especially once the agent has read outside content.
- Allowlist where data can go (domains, recipients, hosts).
- Mark fetched content as data, not instructions, in the prompt. It helps; it isn't a wall.
- Treat phrase filters and detectors as a backstop, not the defence.

These match OWASP's mitigations for LLM01: least privilege, human approval for high-risk
actions, and segregating external content.

## Honest caveats

- The agent is a rule-based stand-in, not a model: it shows what *can* happen, not how
  often a real model falls for it.
- 8 pages I wrote, 4 injection styles: a demo, not a benchmark.
- An approval gate is only as good as the person approving it. Show them exactly what
  will be sent where.

Source: OWASP Gen AI Security Project, LLM01:2025 Prompt Injection -
https://genai.owasp.org/llmrisk/llm01-prompt-injection/
