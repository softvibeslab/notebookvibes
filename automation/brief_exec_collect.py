#!/usr/bin/env python3
"""Brief ejecutivo diario determinista y de solo lectura.

Consulta Calendar, Gmail, GitHub y Notion mediante Composio CLI. Nunca
realiza mutaciones. Cada integración tiene timeout independiente para que
una fuente caída no bloquee el informe completo.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Cancun")
NOW = datetime.now(TZ)
TODAY = NOW.date()
TOMORROW = TODAY + timedelta(days=1)
DAY_AFTER = TODAY + timedelta(days=2)


def call(slug: str, payload: dict, timeout: int = 55) -> dict:
    try:
        p = subprocess.run(
            ["composio", "execute", slug, "-d", json.dumps(payload, ensure_ascii=False)],
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if p.returncode != 0:
            return {"_error": (p.stderr or p.stdout or f"exit {p.returncode}")[:280]}
        try:
            parsed = json.loads(p.stdout)
            if isinstance(parsed, dict) and parsed.get("successful") is False:
                return {"_error": clean(parsed.get("error") or "la integración respondió successful=false", 280)}
            if isinstance(parsed, dict) and parsed.get("error") not in (None, "", False):
                return {"_error": clean(parsed.get("error"), 280)}
            return parsed
        except json.JSONDecodeError:
            return {"_error": "respuesta no JSON", "_raw": p.stdout[:500]}
    except subprocess.TimeoutExpired:
        return {"_error": f"timeout de {timeout}s"}
    except Exception as exc:
        return {"_error": str(exc)[:280]}


def clean(value, limit=140):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def payload_data(resp):
    if not isinstance(resp, dict):
        return {}
    return resp.get("data", resp)


def event_start(obj):
    start = obj.get("start")
    if isinstance(start, dict):
        return start.get("dateTime") or start.get("date") or ""
    return start or obj.get("start_time") or obj.get("startTime") or ""


def parse_events(resp):
    found, seen = [], set()
    data = payload_data(resp)
    for obj in walk(data):
        title = obj.get("summary") or obj.get("title")
        start = event_start(obj)
        if not title or not start:
            continue
        key = (str(title), str(start))
        if key in seen:
            continue
        seen.add(key)
        cal = obj.get("calendar_summary") or obj.get("calendarName") or obj.get("organizer", {}).get("displayName") if isinstance(obj.get("organizer"), dict) else ""
        found.append({"title": clean(title, 100), "start": clean(start, 40), "calendar": clean(cal, 60)})
    found.sort(key=lambda x: x["start"])
    return found[:12]


def parse_emails(resp):
    found, seen = [], set()
    data = payload_data(resp)
    for obj in walk(data):
        mid = obj.get("messageId") or obj.get("message_id") or obj.get("id")
        subject = obj.get("subject")
        sender = obj.get("sender") or obj.get("from") or obj.get("from_email")
        if not subject or not (mid or sender):
            continue
        # Para un brief ejecutivo una cadena de avisos idénticos es una sola
        # señal; el detalle puede revisarse después en Gmail.
        key = f"{str(subject).strip().casefold()}|{str(sender).strip().casefold()}"
        if key in seen:
            continue
        seen.add(key)
        labels = obj.get("labelIds") or obj.get("label_ids") or obj.get("labels") or []
        if isinstance(labels, str):
            labels = [labels]
        found.append({
            "subject": clean(subject, 100),
            "sender": clean(sender, 70),
            "snippet": clean(obj.get("snippet") or obj.get("preview") or "", 120),
            "labels": {str(x).upper() for x in labels},
            "date": clean(obj.get("date") or obj.get("internalDate") or obj.get("received_at") or "", 40),
        })
    def score(x):
        labels = x["labels"]
        text = f"{x['subject']} {x['sender']}".lower()
        high_signal = (
            "acción necesaria", "action required", "alerta de seguridad",
            "security alert", "failure", "fallo", "factura", "invoice",
            "pago", "payment", "reunión", "meeting", "contrato",
        )
        low_signal = (
            "temu", "bumble", "tiktok", "newsletter", "descuento",
            "promotion", "notifications since", "publicó:",
        )
        value = (3 if "IMPORTANT" in labels else 0) + (2 if "UNREAD" in labels else 0) + (1 if "STARRED" in labels else 0)
        value += 6 if any(term in text for term in high_signal) else 0
        value -= 7 if any(term in text for term in low_signal) else 0
        return value
    found.sort(key=lambda x: (score(x), x["date"]), reverse=True)
    return found[:10]


def parse_github(resp):
    found, seen = [], set()
    data = payload_data(resp)
    for obj in walk(data):
        title = obj.get("title")
        url = obj.get("html_url") or obj.get("url")
        if not title or not url or "api.github.com" in str(url):
            continue
        key = str(url)
        if key in seen:
            continue
        seen.add(key)
        found.append({
            "title": clean(title, 105),
            "state": clean(obj.get("state") or "", 20),
            "url": clean(url, 180),
            "updated": clean(obj.get("updated_at") or obj.get("created_at") or "", 40),
            "is_pr": bool(obj.get("pull_request")),
        })
    found.sort(key=lambda x: x["updated"], reverse=True)
    return found[:8]


def notion_title(obj):
    title = obj.get("title")
    if isinstance(title, str):
        return title
    if isinstance(title, list):
        return "".join(str(x.get("plain_text", "")) for x in title if isinstance(x, dict))
    props = obj.get("properties")
    if isinstance(props, dict):
        for val in props.values():
            if isinstance(val, dict) and val.get("type") == "title":
                return "".join(str(x.get("plain_text", "")) for x in val.get("title", []) if isinstance(x, dict))
    return ""


def parse_notion(resp):
    found, seen, seen_titles = [], set(), set()
    data = payload_data(resp)
    for obj in walk(data):
        oid = obj.get("id")
        title = notion_title(obj)
        if not oid or not title:
            continue
        normalized_title = title.strip().casefold()
        if oid in seen or normalized_title in seen_titles:
            continue
        seen.add(oid)
        seen_titles.add(normalized_title)
        found.append({
            "title": clean(title, 105),
            "edited": clean(obj.get("last_edited_time") or obj.get("lastEditedTime") or "", 40),
            "url": clean(obj.get("url") or "", 180),
        })
    found.sort(key=lambda x: x["edited"], reverse=True)
    return found[:6]


requests = {
    "calendar": ("GOOGLECALENDAR_EVENTS_LIST_ALL_CALENDARS", {
        "q": "",
        "time_min": f"{TODAY.isoformat()}T00:00:00-05:00",
        "time_max": f"{DAY_AFTER.isoformat()}T00:00:00-05:00",
        "event_types": [],
        "calendar_ids": [],
        "show_deleted": False,
        "single_events": True,
        "response_detail": "full",
        "max_results_per_calendar": 25,
    }),
    "gmail": ("GMAIL_FETCH_EMAILS", {
        "query": "newer_than:1d (is:unread OR is:important OR is:starred)",
        "user_id": "me",
        "verbose": False,
        "ids_only": False,
        "label_ids": [],
        "page_token": "",
        "max_results": 20,
        "include_payload": False,
        "include_spam_trash": False,
    }),
    "github": ("GITHUB_SEARCH_ISSUES_AND_PULL_REQUESTS", {
        "q": f"user:softvibeslab updated:>={ (TODAY - timedelta(days=1)).isoformat() }",
        "page": 1,
        "sort": "updated",
        "order": "desc",
        "per_page": 20,
        "response_detail": "minimal",
    }),
    "notion": ("NOTION_SEARCH_NOTION_PAGE", {
        "query": "",
        "direction": "descending",
        "page_size": 20,
        "timestamp": "last_edited_time",
        "filter_value": "page",
        "start_cursor": "",
        "filter_property": "object",
        "filter_properties": [],
    }),
}

responses = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    futs = {pool.submit(call, slug, payload): name for name, (slug, payload) in requests.items()}
    for fut in concurrent.futures.as_completed(futs):
        responses[futs[fut]] = fut.result()

events = parse_events(responses.get("calendar", {}))
emails = parse_emails(responses.get("gmail", {}))
github = parse_github(responses.get("github", {}))
notion = parse_notion(responses.get("notion", {}))
errors = {k: v.get("_error") for k, v in responses.items() if isinstance(v, dict) and v.get("_error")}

priorities = []
if events:
    next_timed = next((event for event in events if "T" in event["start"]), events[0])
    priorities.append(f"Preparar el próximo evento con horario: {next_timed['title']}")
if emails:
    priorities.append(f"Revisar correo prioritario: {emails[0]['subject']}")
if github:
    priorities.append(f"Revisar actividad técnica: {github[0]['title']}")
if notion:
    priorities.append(f"Validar pendiente en Notion: {notion[0]['title']}")
while len(priorities) < 3:
    priorities.append("Revisar pendientes manuales; no hubo otra señal verificable en las fuentes consultadas")

print(f"# Brief ejecutivo — {TODAY.isoformat()}\n")
print(f"**Corte:** {NOW.strftime('%H:%M')} · **Zona:** America/Cancun · **Modo:** solo lectura\n")
print("## Tres prioridades")
for i, item in enumerate(priorities[:3], 1):
    print(f"{i}. {item}")

print("\n## Agenda de hoy y mañana")
if events:
    for item in events:
        suffix = f" · {item['calendar']}" if item["calendar"] else ""
        print(f"- {item['start']} — **{item['title']}**{suffix}")
else:
    print("- No se recuperaron eventos verificables en la ventana.")

print("\n## Correos a atender")
if emails:
    for item in emails:
        flags = []
        if "UNREAD" in item["labels"]: flags.append("no leído")
        if "IMPORTANT" in item["labels"]: flags.append("importante")
        marker = f" ({', '.join(flags)})" if flags else ""
        sender = f" — {item['sender']}" if item["sender"] else ""
        print(f"- **{item['subject']}**{sender}{marker}")
else:
    print("- No se recuperaron mensajes prioritarios de las últimas 24 horas.")

print("\n## Alertas técnicas")
if github:
    for item in github:
        kind = "PR" if item["is_pr"] else "Issue"
        state = f" · {item['state']}" if item["state"] else ""
        print(f"- {kind}: **{item['title']}**{state}")
else:
    print("- No se recuperó actividad reciente de issues o pull requests de softvibeslab.")

print("\n## Notion")
if notion:
    for item in notion:
        edited = f" · editado {item['edited']}" if item["edited"] else ""
        print(f"- **{item['title']}**{edited}")
else:
    print("- No se recuperaron páginas compartidas recientes.")

print("\n## Límites y bloqueos")
if errors:
    for name, error in errors.items():
        print(f"- {name}: {clean(error, 180)}")
else:
    print("- Todas las consultas finalizaron sin error técnico reportado.")
print("- El brief no envió correos ni modificó Calendar, GitHub o Notion.")

print("\n## Próximo paso mínimo")
print(f"- Abrir la primera prioridad y confirmar en Telegram si debe convertirse en acción.")
