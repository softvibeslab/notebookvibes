---
name: composio-telegram-miniapp
description: Use when linking Composio apps from a Telegram Mini App.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [composio, telegram, miniapp, oauth, gmail, notion, google-calendar]
    related_skills: [hosted-tool-platform-integrations, hermes-agent]
---

# Composio Telegram Mini App

## Overview

Build and operate a searchable Telegram Mini App that exposes Composio's live toolkit catalog while keeping Notebookvibes recommendations highlighted: Google Drive, Notion, YouTube, GitHub, Gmail, Google Calendar, Slack, and Dropbox. The interface offers `Recomendadas`, `Conectadas`, and `Todas`, assigns every toolkit to a stable Spanish category, combines category filters with search/view filters, paginates large result sets, and searches the complete catalog returned by Composio. The backend generates fresh authorization links and reports connection state. It does not expose OAuth credentials or execute application actions.

This skill ships a working Python backend and a Telegram-aware frontend. Use the files under `scripts/` and `assets/`; never place Composio credentials, OAuth tokens, Telegram bot tokens, callback codes, or live capability URLs in the skill.

## When to Use

Use this skill when:

- a Hermes profile needs a UI for connecting Composio toolkits;
- Gmail, Notion, or Google Calendar authorization should start inside Telegram;
- the setup must be portable to another Hermes profile;
- a temporary HTTPS prototype or a production deployment is required.

Do not use the bundled capability-token mode as a general multi-user production service. For production, validate Telegram `initData` on the backend and isolate each Telegram user to a separate Composio identity.

## Security Model

The bundled server is intentionally narrow:

- live toolkit catalog loaded from `composio dev --mode on toolkits list`, cached for one hour and validated server-side;
- eight Notebookvibes recommendations remain highlighted, but any connectable toolkit returned by the live catalog may be linked;
- user-supplied slugs are syntax-checked and must exist in the server-side catalog; no-auth toolkits are shown as ready and cannot open an unnecessary link flow;
- `Recomendadas`, `Conectadas`, and `Todas` views plus client-side search, 16 category filters with counts, and incremental rendering for large catalogs;
- categories are inferred from verified slugs and Composio descriptions because the CLI catalog does not expose an official category field; every toolkit falls back safely to `Otros`;
- one cached `composio connections list` call supplies all statuses, avoiding one high-memory CLI process per toolkit;
- failed status refreshes are negatively cached for 30 seconds so concurrent callers do not create a sequential retry storm while Composio is unavailable;
- no endpoint for reading mail, pages, calendars, or executing mutating tools;
- a random `MINIAPP_ACCESS_TOKEN` protects the page and API;
- authorization URLs must use `https://connect.composio.dev/`;
- request logs omit the access token embedded in the app path;
- security headers and a restrictive CSP are enabled.

Treat the capability URL as sensitive. Rotate it if shared accidentally. For production, replace capability-token authentication with Telegram `initData` validation as described in `references/setup.md`.

## Workflow

### 1. Verify prerequisites

Run:

```bash
command -v composio
composio whoami
python3 --version
```

If Composio is not authenticated, initiate human login without exposing credentials:

```bash
composio login --no-wait --no-skill-install
composio login --poll --no-skill-install
```

Completion criterion: `composio whoami` exits 0 and reports an authenticated account.

### 2. Install the Mini App files

Copy these files from the skill into a writable deployment directory:

```text
scripts/server.py  -> server.py
assets/index.html  -> index.html
assets/app.js      -> app.js
templates/env.example -> .env.example
```

Do not copy tokens or local Composio state. Completion criterion: all three runtime files exist in the same directory.

### 3. Generate runtime configuration

Generate a fresh capability token locally:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(24))'
```

Set it only in the process environment or a secret manager:

```bash
export MINIAPP_ACCESS_TOKEN='[REDACTED]'
export MINIAPP_HOST='127.0.0.1'
export MINIAPP_PORT='49234'
```

Completion criterion: the real token is absent from source files, Git history, logs, and chat transcripts.

### 4. Start and test locally

```bash
python3 server.py
```

In another shell:

```bash
curl -fsS http://127.0.0.1:49234/health
curl -fsS -H "X-Miniapp-Token: $MINIAPP_ACCESS_TOKEN" \
  http://127.0.0.1:49234/api/status
