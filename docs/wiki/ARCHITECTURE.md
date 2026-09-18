# Arquitectura

```text
Usuario (CLI / Telegram)
        |
        v
Hermes profile: notebookllm
  |-- SOUL + skills + config
  |-- research-web MCP --------> web pública (SSRF + robots)
  |-- open-notebook MCP -------> Open Notebook API
  |                                |-- listar/estado: lectura
  |                                `-- agregar: aprobación explícita
  |-- automatizaciones --------> Composio (solo lectura)
  `-- Telegram Mini App
         |-- Composio: herramientas/documentos
         `-- Zernio: cuentas sociales
                |-- initData HMAC + allowlist
                |-- sesiones efímeras con hash
                `-- SQLite sin tokens OAuth
```

## Límites de confianza

- El navegador no decide identidad: el backend verifica `Telegram.WebApp.initData`.
- Los secretos solo entran mediante variables de entorno o gestores de secretos.
- Open Notebook no recibe contenido por iniciativa del agente: la mutación exige aprobación exacta.
- La extracción web rechaza destinos no públicos, credenciales embebidas y redirecciones inseguras.
- Composio y Zernio no comparten credenciales ni modelo de estado.

## Componentes

### Herramientas MCP

`tools/open_notebook_client.py` implementa el cliente HTTP sin dependencias pesadas. `tools/open_notebook_mcp.py` expone operaciones tipadas. `tools/research_web.py` valida URL/DNS, respeta robots.txt, limita descargas y extrae HTML/PDF. `tools/research_web_mcp.py` expone esas capacidades.

### Mini App

`composio-telegram-miniapp/server.py` sirve frontend/API, consulta el catálogo de Composio y delega Zernio en `integratevibes/`. El frontend conserva sesiones efímeras solo en memoria.

### Automatización

Los scripts de `automation/` generan texto determinista a partir de fuentes conectadas. No escriben correo, calendario, Notion, GitHub ni Instagram.
