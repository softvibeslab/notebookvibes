# Operación

## Pruebas

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q tools integratevibes composio-telegram-miniapp automation
node --check composio-telegram-miniapp/app.js
git diff --check
```

## MCP

Configura `OPEN_NOTEBOOK_URL` y `OPEN_NOTEBOOK_PASSWORD` en el entorno privado. Inicia manualmente:

```bash
python tools/open_notebook_mcp.py
python tools/research_web_mcp.py
```

En Hermes, registra ambos servidores con rutas absolutas según `profile/config.example.yaml`.

## Mini App

```bash
export MINIAPP_ACCESS_TOKEN='valor-privado'
export MINIAPP_HOST='127.0.0.1'
export MINIAPP_PORT='4192'
python composio-telegram-miniapp/server.py
```

Prueba `/health` y confirma que `/api/status` sin token devuelve 401. Para producción usa el ejemplo systemd, un usuario dedicado, un environment file `0600`, Caddy y HTTPS.

## Rollback

Conserva despliegues como releases o directorios versionados fuera del árbol servido. No subas copias de `/etc`, bases de datos ni backups al repositorio.
