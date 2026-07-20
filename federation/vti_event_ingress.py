from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping

from federation.vti_event_consumer import EventAuthenticationError, EventValidationError, VtiEventConsumer

MAX_BODY_BYTES = 2_000_000


def ingest_request(body: bytes, headers: Mapping[str, str], consumer: VtiEventConsumer) -> tuple[int, dict[str, Any]]:
    if len(body) > MAX_BODY_BYTES:
        return 413, {"error": "payload_too_large"}
    signature = headers.get("x-vti-signature", "")
    correlation = headers.get("x-correlation-id", "")
    try:
        event = json.loads(body.decode("utf-8"))
        if correlation and event.get("correlation_id") != correlation:
            return 400, {"error": "correlation_mismatch"}
        ack = consumer.ingest(event, signature)
        return 202, {"accepted": ack.accepted, "duplicate": ack.duplicate, "event_id": ack.event_id, "correlation_id": ack.correlation_id, "status": ack.status}
    except json.JSONDecodeError:
        return 400, {"error": "invalid_json"}
    except EventAuthenticationError:
        return 401, {"error": "invalid_signature"}
    except EventValidationError as exc:
        return 400, {"error": "invalid_event", "detail": str(exc)}


def serve(host: str = "127.0.0.1", port: int = 8791) -> None:
    secret = os.environ.get("VTI_EVENT_SIGNING_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("VTI_EVENT_SIGNING_SECRET is required")
    database = Path(os.environ.get("VTI_EVENT_DATABASE", "var/vti-events.sqlite3"))
    database.parent.mkdir(parents=True, exist_ok=True)
    consumer = VtiEventConsumer(database, secret)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            payload = {"status": "ok", "service": "hub-vti-event-ingress", "schema_version": "1.0.0"}
            self._send(200, payload)

        def do_POST(self) -> None:
            if self.path != "/v1/federation/vti/events":
                self._send(404, {"error": "not_found"})
                return
            length = int(self.headers.get("content-length", "0"))
            if length < 1 or length > MAX_BODY_BYTES:
                self._send(413 if length > MAX_BODY_BYTES else 400, {"error": "invalid_content_length"})
                return
            body = self.rfile.read(length)
            status, payload = ingest_request(body, {key.lower(): value for key, value in self.headers.items()}, consumer)
            self._send(status, payload)

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            content = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_: Any) -> None:
            return

    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    serve(os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8791")))
