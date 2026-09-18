"""Credential-free public web search and respectful page extraction for NotebookLLM."""

from __future__ import annotations

import base64
import ipaddress
import socket
from html import unescape
from typing import Any
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup


USER_AGENT = "NotebookLLMResearch/1.0 (+https://notebook.softvibes.cloud)"
MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024


class ResearchWebError(RuntimeError):
    pass


class UnsafeURL(ResearchWebError):
    pass


class RobotsDenied(ResearchWebError):
    pass


def validate_public_url(url: str) -> str:
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeURL("Only absolute http(s) URLs are allowed")
    if parsed.username or parsed.password:
        raise UnsafeURL("URLs with embedded credentials are not allowed")
    if len(url) > 4096:
        raise UnsafeURL("URL is too long")
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeURL(f"Hostname cannot be resolved: {parsed.hostname}") from exc
    addresses = {info[4][0].split("%", 1)[0] for info in infos}
    if not addresses:
        raise UnsafeURL("Hostname resolved to no addresses")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise UnsafeURL(f"Private or non-public destination is blocked: {address}")
    return url


def _decode_bing_target(href: str) -> str:
    parsed = urlparse(href)
    if not parsed.hostname or not parsed.hostname.endswith("bing.com"):
        return href
    value = parse_qs(parsed.query).get("u", [""])[0]
    if not value.startswith("a1"):
        return href
    encoded = value[2:]
    encoded += "=" * (-len(encoded) % 4)
    try:
        return base64.urlsafe_b64decode(encoded).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return href


def parse_bing_results(html: str, limit: int = 10) -> list[dict[str, str]]:
    limit = max(1, min(int(limit), 20))
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in soup.select("li.b_algo"):
        anchor = item.select_one("h2 a[href]")
        if anchor is None:
            continue
        href = _decode_bing_target(str(anchor.get("href", "")))
        parsed = urlparse(href)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            continue
        if href in seen:
            continue
        caption = item.select_one(".b_caption p")
        results.append(
            {
                "title": anchor.get_text(" ", strip=True),
                "url": href,
                "snippet": caption.get_text(" ", strip=True) if caption else "",
                "search_engine": "Bing public web results",
            }
        )
        seen.add(href)
        if len(results) >= limit:
            break
    return results


def search_web(query: str, limit: int = 10) -> list[dict[str, str]]:
    query = query.strip()
    if not query:
        raise ValueError("Search query is required")
    if len(query) > 500:
        raise ValueError("Search query is too long")
    limit = max(1, min(int(limit), 20))
    url = f"https://www.bing.com/search?q={quote_plus(query)}&count={limit}"
    try:
        response = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.8"},
            timeout=20.0,
            follow_redirects=False,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ResearchWebError(f"Search request failed: {exc}") from exc
    results = parse_bing_results(response.text, limit)
    if not results:
        raise ResearchWebError("Search engine returned no parseable results")
    return results


def extract_readable_text(html: str, max_chars: int = 40000) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for tag in soup.select("script,style,noscript,svg,nav,footer,form,button"):
        tag.decompose()
    root = soup.select_one("article") or soup.select_one("main") or soup.body or soup
    lines = []
    for line in root.get_text("\n", strip=True).splitlines():
        cleaned = " ".join(unescape(line).split())
        if cleaned and (not lines or cleaned != lines[-1]):
            lines.append(cleaned)
    return {"title": title, "text": "\n".join(lines)[: max(1000, min(max_chars, 100000))]}


def _get_with_safe_redirects(url: str, max_bytes: int = MAX_DOWNLOAD_BYTES) -> tuple[str, str, bytes]:
    current = validate_public_url(url)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,application/pdf,application/json;q=0.9,*/*;q=0.2"}
    with httpx.Client(timeout=30.0, follow_redirects=False, headers=headers) as client:
        for _ in range(6):
            try:
                with client.stream("GET", current) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise ResearchWebError("Redirect response lacks Location header")
                        current = validate_public_url(urljoin(current, location))
                        continue
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
                    chunks = []
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > max_bytes:
                            raise ResearchWebError(f"Page exceeds {max_bytes} bytes")
                        chunks.append(chunk)
                    return str(response.url), content_type, b"".join(chunks)
            except httpx.HTTPError as exc:
                raise ResearchWebError(f"Page retrieval failed: {exc}") from exc
    raise ResearchWebError("Too many redirects")


def _robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        _final, content_type, raw = _get_with_safe_redirects(robots_url, max_bytes=512_000)
    except ResearchWebError:
        return True
    if content_type and "text" not in content_type:
        return True
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(raw.decode("utf-8", errors="replace").splitlines())
    return parser.can_fetch(USER_AGENT, url)


def fetch_public_page(url: str, max_chars: int = 40000) -> dict[str, Any]:
    safe_url = validate_public_url(url)
    if not _robots_allowed(safe_url):
        raise RobotsDenied("robots.txt does not permit this automated fetch")
    final_url, content_type, raw = _get_with_safe_redirects(safe_url)
    if content_type == "application/pdf" or raw.startswith(b"%PDF"):
        try:
            import fitz
        except ImportError as exc:
            raise ResearchWebError("PDF extraction is unavailable; save the URL directly to Open Notebook") from exc
        try:
            document = fitz.open(stream=raw, filetype="pdf")
            text = "\n".join(page.get_text() for page in document)
            title = str(document.metadata.get("title") or "")
        except Exception as exc:
            raise ResearchWebError(f"PDF extraction failed: {exc}") from exc
        return {
            "url": final_url,
            "title": title,
            "content_type": "application/pdf",
            "text": text[: max(1000, min(max_chars, 100000))],
        }
    if content_type not in {"text/html", "text/plain", "application/json", "application/xml", "text/xml"}:
        raise ResearchWebError(f"Unsupported content type: {content_type or 'unknown'}")
    decoded = raw.decode("utf-8", errors="replace")
    if content_type == "text/html" or "<html" in decoded[:1000].lower():
        extracted = extract_readable_text(decoded, max_chars=max_chars)
    else:
        extracted = {"title": "", "text": decoded[: max(1000, min(max_chars, 100000))]}
    return {"url": final_url, "content_type": content_type, **extracted}
