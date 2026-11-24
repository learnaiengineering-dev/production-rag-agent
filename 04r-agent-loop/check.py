"""Quick check before run.py: is Ollama running, is the model there, does one chat call work?"""
import json, sys, urllib.request, urllib.error
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen3:8b"
BASE = "http://localhost:11434"
try:
    tags = json.loads(urllib.request.urlopen(BASE + "/api/tags", timeout=10).read())
except Exception as e:
    sys.exit(f"Ollama is not answering at {BASE} ({type(e).__name__}: {e}).\nOpen the Ollama app, or run `ollama serve` in another Terminal tab, then try again.")
names = [m["name"] for m in tags.get("models", [])]
print("models installed:", ", ".join(names) or "none")
if MODEL not in names:
    sys.exit(f"{MODEL} is not installed. Run: ollama pull {MODEL}")
body = {"model": MODEL, "messages": [{"role": "user", "content": "Say OK."}], "stream": False, "think": False}
req = urllib.request.Request(BASE + "/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
try:
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    print("chat works:", r["message"]["content"][:60])
except urllib.error.HTTPError as e:
    sys.exit(f"chat failed: HTTP {e.code}: {e.read().decode()[:300]}")
except Exception as e:
    sys.exit(f"chat failed: {type(e).__name__}: {e}")
