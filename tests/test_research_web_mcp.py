import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import research_web_mcp


class ResearchWebMcpContractTest(unittest.TestCase):
    def test_server_exposes_search_and_fetch(self):
        self.assertEqual(set(research_web_mcp.tool_names()), {"search_public_web", "fetch_public_source"})


if __name__ == "__main__":
    unittest.main()
