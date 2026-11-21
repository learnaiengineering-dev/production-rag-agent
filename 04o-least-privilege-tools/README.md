# 04o · Least-privilege tools for agents

Four agents share one toolbox of 8 tools. `calls.jsonl` holds the 17 tool calls they ask for: 8 that their job needs and 9 that something they read told them to make (a supplier page, a support ticket, a CSV cell, a customer's message).

No model is called. The calls are fixed, so the only thing that changes between runs is the policy, which is checked at the tool layer before anything executes. Every tool is simulated: nothing is read, written, sent, refunded or queried, and every address is a reserved `.example` domain.

```bash
python3 run.py                       # writes the table below
python3 -m unittest -v test_policy   # 5 tests
```
No installs, no internet, no API key. Python 3.9+.

## Results (run 20 Nov 2026, `output.txt`)

| Policy | Job calls done | Injected calls that ran | Held for a person | Refused |
|---|---|---|---|---|
| Shared toolbox (every agent, every tool) | 8 of 8 | 9 of 9 | 0 | 0 |
| Tool allowlist per agent | 8 of 8 | 5 of 9 | 0 | 4 |
| Allowlist + scoped arguments | 8 of 8 | 0 of 9 | 1 | 8 |

The allowlist cut the tools exposed from 32 to 7, but 5 injected calls used a tool the agent was allowed to have, with the wrong argument: an email to someone other than the ticket's customer, a `../` path out of the reports folder, a write outside `reports/out/`, a $900 refund and an `UPDATE` query. Scoping the arguments stopped all 5.

## The scopes (`policy.py`)
- `send_email`: only to the customer on the ticket being answered.
- `read_file` / `write_file`: only inside `reports/` / `reports/out/`, after resolving `../`.
- `run_sql`: `SELECT` only. In production use a read-only database role; this check stands in for it.
- `create_refund`: up to $50 runs; anything above waits for a person.

## What this is and isn't
A demo, not a benchmark. The 17 calls and the agents are made up, and a real model would ask for different things. The point is where the check lives: in code around the tool, so it holds whatever the model asks for. Enforce the same limits in the systems behind the tools too (database roles, scoped API tokens), and don't rely on this layer alone.

Guidance: OWASP LLM06:2025 Excessive Agency (https://genai.owasp.org/llmrisk/llm062025-excessive-agency/): minimise extensions, their functionality and their permissions, avoid open-ended tools, require user approval for high-impact actions, and enforce authorisation in downstream systems.