```

Expected status payload contains a large live catalog, an eight-item recommended subset, and connection states. An unauthenticated request to `/api/status` must return HTTP 401.

### 5. Expose HTTPS

For a disposable prototype:

```bash
cloudflared tunnel --protocol http2 --url http://127.0.0.1:49234 --no-autoupdate
```

Build the Mini App URL as:

```text
https://<generated-host>/app/<MINIAPP_ACCESS_TOKEN>
```

Quick tunnels have no uptime guarantee. For persistent use, deploy behind a named tunnel or another stable HTTPS service.

Completion criterion: `/health`, the protected page, `/app.js`, and authenticated `/api/status` all return HTTP 200 over HTTPS.

### 5b. Deploy persistently on a Hostinger-managed VPS domain

For a stable deployment, do not run the Mini App as an ad-hoc shell process:

1. Create a dedicated system user with a private home under `/var/lib`.
2. Install the app under `/opt/<service-name>` and the Composio executable in a system path.
3. Copy only the minimum Composio CLI state (`user_data.json` and `config.json`) into the service user's private `.composio` directory with mode `0600`.
4. Store `MINIAPP_ACCESS_TOKEN`, `HOME`, host, port, and `PATH` in a root-owned `0600` environment file.
5. Install the hardened systemd unit from `templates/miniapp.service` after replacing placeholders.
6. Add or update the Hostinger DNS `A` record for the subdomain so it targets the VPS public IPv4 address. Validate the DNS operation before applying it and preserve unrelated records.
7. Install the Caddy site from `templates/site.caddy`, validate the complete Caddy configuration, then reload Caddy.
8. Verify public DNS through at least two independent resolvers, confirm the TLS SAN, and test authenticated and unauthenticated API behavior.

Use `--protocol http2` only for a temporary Cloudflare tunnel; it is not needed after the stable domain points directly at Caddy.

Completion criterion: the systemd service and Caddy are active, two resolvers return the VPS address, TLS covers the exact hostname, the protected page returns 200, unauthenticated status returns 401, and authenticated status returns all toolkits.

### 6. Configure Telegram

Use BotFather to set the bot menu button or create a Web App using the HTTPS URL. Open the app from inside Telegram and verify that Telegram theme variables apply.

Never put a Telegram bot token in frontend JavaScript. See `references/setup.md` for production `initData` verification and identity mapping.

### 7. Verify connection flow

From the Mini App:

1. Tap a disconnected or expired service.
2. Confirm the browser opens a URL under `connect.composio.dev`.
3. Finish provider authorization.
4. Return to Telegram.
5. Refresh until the service displays `Conectado`.

Then verify read-only access with the smallest available tool. Do not send email, write Notion content, or create/modify/delete calendar events without explicit user confirmation.

## Toolkit Slugs

| UI label | Composio toolkit slug |
|---|---|
| Gmail | `gmail` |
| Notion | `notion` |
| Google Calendar | `googlecalendar` |

Do not use `google_calendar`; current Composio discovery returns `googlecalendar`.

## Zernio Social Integrations Module

The same Mini App now exposes a separate **Redes sociales · Zernio** tab. Do not merge Zernio account state with Composio toolkit state.

Server-side requirements:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_ALLOWED_USERS
ZERNIO_API_KEY
ZERNIO_WEBHOOK_SECRET
INTEGRATIONS_DB_PATH=/var/lib/softvibes-miniapp/integrations.db
PUBLIC_BASE_URL=https://auth.softvibes.art
```

Security and identity:

- Zernio routes require Telegram `initData` verified with HMAC-SHA256, age checking, and a non-empty allowlist.
- Each verified Telegram user maps to one immutable Zernio profile in SQLite.
- OAuth callbacks use a random, expiring, single-use state and reconcile success against Zernio's accounts API.
- Webhooks validate `X-Zernio-Signature` against the unmodified body and deduplicate `payload.id`.
- Never store social OAuth tokens locally; Zernio owns provider authorization.

Production routes:

```text
GET  /api/zernio/status
POST /api/zernio/connect
POST /api/zernio/telegram/start
POST /api/zernio/telegram/check
GET  /integrations/zernio/callback
POST /webhooks/zernio
```

`integratevibes/` under `scripts/` contains the reusable backend package required by `server.py`. Keep it synchronized when transferring the skill.

## Transfer to Another Hermes Profile

Copy the entire skill directory to the target profile's skill directory, preserving the name:

```text
<target-profile-skills>/integrations/composio-telegram-miniapp/
```

Start a new Hermes session in the target profile so skill discovery refreshes. Authenticate Composio separately in that profile or runtime environment; authentication is not part of the bundle.

Completion criterion: the target profile can load `composio-telegram-miniapp`, all linked files resolve, and no secret files were transferred.

## Common Pitfalls

1. **Embedding live tokens in the skill.** Use environment variables; package only `.env.example`.
2. **Using `google_calendar`.** The expected slug is `googlecalendar`.
3. **Inline JavaScript blocked by CSP.** Keep runtime JavaScript in `app.js` and serve it with `application/javascript`.
4. **Rendering the full catalog at once.** Keep incremental rendering (`PAGE_SIZE`) and “Mostrar más”; hundreds of mobile cards should not enter the DOM simultaneously.
5. **Catalog process pressure.** Cache the live toolkit list for one hour and serialize refreshes; the Composio CLI can consume significant memory.
6. **Quick Tunnel instability.** Force `--protocol http2`; use a named tunnel or Caddy on a stable domain for production.
7. **Running the persistent service as root.** Prefer a dedicated system user and copy only the minimum Composio CLI state into its private home.
8. **Reloading Caddy before DNS exists.** Validate and create the Hostinger record first; Caddy can then complete HTTP-01 issuance without repeated failures.
9. **Assuming CLI login links provider accounts.** `composio whoami` verifies Composio login only. Each toolkit still needs its own link flow.
10. **Treating expired as active.** Only `ACTIVE` means connected; `INITIALIZING`/`PENDING` mean pending and other existing states render expired.
11. **Trusting frontend Telegram identity.** Production backends must verify signed `initData`; never trust a user ID sent as plain JSON.

## Verification Checklist

- [ ] `composio whoami` exits 0
- [ ] `/health` returns HTTP 200
- [ ] protected Mini App page returns HTTP 200
- [ ] `/app.js` returns JavaScript
- [ ] unauthenticated `/api/status` returns HTTP 401
- [ ] authenticated `/api/status` returns the live catalog and the recommended subset
- [ ] `Recomendadas`, `Conectadas`, and `Todas` render correctly
- [ ] all returned toolkits have one of the stable category values and category counts sum to `total`
- [ ] category filters combine correctly with view and search filters
- [ ] search scans the full loaded catalog and “Mostrar más” paginates large result sets
- [ ] generated authorization links use `https://connect.composio.dev/`
- [ ] mobile viewport renders without clipping
- [ ] no secrets exist in skill files or transfer bundle
- [ ] Telegram bot token remains server-side
- [ ] mutating app actions remain outside this connector UI
