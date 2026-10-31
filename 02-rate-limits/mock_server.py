"""A local stand-in for an LLM API with a rate limit: 4 requests in flight at once.

Each answer takes 0.5 s. A request over the limit gets 429 with `retry-after: 1`,
like a real API asking you to slow down.
"""
import json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LIMIT = 4
lock, in_flight, stats = threading.Lock(), 0, {"ok": 0, "429": 0}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global in_flight
        self.rfile.read(int(self.headers.get("content-length", 0)))
        with lock:
            busy = in_flight >= LIMIT
            if busy:
                stats["429"] += 1
            else:
                in_flight += 1
        if busy:
            body = json.dumps({"type": "error", "error": {"type": "rate_limit_error", "message": "Too many requests"}}).encode()
            self.send_response(429)
            self.send_header("retry-after", "1")
        else:
            time.sleep(0.5)
            with lock:
                in_flight -= 1
                stats["ok"] += 1
            body = json.dumps({
                "id": "msg", "type": "message", "role": "assistant", "model": "mock",
                "content": [{"type": "text", "text": "Done."}], "stop_reason": "end_turn",
                "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 2},
            }).encode()
            self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        print(f"[server] answered {stats['ok']}, sent 429 x{stats['429']}", flush=True)

    def log_message(self, *args):
        pass


ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
