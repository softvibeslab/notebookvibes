# Notebookvibes agent guide

## Alcance

Este repositorio exporta de forma portable el perfil Hermes `notebookllm`, sus MCP, la Mini App y documentación asociada.

## Reglas

- Nunca agregues `.env`, tokens, credenciales, cookies, sesiones, memorias, logs, bases SQLite ni salidas de cron.
- Usa valores ficticios en ejemplos y pruebas.
- Mantén la aprobación explícita antes de cualquier escritura en Open Notebook.
- La Mini App debe verificar Telegram `initData` del lado servidor y fallar cerrada si la allowlist está vacía.
- Composio y Zernio conservan estado, credenciales y rutas separados.
- No conviertas datos de audiencia agregados en perfiles individuales.
- Ejecuta antes de entregar:

```bash
python -m unittest discover -s tests -v
python -m compileall -q tools integratevibes composio-telegram-miniapp automation
node --check composio-telegram-miniapp/app.js
git diff --check
```
