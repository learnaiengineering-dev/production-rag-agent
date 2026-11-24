"""Day 23: build the agent loop (agent.py, 26 lines) and test it on the Day 22 refund shop.

The same loop and the same 10 requests as 04q. Two system prompts, each run 3 times per request:
  A  the 7 rules from Day 22
  B  the same 7 rules plus one line: "Nothing happens until you call a tool..."
Runs alternate A, B, A, B so a slow patch hits both the same.

    ollama pull qwen3:8b          # if you don't have it yet
    python3 run.py                # 60 runs, roughly 10-20 minutes on an M2 MacBook Air
    python3 run.py --runs 1       # quicker
    python3 report.py             # re-scores the saved runs: did it do the job?

No API key, no installs beyond Ollama. Python 3.9+, standard library only. Nothing real is refunded.
Writes runs.jsonl (every step) and output.txt (the rules summary).
"""
import argparse, json, time
from pathlib import Path
from agent import run_agent
from shop import TOOLS, SCHEMAS, SYSTEM, SYSTEM_8
from grade import grade

HERE = Path(__file__).resolve().parent
PROMPTS = {"A": SYSTEM, "B": SYSTEM_8}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--runs", type=int, default=3)
    a = ap.parse_args()
    reqs = json.loads((HERE / "requests.json").read_text())
    out = open(HERE / "runs.jsonl", "w")
    results, started = [], time.strftime("%Y-%m-%d %H:%M")
    for req in reqs:
        for k in range(1, a.runs + 1):
            for v, system in PROMPTS.items():
                run_id, t0 = f"{v}-{req['id']}-{k}", time.time()

                def log(ev, run_id=run_id, t0=t0):
                    out.write(json.dumps({"run": run_id, "t": round(time.time() - t0, 2), **ev}) + "\n"); out.flush()
                log({"event": "user", "text": req["text"]})
                final, calls, steps = run_agent(a.model, system, req["text"], TOOLS, SCHEMAS,
                                                log=lambda n, args, res, log=log: log({"event": "tool_call", "name": n, "args": args, "result": res}))
                log({"event": "answer" if final is not None else "stopped", "text": final or "hit the 8-step limit"})
                broken = grade(req, calls)
                log({"event": "graded", "broken": [f"{x}: {d}" for x, d in broken]})
                secs = round(time.time() - t0, 1)
                results.append({"v": v, "req": req["id"], "broken": broken, "secs": secs, "steps": steps, "stopped": final is None})
                print(f"{run_id}: {'clean' if not broken else 'BROKE: ' + '; '.join(f'{x} ({d})' for x, d in broken)}  ({secs}s)", flush=True)
    out.close()

    lines = ["04r: the agent loop on the Day 22 refund shop",
             f"model {a.model} via Ollama (local) · thinking off · model's default sampling · run {started}",
             f"{len(reqs)} requests x {a.runs} runs x 2 prompts = {len(results)} runs · tools enforce nothing", "=" * 72, ""]
    for v, label in (("A", "A: the 7 rules from Day 22"), ("B", "B: the 7 rules + 'nothing happens until you call a tool'")):
        rs = [r for r in results if r["v"] == v]
        lines.append(f"{label}")
        lines.append(f"  runs with no broken rule: {sum(1 for r in rs if not r['broken'])} of {len(rs)}")
        lines.append(f"  runs that hit the step limit: {sum(r['stopped'] for r in rs)}")
        secs = sorted(r["secs"] for r in rs)
        lines.append(f"  seconds per run: median {secs[len(secs)//2]}, max {secs[-1]}")
        broken = {}
        for r in rs:
            for b in {x for x, _ in r["broken"]}:
                broken[b] = broken.get(b, 0) + 1
        for b, n in sorted(broken.items(), key=lambda x: -x[1]):
            lines.append(f"  {n:>3}  {b}")
        lines.append("")
    (HERE / "output.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
