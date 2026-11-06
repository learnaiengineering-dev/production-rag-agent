"""A local stand-in for an LLM API where the main model can be "down".

  python mock_server.py            # claude-sonnet-5-5 is down (529 overloaded), claude-haiku-5-5 works
  python mock_server.py all-down   # both models are down
  python mock_server.py ok         # everything works

A working model answers after 0.5 s. A model that is down answers 529 "overloaded" after 0.3 s.
It speaks just enough of the Anthropic Messages API for the SDK.
"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = sys.argv[1] if len(sys.argv) > 1 else "primary-down"
PRIMARY = "claude-sonnet-5-5"
OK_AFTER, DOWN_AFTER = 0.5, 0.3
ANSWER = "You can return most items within 30 days of delivery. Start the return from your orders page."


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128

    def handle_error(self, request, client_address):
        pass


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))))
        model = req.get("model")
        down = MODE == "all-down" or (MODE == "primary-down" and model == PRIMARY)
        if down:
            time.sleep(DOWN_AFTER)
            body = json.dumps({"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}).encode()
            status = 529
        else:
            time.sleep(OK_AFTER)
            body = json.dumps({"id": "msg", "type": "message", "role": "assistant", "model": model,
                               "content": [{"type": "text", "text": ANSWER}], "stop_reason": "end_turn",
                               "stop_sequence": None, "usage": {"input_tokens": 12, "output_tokens": 18}}).encode()
            status = 200
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


Server(("127.0.0.1", 8787), Handler).serve_forever()
