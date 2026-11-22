"""Day 22 myth test: does a careful prompt make an agent reliable?

A real model (qwen3:8b on Ollama, running locally) gets a clear system prompt with 7 rules
and three simulated refund tools. The tools enforce nothing, so only the prompt decides.
10 customer requests, each run 3 times. Every tool call is logged and checked by code.

    ollama pull qwen3:8b
    python3 run.py                 # about 10-20 minutes on an M2 MacBook Air
    python3 run.py --runs 1        # quicker, one pass

No API key, no internet after the model is downloaded. Python 3.9+, standard library only.
Writes runs.jsonl (every step, with timings) and output.txt (the summary).
"""
import argparse, json, time, urllib.request
from pathlib import Path
from shop import TOOLS, SCHEMAS, SYSTEM
from grade import grade

HERE = Path(__file__).resolve().parent
URL = "http://localhost:11434/api/chat"
MAX_STEPS = 8


def chat(model, messages, think):
    body = {"model": model, "messages": messages, "tools": SCHEMAS, "stream": False, "think": think}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["message"]


def run_once(model, text, think, log):
    t0 = time.time()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]
    calls, steps, final = [], 0, ""
    log({"t": 0.0, "event": "user", "text": text})
    while steps < MAX_STEPS:
        steps += 1
        msg = chat(model, messages, think)
        messages.append(msg)
        tcs = msg.get("tool_calls") or []
        if not tcs:
            final = (msg.get("content") or "").strip()
            log({"t": round(time.time() - t0, 2), "event": "answer", "text": final})
            break
        for tc in tcs:
            name = tc["function"]["name"]
            args = tc["function"].get("arguments") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = {"_raw": args}
            fn = TOOLS.get(name)
            result = fn(**{k: v for k, v in args.items() if k in ("order_id", "amount")}) if fn else {"error": f"no tool {name}"}
            calls.append((name, args))
            log({"t": round(time.time() - t0, 2), "event": "tool_call", "name": name, "args": args, "result": result})
            messages.append({"role": "tool", "tool_name": name, "content": json.dumps(result)})
    else:
        log({"t": round(time.time() - t0, 2), "event": "stopped", "text": f"hit the {MAX_STEPS}-step limit"})
    return calls, final, round(time.time() - t0, 1), steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--think", action="store_true", help="let the model think before answering (slower)")
    a = ap.parse_args()
    reqs = json.loads((HERE / "requests.json").read_text())
    out = open(HERE / "runs.jsonl", "w")
    results = []
    started = time.strftime("%Y-%m-%d %H:%M")
    for req in reqs:
        for k in range(1, a.runs + 1):
            run_id = f"{req['id']}-{k}"

            def log(ev, run_id=run_id):
                out.write(json.dumps({"run": run_id, **ev}) + "\n"); out.flush()
            calls, final, secs, steps = run_once(a.model, req["text"], a.think, log)
            broken = grade(req, calls)
            log({"t": secs, "event": "graded", "broken": [f"{x}: {d}" for x, d in broken]})
            results.append({"req": req["id"], "run": k, "broken": broken, "secs": secs, "steps": steps,
                            "calls": [n for n, _ in calls]})
            print(f"{run_id}: {'clean' if not broken else 'BROKE: ' + '; '.join(f'{x} ({d})' for x, d in broken)}  ({secs}s)", flush=True)
    out.close()

    lines = [f"myth test: does a careful prompt make an agent reliable?",
             f"model {a.model} via Ollama (local) · thinking {'on' if a.think else 'off'} · model's default sampling · run {started}",
             f"{len(reqs)} requests x {a.runs} runs = {len(results)} runs · 7 rules in the system prompt · tools enforce nothing", "=" * 72, ""]
    clean = sum(1 for r in results if not r["broken"])
    lines.append(f"runs with no broken rule: {clean} of {len(results)}")
    rules = {}
    for r in results:
        for b in {x for x, _ in r["broken"]}:
            rules[b] = rules.get(b, 0) + 1
    lines.append("")
    lines.append("broken rules (number of runs):")
    for b, n in sorted(rules.items(), key=lambda x: -x[1]) or [("none", 0)]:
        lines.append(f"  {n:>3}  {b}")
    lines.append("")
    lines.append("per request (same request, same prompt, each run):")
    mixed = 0
    for req in reqs:
        rs = [r for r in results if r["req"] == req["id"]]
        marks = " ".join("ok" if not r["broken"] else "X " for r in rs)
        if len({bool(r["broken"]) for r in rs}) > 1:
            mixed += 1
        lines.append(f"  {req['id']}  {marks:<12} {req['text'][:52]}")
    lines.append("")
    lines.append(f"requests that behaved differently across runs: {mixed} of {len(reqs)}")
    secs = [r["secs"] for r in results]
    lines.append(f"seconds per run: median {sorted(secs)[len(secs)//2]}, max {max(secs)}")
    (HERE / "output.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
