import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from research_web import (
    UnsafeURL,
    extract_readable_text,
    parse_bing_results,
    validate_public_url,
)


BING_HTML = """
<html><body>
<li class="b_algo"><h2><a href="https://example.org/primary">Primary report</a></h2>
<div class="b_caption"><p>Official primary evidence.</p></div></li>
<li class="b_algo"><h2><a href="https://example.net/analysis">Independent analysis</a></h2>
<div class="b_caption"><p>Secondary corroboration.</p></div></li>
</body></html>
"""


class ResearchWebTest(unittest.TestCase):
    def test_parses_bing_results(self):
        results = parse_bing_results(BING_HTML, limit=5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["url"], "https://example.org/primary")
        self.assertEqual(results[0]["title"], "Primary report")
        self.assertEqual(results[0]["snippet"], "Official primary evidence.")

    def test_extracts_readable_text_without_active_or_navigation_content(self):
        html = """
        <html><head><title>Evidence</title><script>steal()</script></head>
        <body><nav>Menu</nav><main><h1>Finding</h1><p>Verified text.</p></main>
        <footer>Footer</footer></body></html>
        """
        result = extract_readable_text(html)
        self.assertEqual(result["title"], "Evidence")
        self.assertIn("Finding", result["text"])
        self.assertIn("Verified text.", result["text"])
        self.assertNotIn("steal", result["text"])
        self.assertNotIn("Menu", result["text"])

    def test_rejects_private_and_non_http_urls(self):
        for url in ("file:///etc/passwd", "http://127.0.0.1/private", "http://localhost/admin"):
            with self.subTest(url=url), self.assertRaises(UnsafeURL):
                validate_public_url(url)

    def test_rejects_urls_with_embedded_credentials(self):
        with self.assertRaises(UnsafeURL):
            validate_public_url("https://user:password@example.com/")


if __name__ == "__main__":
    unittest.main()
