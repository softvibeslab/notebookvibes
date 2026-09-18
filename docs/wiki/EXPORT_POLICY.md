# Política de exportación del perfil

## Incluido

- identidad y metodología (`SOUL.md`);
- configuración reproducible con placeholders;
- skills propios relevantes y sus recursos (los seis personalizados detectados fuera del catálogo bundled);
- código MCP, Mini App, integraciones y pruebas;
- automatizaciones de solo lectura;
- documentación técnica y un dashboard de ejemplo saneado;
- plantillas de despliegue sin secretos.

## Excluido deliberadamente

- `.env`, `auth.json`, tokens MCP y credenciales;
- `config.yaml` vivo con IDs de Telegram, canales y rutas locales;
- memorias de usuario y del agente;
- sesiones, historial, logs y response stores;
- bases SQLite, locks, PID, heartbeats, estado de gateway y cron;
- catálogo/cache de modelos, npm/uv caches y binarios;
- outputs privados de Instagram/Notion, CSV, JSON, capturas y archivos comprimidos;
- skills generales de terceros instalados por Hermes.

## Razón

“Subir todo” se interpreta como preservar todo el código, estructura y conocimiento reusable que sea seguro y legal publicar, no como divulgar secretos, datos personales, estado efímero o dependencias descargables. Esta política hace explícita esa frontera.
