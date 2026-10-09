"""Minimal local HTTP server for the AI Assistant browser dashboard."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ai.assistant.service import process_question


PAGE = Path(__file__).parent / "static" / "index.html"


class AssistantHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self._send(404, "Not found", "text/plain; charset=utf-8")
            return
        self._send(200, PAGE.read_text(encoding="utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/ask":
            self._send(404, json.dumps({"error": "Not found"}), "application/json; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 10000:
                raise ValueError("Send a question under 10,000 bytes.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            question = payload.get("question", "")
            if not isinstance(question, str) or not question.strip():
                raise ValueError("Enter a question first.")
            result = process_question(question.strip())
            response = {
                "route": result.get("route"),
                "answer": result.get("answer") or {},
                "natural_language_response": result.get("natural_language_response"),
                "errors": result.get("errors") or [],
            }
            self._send(200, json.dumps(response, default=str), "application/json; charset=utf-8")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send(400, json.dumps({"error": str(exc)}), "application/json; charset=utf-8")
        except Exception as exc:
            error_body = json.dumps(
                {"error": f"Assistant request failed: {type(exc).__name__}"}
            )
            self._send(
                500,
                error_body,
                "application/json; charset=utf-8",
            )

    def log_message(self, format, *args):
        print(f"[assistant-ui] {self.address_string()} - {format % args}")


def main():
    host = "127.0.0.1"
    port = int(os.getenv("AI_ASSISTANT_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), AssistantHandler)
    print(f"AI Assistant dashboard: http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
