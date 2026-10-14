"""
Zero-dependency HTTP Server & REST API for Distributed Snapshot Simulator.
Serves interactive Web UI and simulation control endpoints.
"""

import json
import os
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from simulator.engine import SimulationEngine
from simulator.topology import NetworkTopology

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

# Shared Simulation Engine Instance
engine = SimulationEngine(NetworkTopology.create_ring(node_count=4, initial_balance=100, latency=2))


class SimulatorRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _send_json(self, data, status=HTTPStatus.OK):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self._send_json(engine.get_state())
        elif parsed.path == "/api/health":
            self._send_json({"status": "running", "step": engine.current_step})
        else:
            # Fallback to serving static files from web/
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except json.JSONDecodeError:
            payload = {}

        if parsed.path == "/api/step":
            state = engine.step()
            self._send_json(state)

        elif parsed.path == "/api/transfer":
            sender = payload.get("sender")
            receiver = payload.get("receiver")
            amount = int(payload.get("amount", 10))
            latency = payload.get("latency", 2)
            msg = engine.send_transfer(sender, receiver, amount, latency=latency)
            self._send_json({"success": msg is not None, "state": engine.get_state()})

        elif parsed.path == "/api/snapshot":
            initiator = payload.get("initiator", "P0")
            snap = engine.initiate_snapshot(initiator)
            self._send_json({"success": snap is not None, "state": engine.get_state()})

        elif parsed.path == "/api/run_until_complete":
            state = engine.run_until_snapshot_complete(max_steps=50)
            self._send_json(state)

        elif parsed.path == "/api/reset":
            topology_type = payload.get("topology", "ring")
            node_count = int(payload.get("node_count", 4))
            balance = int(payload.get("initial_balance", 100))
            latency = int(payload.get("latency", 2))
            engine.reset(topology_type=topology_type, node_count=node_count, initial_balance=balance, latency=latency)
            self._send_json(engine.get_state())

        elif parsed.path == "/api/scenario/run_demo":
            # Preset classic scenario:
            # Reset -> 2 transfers in-flight -> Trigger snapshot
            engine.reset("ring", node_count=4, initial_balance=100, latency=3)
            engine.send_transfer("P0", "P1", 25, latency=3)
            engine.send_transfer("P2", "P3", 15, latency=3)
            engine.step()
            engine.initiate_snapshot("P0")
            self._send_json(engine.get_state())

        else:
            self._send_json({"error": "Unknown API endpoint"}, status=HTTPStatus.NOT_FOUND)


def start_server(port=PORT):
    server = ThreadingHTTPServer(("0.0.0.0", port), SimulatorRequestHandler)
    print("=" * 60)
    print(f" 🚀 Distributed Snapshot Simulator Server running at:")
    print(f"    👉 Local:   http://localhost:{port}")
    print(f"    👉 Network: http://127.0.0.1:{port}")
    print(f" Press Ctrl+C to terminate the server.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        server.shutdown()


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    start_server(port_arg)
