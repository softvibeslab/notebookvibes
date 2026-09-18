#!/usr/bin/env python3
"""Control Tower semanal: reúne brief, reuniones, Instagram, GitHub y conexiones."""
from __future__ import annotations
import json, os, re, subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
TZ=ZoneInfo(os.getenv('NOTEBOOKVIBES_TIMEZONE', 'America/Cancun')); NOW=datetime.now(TZ)
BASE=Path(os.getenv('NOTEBOOKVIBES_AUTOMATION_DIR', str(Path(__file__).resolve().parent)))

def run_script(name,env=None,timeout=150):
 e=os.environ.copy();e.update(env or {})
 try:
  p=subprocess.run(['python',str(BASE/name)],capture_output=True,text=True,timeout=timeout,env=e)
  if p.returncode:return f"- Error en {name}: {(p.stderr or p.stdout)[:180]}"
  return p.stdout.strip()
 except Exception as ex:return f"- Error en {name}: {ex}"
def section(text,title,next_title=None,max_lines=12):
 marker=f'## {title}';i=text.find(marker)
 if i<0:return ''
 chunk=text[i+len(marker):]
 if next_title:
  j=chunk.find(f'## {next_title}')
  if j>=0:chunk=chunk[:j]
 lines=[x for x in chunk.strip().splitlines() if x.strip()]
 return '\n'.join(lines[:max_lines])
def connections():
 try:
  p=subprocess.run(['composio','connections','list'],capture_output=True,text=True,timeout=60)
  d=json.loads(p.stdout);active=[];expired=[]
  for kit,items in d.items():
   statuses={str(x.get('status','')).upper() for x in items if isinstance(x,dict)}
   if 'ACTIVE' in statuses:active.append(kit)
   elif statuses:expired.append(kit)
  return active,expired
 except Exception:return [],[]

# Composio CLI comparte estado local; las consultas deliberadamente se
# serializan para evitar contención entre varios procesos concurrentes.
data={
 'brief':run_script('brief_exec_collect.py'),
 'meet':run_script('meeting_assistant.py',{'MEETING_LOOKAHEAD_MINUTES':'1440','MEETING_DRY_RUN':'1'}),
 'ig':run_script('instagram_weekly_radar.py'),
 'gh':run_script('github_change_monitor.py',{'GITHUB_MONITOR_DRY_RUN':'1'}),
 'conn':connections(),
}

brief=data['brief'];meet=data['meet'];ig=data['ig'];gh=data['gh'];active,expired=data['conn']
parts=[f"# Control Tower integral — {NOW.date().isoformat()}\n",f"**Corte:** {NOW.strftime('%H:%M')} · **Zona:** America/Cancun · **Modo:** solo lectura\n"]
parts.append('## Prioridades ejecutivas\n'+(section(brief,'Tres prioridades','Agenda de hoy y mañana',5) or '- No se recuperaron prioridades.'))
meeting_block=''
if meet.startswith('# Asistente'):
 meeting_block='\n'.join([x for x in meet.splitlines() if x.strip() and not x.startswith('# Asistente')][:18])
if not meeting_block:
 meeting_block=section(brief,'Agenda de hoy y mañana','Correos a atender',8) or '- No hay reuniones próximas verificables.'
parts.append('## Agenda e inteligencia de reuniones\n'+meeting_block)
mail=section(brief,'Correos a atender','Alertas técnicas',7)
parts.append('## Bandeja prioritaria\n'+(mail or '- Sin señales verificables.'))
ig_lines=[]
for sec,nxt,limit in [('Estado de cuenta','Indicadores de 7 días',5),('Indicadores de 7 días','Contenido publicado y rendimiento',12),('Recomendaciones','Límites',5)]:
 x=section(ig,sec,nxt,limit)
 if x:ig_lines.append(x)
parts.append('## Instagram — crecimiento y contenido\n'+('\n'.join(ig_lines) or '- Radar no disponible.'))
gh_lines=[]
for line in gh.splitlines():
 if line.startswith('- **') or line.startswith('- Cambios') or line.startswith('- Priorizar'):gh_lines.append(line)
parts.append('## GitHub — entrega técnica\n'+('\n'.join(gh_lines[:10]) or '- Sin cambios verificables.'))
parts.append('## Salud de integraciones\n- Activas: '+(', '.join(sorted(active)) if active else 'no verificadas')+'\n- Sin conexión activa: '+(', '.join(sorted(expired)) if expired else 'ninguna detectada'))
parts.append('## Control y aprobación\n- No se enviaron correos ni se modificaron Calendar, Notion, GitHub o Instagram.\n- Cualquier escritura, publicación o cambio de campaña requiere aprobación explícita en Telegram.\n- Drive continúa sujeto a su cuota de almacenamiento; Meta Ads no se considera operativo mientras no exista conexión activa.')
out='\n\n'.join(parts)
# Telegram tolera mensajes mayores, pero mantener el tablero ejecutivo compacto.
if len(out)>7000:out=out[:6950]+'\n\n_[Salida truncada para mantener el informe legible.]_'
print(out)
