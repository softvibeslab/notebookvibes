# Composio: Hermes, Connect MCP, and SDK sessions

Validated against official Composio documentation on 2026-09-16.

## Choose the route

### Existing Hermes agent: Composio Connect

Use the shared hosted MCP endpoint:

```text
https://connect.composio.dev/mcp
```

Composio Connect exposes seven meta-tools rather than thousands of app schemas. The agent discovers apps/tools, generates authorization links on demand, and executes across connected apps. Downstream app OAuth remains separate from Composio authorization.

Configure with Hermes:

```bash
hermes mcp list
hermes mcp add composio \
  --url https://connect.composio.dev/mcp \
  --auth oauth \
  --connect-timeout 90
```

For a headless Hermes process, run the add command in a tracked background PTY. Hermes prints an authorization URL and waits for either its local callback listener or a pasted redirect URL. If the user's browser redirects to `http://127.0.0.1:<port>/callback?...` on their own device and cannot load, have them copy the complete address-bar URL. Submit it directly to the waiting process without quoting it back.

### Timeout-safe OAuth recovery

`hermes mcp add` can finish its connection timeout and advance to `Save config anyway?` while the user is still authorizing in a browser. Before submitting any callback, poll the tracked PTY and verify that the matching callback prompt is still active.

If the prompt has already advanced:

1. Do **not** submit the stale callback URL.
2. Save the server only as a disabled/pending config if needed so the login command can address it; do not call this success.
3. Start `hermes mcp login composio` in a fresh tracked background PTY.
4. Relay the newly generated authorization URL.
5. Submit only the callback whose port/state correspond to that active login process.
6. Wait for explicit login completion before sending any other answer.
7. Run `hermes mcp test composio`, then verify a harmless read-only tool call.

A callback pasted after the CLI has moved to a yes/no save prompt can be consumed by the wrong interaction and leave no cached token. Avoid this race by checking the live prompt immediately before submission.

Then verify:

```bash
hermes mcp list
hermes mcp test composio
```

Finally run a harmless read-only request through a discovered Composio tool. Do not declare success before the test and live call both succeed.

## Composio CLI login is a different route

The current Composio docs show this for Hermes:

```bash
curl -fsSL https://composio.dev/install | sh
composio login
```

The CLI is useful for direct `search`, `execute`, `link`, `proxy`, and `run` workflows. It is not required when Hermes connects directly to Composio Connect over OAuth MCP.

When a human is available, use the standard human login flow. In Composio CLI 0.4.1, `composio login --help` does not expose an `--agent` option; do not recommend it. For a headless process, use the documented `--no-wait` plus `--poll` flow below and verify the exact flags against the installed CLI.

### Robust headless CLI login

When the remote-MCP callback cannot be completed reliably within the active Hermes prompt, use the official CLI route as a functional fallback rather than repeatedly issuing short-lived callbacks:

```bash
composio login --no-wait --no-skill-install
# Give the printed dashboard URL to the human, then immediately run:
composio login --poll --no-skill-install
composio whoami
```

Run `--poll` as a tracked background process; it caches the login key and waits for authorization without requiring the user to paste a loopback callback. Completion requires exit code 0 from polling plus `composio whoami` success. This authenticates the CLI, not the downstream providers.

Discover and verify tools with a public read-only call before linking private applications:

```bash
composio search "list upcoming Google Calendar events" --limit 3
composio execute HACKERNEWS_GET_USER -d '{"username":"pg"}'
```

### Downstream toolkit links

Generate browser links without blocking the agent process:

```bash
composio link gmail --no-wait --no-browser
composio link notion --no-wait --no-browser
composio link googlecalendar --no-wait --no-browser
```

The Google Calendar toolkit slug is `googlecalendar`, not `google_calendar`. Verify each provider independently:

```bash
composio connections list --toolkit gmail
composio connections list --toolkit notion
composio connections list --toolkit googlecalendar
```

Treat only `ACTIVE` as connected. `INITIALIZING`, `PENDING`, or `INITIATED` are pending; expired states require a fresh link. Do not infer downstream authorization from successful `composio whoami`.

### Telegram Mini App connector pattern

For a connector-only Mini App, expose only two backend operations: connection status and fresh link generation. Keep a fixed toolkit allowlist, validate that returned redirects use `https://connect.composio.dev/`, and do not expose generic tool execution. Query independent toolkit statuses concurrently so the UI does not appear frozen.

For a single-user prototype, a rotated capability URL can protect the page. For multi-user production, validate signed Telegram `initData` server-side, reject stale `auth_date`, and map each verified Telegram user ID to an isolated Composio identity. Never trust a frontend-supplied user ID or place the bot token in JavaScript.

Browser hardening notes:

- Put application JavaScript in an external file when CSP omits `'unsafe-inline'` from `script-src`; otherwise the UI remains stuck in its loading state.
- Serve the app, status API, and script from one origin when using `connect-src 'self'`.
- Cloudflare Quick Tunnels are disposable; forcing `--protocol http2` can avoid transient QUIC instability, but a named tunnel or stable HTTPS host is required for production.

## Building an application: SDK session MCP

Use current SDK packages, not legacy `composio-core` on Python. The current Python package is `composio` and requires Python 3.10+.

```python
from composio import Composio

composio = Composio()
session = composio.sessions.create(user_id="stable_user_id", mcp=True)

mcp_url = session.mcp.url
mcp_headers = session.mcp.headers
session_id = session.session_id  # persist and reuse
```

Resume with:

```python
session = composio.use(session_id, mcp=True)
```

Use `session.mcp.url` **and** `session.mcp.headers` in the client. For fixed least-privilege tools, use the direct-tools preset and explicit toolkit/tool allowlists.

MCP trade-offs documented by Composio:

- SDK `beforeExecute`, `afterExecute`, and schema modifiers do not run over hosted MCP.
- Process-local custom tools/toolkits are unavailable through the hosted MCP endpoint.
- Use direct provider integration instead when those hooks or local tools are required.

## Production invariants

- Replace sample `user_123` with a stable application user/workspace identity.
- Persist session IDs rather than creating a session on every turn.
- Scope connected accounts and toolkits per user/tenant.
- Ask for confirmation before create/update/delete actions.
- Verify writes with a follow-up read or provider UI.
- Keep `COMPOSIO_API_KEY`, callback codes, MCP headers, and account IDs out of chat logs and version control.

## Official sources

- Quickstart: https://docs.composio.dev/docs/quickstart
- Composio Connect: https://docs.composio.dev/docs/composio-connect
- Sessions via MCP: https://docs.composio.dev/docs/sessions-via-mcp
- Unattended authentication: https://docs.composio.dev/docs/agent-setup/unattended-authentication
- Repository: https://github.com/ComposioHQ/composio
