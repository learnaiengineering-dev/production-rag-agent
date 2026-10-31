"""A local stand-in for an LLM API that "generates" at a steady pace.

  python mock_server.py          # first word after 0.4 s, then one word every 0.1 s
  python mock_server.py break    # streaming stops halfway: the connection drops

Non-streaming requests get the whole answer at the end, like a real API.
It speaks just enough of the Anthropic Messages API (JSON and SSE) for the SDK.
"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = sys.argv[1] if len(sys.argv) > 1 else "normal"
ANSWER = ("You can return most items within 30 days of delivery. Start the return from your orders page, "
          "print the label, and drop the parcel at any post office. Refunds go back to your original payment "
          "method within 5 business days of the item reaching us. Opened software and gift cards can't be "
          "returned, but faulty items are always covered.").split(" ")
FIRST, EACH = 0.4, 0.1


def sse(handler, event, data):
    handler.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
    handler.wfile.flush()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))))
        if not req.get("stream"):
            time.sleep(FIRST + EACH * (len(ANSWER) - 1))
            body = json.dumps({"id": "msg", "type": "message", "role": "assistant", "model": "mock",
                               "content": [{"type": "text", "text": " ".join(ANSWER)}], "stop_reason": "end_turn",
                               "stop_sequence": None, "usage": {"input_tokens": 12, "output_tokens": len(ANSWER)}}).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()
        sse(self, "message_start", {"type": "message_start", "message": {"id": "msg", "type": "message", "role": "assistant",
            "content": [], "model": "mock", "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 12, "output_tokens": 1}}})
        sse(self, "content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})
        time.sleep(FIRST)
        for i, word in enumerate(ANSWER):
            if MODE == "break" and i == len(ANSWER) // 2:
                self.connection.close()          # the network drops mid-answer
                return
            sse(self, "content_block_delta", {"type": "content_block_delta", "index": 0,
                                              "delta": {"type": "text_delta", "text": (" " if i else "") + word}})
            time.sleep(EACH)
        sse(self, "content_block_stop", {"type": "content_block_stop", "index": 0})
        sse(self, "message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                                    "usage": {"output_tokens": len(ANSWER)}})
        sse(self, "message_stop", {"type": "message_stop"})

    def log_message(self, *args):
        pass


ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
