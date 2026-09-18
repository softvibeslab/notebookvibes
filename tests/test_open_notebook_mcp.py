import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import open_notebook_mcp


class McpServerContractTest(unittest.TestCase):
    def test_client_requires_profile_secret(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPEN_NOTEBOOK_PASSWORD"):
                open_notebook_mcp.make_client(env_path="/definitely/missing/notebookllm.env")

    def test_client_loads_profile_secret_file_when_environment_is_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                "OPEN_NOTEBOOK_URL='http://127.0.0.1:8502'\n"
                "OPEN_NOTEBOOK_PASSWORD='profile-secret'\n"  # pragma: allowlist secret — test fixture
            )
            with patch.dict(os.environ, {}, clear=True):
                client = open_notebook_mcp.make_client(env_path=str(env_path))
            self.assertEqual(client.base_url, "http://127.0.0.1:8502")
            self.assertEqual(client.password, "profile-secret")

    def test_server_exposes_expected_tools(self):
        names = set(open_notebook_mcp.tool_names())
        self.assertEqual(
            names,
            {
                "list_notebooks",
                "create_research_notebook",
                "add_source_url",
                "add_research_digest",
                "get_source_status",
            },
        )


if __name__ == "__main__":
    unittest.main()
