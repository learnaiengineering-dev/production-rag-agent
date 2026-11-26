"""The whole agent. A loop: ask the model, run the tools it asks for, show it the results, repeat."""
import json, urllib.request

def ask(model, messages, schemas, url="http://localhost:11434/api/chat"):
    body = {"model": model, "messages": messages, "tools": schemas, "stream": False, "think": False}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())["message"]

def run_agent(model, system, user, tools, schemas, max_steps=8, log=print):
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    calls = []
    for step in range(1, max_steps + 1):
        msg = ask(model, messages, schemas)                      # 1. the model decides
        messages.append(msg)
        if not msg.get("tool_calls"):                            # 2. no tool asked for: it is done
            return (msg.get("content") or "").strip(), calls, step
        for tc in msg["tool_calls"]:                             # 3. do what it asked
            name, args = tc["function"]["name"], tc["function"].get("arguments") or {}
            try:
                if isinstance(args, str):
                    args = json.loads(args)
                result = tools[name](**args)
            except Exception as e:                               # a bad call is feedback, not a crash
                result = {"error": f"{type(e).__name__}: {e}"}
            calls.append((name, args))
            log(name, args, result)
            messages.append({"role": "tool", "tool_name": name, "content": json.dumps(result)})  # 4. show it
    return None, calls, max_steps                                # step limit hit: no answer
