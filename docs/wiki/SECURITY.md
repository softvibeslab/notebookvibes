# Seguridad y privacidad

## Nunca versionar

- `.env`, API keys, bot tokens, OAuth, cookies y credenciales.
- `auth.json`, `mcp-tokens/`, estado de Composio o Zernio.
- sesiones, memorias de usuario, logs, respuestas del modelo y bases SQLite.
- outputs de cron, caches, archivos temporales o backups de producción.
- IDs reales de Telegram, chats, notebooks u objetos internos.
- datasets de audiencia, correos, calendarios o páginas privadas.

## Gates de autorización

`add_source_url` y `add_research_digest` exigen `approved=True`. La aprobación debe mencionar el elemento exacto y el notebook de destino en la conversación actual.

## Telegram

- Verificar HMAC-SHA256 y antigüedad de `initData`.
- Exigir una allowlist no vacía.
- No aceptar un user ID enviado como JSON sin firma.
- Mantener `TELEGRAM_BOT_TOKEN` solo en el backend.

## Web

- Solo URLs HTTP(S) absolutas.
- Bloquear usuario/contraseña embebidos.
- Resolver DNS y rechazar IP privadas/no globales.
- Validar cada redirección.
- Limitar bytes descargados y respetar `robots.txt`.

## Antes de publicar

```bash
git status --short
git diff --check
git grep -nE '(api[_-]?key|secret|token|password)[[:space:]]*[:=][[:space:]]*[^[:space:]${}<]+'
```

La última búsqueda genera falsos positivos en pruebas y nombres de variables; cada coincidencia debe revisarse manualmente.
