import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from open_notebook_client import OpenNotebookClient, ApprovalRequired, InvalidSourceURL


class RecordingHandler(BaseHTTPRequestHandler):
    requests = []

    def _record(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        self.__class__.requests.append(
            {
                "method": self.command,
                "path": self.path,
                "authorization": self.headers.get("Authorization"),
                "body": json.loads(body) if body else None,
            }
        )

    def do_GET(self):
        self._record()
        if self.path == "/api/notebooks":
            payload = [{"id": "notebook:research", "name": "Deep Research — Hermes"}]
        elif self.path == "/api/sources/source%3A1/status":
            payload = {"status": "completed", "message": "Ready"}
        else:
            self.send_error(404)
            return
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        self._record()
        if self.path == "/api/notebooks":
            payload = {"id": "notebook:research", "name": self.__class__.requests[-1]["body"]["name"]}
        elif self.path == "/api/sources/json":
            payload = {"id": "source:1", "status": "queued"}
        else:
            self.send_error(404)
            return
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *_args):
        return


class OpenNotebookClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), RecordingHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        RecordingHandler.requests.clear()
        self.client = OpenNotebookClient(self.base_url, "secret-password")

    def test_lists_notebooks_with_bearer_auth(self):
        notebooks = self.client.list_notebooks()
        self.assertEqual(notebooks[0]["id"], "notebook:research")
        self.assertEqual(RecordingHandler.requests[0]["authorization"], "Bearer secret-password")

    def test_creates_research_notebook(self):
        notebook = self.client.create_notebook("Deep Research — Hermes", "Investigación verificada")
        self.assertEqual(notebook["id"], "notebook:research")
        self.assertEqual(RecordingHandler.requests[0]["body"]["description"], "Investigación verificada")

    def test_refuses_source_addition_without_explicit_approval(self):
        with self.assertRaises(ApprovalRequired):
            self.client.add_source_url("notebook:research", "https://example.com/report", approved=False)
        self.assertEqual(RecordingHandler.requests, [])

    def test_rejects_non_http_source_url(self):
        with self.assertRaises(InvalidSourceURL):
            self.client.add_source_url("notebook:research", "file:///etc/passwd", approved=True)
        self.assertEqual(RecordingHandler.requests, [])

    def test_adds_approved_url_to_selected_notebook(self):
        source = self.client.add_source_url(
            "notebook:research",
            "https://example.com/report",
            title="Primary report",
            approved=True,
        )
        self.assertEqual(source["id"], "source:1")
        body = RecordingHandler.requests[0]["body"]
        self.assertEqual(body["type"], "link")
        self.assertEqual(body["notebooks"], ["notebook:research"])
        self.assertEqual(body["url"], "https://example.com/report")
        self.assertTrue(body["async_processing"])

    def test_adds_approved_digest_with_citations(self):
        self.client.add_research_digest(
            "notebook:research",
            "Digest: Market",
            "Verified finding.",
            ["https://official.example/report", "https://journal.example/paper"],
            approved=True,
        )
        body = RecordingHandler.requests[0]["body"]
        self.assertEqual(body["type"], "text")
        self.assertIn("Verified finding.", body["content"])
        self.assertIn("https://official.example/report", body["content"])
        self.assertEqual(body["notebooks"], ["notebook:research"])

    def test_reads_source_processing_status(self):
        status = self.client.get_source_status("source:1")
        self.assertEqual(status["status"], "completed")


if __name__ == "__main__":
    unittest.main()
