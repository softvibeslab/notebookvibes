# Notebookvibes

Repositorio portable del perfil Hermes `notebookllm`: investigación profunda, puente MCP hacia Open Notebook, búsqueda web pública con controles SSRF/robots, Telegram Mini App para integraciones, automatizaciones de solo lectura y ejemplos de dashboards.

## Qué contiene

- `profile/`: identidad del agente, configuración saneada y skills propios relevantes.
- `tools/`: servidores MCP `open-notebook` y `research-web`.
- `composio-telegram-miniapp/`: frontend y backend de la Mini App.
- `integratevibes/`: autenticación Telegram, persistencia y cliente/orquestación Zernio.
- `automation/`: briefs, monitor GitHub, asistente de reuniones y radar de Instagram en modo lectura.
- `dashboards/`: artefactos HTML publicables sin datos privados.
- `docs/wiki/`: arquitectura, seguridad, operación y política de exportación.
- `tests/`: pruebas unitarias y HTTP.
- `deployment/`: ejemplos de systemd y Caddy sin secretos.

Consulta `docs/wiki/README.md` para el mapa completo.

## Inicio rápido

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
node --check composio-telegram-miniapp/app.js
```

## Configuración del perfil

1. Copia `profile/config.example.yaml` a la configuración del perfil mediante `hermes config set`; no reemplaces manualmente un `config.yaml` activo.
2. Copia `.env.example` a un archivo de entorno privado y completa los valores fuera de Git.
3. Configura los servidores MCP usando rutas absolutas del checkout.
4. Reinicia la sesión de Hermes para recargar perfil, skills y MCP.

## Principios de seguridad

- Ningún secreto, token OAuth, sesión, base de datos, memoria personal, log o salida de cron pertenece al repositorio.
- Las escrituras en Open Notebook requieren `approved=true` y una aprobación humana explícita para el elemento y notebook exactos.
- La Mini App valida Telegram `initData`, usa allowlist y separa los proveedores Composio y Zernio.
- Las automatizaciones incluidas son de solo lectura; cualquier mutación externa requiere un flujo separado de aprobación.

## Estado de los datos

Este repositorio contiene código, plantillas, documentación y ejemplos saneados. Los informes reales de Instagram/Notion, IDs internos de notebooks, memorias, cron outputs, credenciales y bases de datos fueron excluidos deliberadamente.

## Licencia

MIT. Consulta `LICENSE`.
