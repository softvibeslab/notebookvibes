# Deployment and Telegram setup

## Prototype deployment

1. Authenticate the local Composio CLI with a human account.
2. Copy `server.py`, `index.html`, and `app.js` to one directory.
3. Generate a fresh random `MINIAPP_ACCESS_TOKEN` and export it.
4. Start `python3 server.py`.
5. Verify local health and authenticated status endpoints.
6. Start `cloudflared tunnel --protocol http2 --url http://127.0.0.1:49234 --no-autoupdate`.
7. Use `https://<host>/app/<token>` as the Telegram Mini App URL.

Quick tunnels are prototypes only. They can change URL or stop without notice.

## BotFather configuration

In Telegram, open BotFather and configure the bot that should launch the Mini App:

1. Use `/setmenubutton` and select the bot.
2. Set a concise label such as `Conectar apps`.
3. Paste the complete HTTPS Mini App URL.
4. Open the bot, tap the menu button, and verify the page loads inside Telegram.

If using a named Web App instead, follow BotFather's `/newapp` flow and use the same HTTPS URL.

Do not paste the Telegram bot token into BotFather fields intended for URLs, into frontend code, or into the skill.

## Production authentication with Telegram initData

The bundled capability-token mode is suitable for a single-user prototype. A multi-user deployment must validate Telegram `initData` server-side.

Required flow:

1. Frontend sends `Telegram.WebApp.initData` to the backend over HTTPS.
2. Backend parses fields except `hash` and sorts them as `key=value` joined with `\n`.
3. Backend computes the Web App secret key as HMAC-SHA256 with key `WebAppData` and message equal to the bot token.
4. Backend computes HMAC-SHA256 of the data-check string with that secret key.
5. Backend compares the hexadecimal result to `hash` using constant-time comparison.
6. Backend rejects stale `auth_date` values.
7. Backend extracts the verified Telegram user ID and maps it to a separate Composio identity.

Never trust a Telegram user ID supplied as plain JSON. Never send the bot token to the browser.

## Composio identity isolation

For multiple users, use this mapping:

```text
verified Telegram user ID
  -> internal user record
  -> Composio external user ID
  -> that user's connected accounts
```

Do not share one global Gmail, Notion, or Google Calendar connection across Telegram users unless the product explicitly represents a shared service account and the user has approved that model.

## Permission posture

Start read-only where the provider and Composio auth configuration allow it:

- Gmail: profile, labels, search, and message reading before send/reply/delete.
- Notion: only pages and databases explicitly shared with the integration; read before write.
- Google Calendar: list calendars/events before create/update/delete.

Require explicit human confirmation for sending mail, editing Notion, and creating, modifying, or deleting calendar events.

## Revocation

Disconnect provider access from the Composio dashboard and, when needed, from the provider's own connected-app settings. Rotate `MINIAPP_ACCESS_TOKEN` whenever its capability URL may have leaked.
