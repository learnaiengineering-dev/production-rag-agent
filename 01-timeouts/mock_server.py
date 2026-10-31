"""A local stand-in for an LLM API, so the hang is reproducible.

  python mock_server.py hang    # every request hangs (never answers)
  python mock_server.py flaky   # the first request hangs, the next ones answer

It speaks just enough of the Anthropic Messages API for the SDK to parse it.
"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = sys.argv[1] if len(sys.argv) > 1 else "flaky"
count = 0


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global count
        count += 1
        self.rfile.read(int(self.headers.get("content-length", 0)))
        if MODE == "hang" or count == 1:
            print(f"[server] request {count}: hanging", flush=True)
            time.sleep(3600)
            return
        print(f"[server] request {count}: answering", flush=True)
        body = json.dumps({
            "id": f"msg_{count}", "type": "message", "role": "assistant", "model": "mock",
            "content": [{"type": "text", "text": "Refunds take 5 business days."}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 12, "output_tokens": 7},
        }).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
