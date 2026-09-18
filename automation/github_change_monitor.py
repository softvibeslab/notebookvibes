#!/usr/bin/env python3
"""Monitor de cambios GitHub; solo lectura y salida vacía sin novedades."""
from __future__ import annotations
import json, os, re, subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
TZ=ZoneInfo(os.getenv('NOTEBOOKVIBES_TIMEZONE', 'America/Cancun')); NOW=datetime.now(TZ); DRY=os.getenv('GITHUB_MONITOR_DRY_RUN','0')=='1'
STATE=Path(os.getenv('GITHUB_MONITOR_STATE', str(Path.home()/'.local/state/notebookvibes/github_monitor_state.json')))
def clean(x,n=150):
 s=re.sub(r'\s+',' ',str(x or '')).strip();return s if len(s)<=n else s[:n-1]+'…'
def call(slug,payload,timeout=55):
 try:
  p=subprocess.run(['composio','execute',slug,'-d',json.dumps(payload,ensure_ascii=False)],capture_output=True,text=True,timeout=timeout)
  if p.returncode:return {'_error':clean(p.stderr or p.stdout,240)}
  d=json.loads(p.stdout)
  if isinstance(d,dict) and (d.get('successful') is False or d.get('error')):return {'_error':clean(d.get('error') or 'successful=false',240)}
  return d
 except Exception as e:return {'_error':clean(e,240)}
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def load():
 try:return json.loads(STATE.read_text())
 except:return {}
def save(x):
 STATE.parent.mkdir(parents=True,exist_ok=True);STATE.write_text(json.dumps(x,indent=2))

resp=call('GITHUB_SEARCH_ISSUES_AND_PULL_REQUESTS',{'q':f'user:softvibeslab updated:>={(NOW-timedelta(days=2)).date().isoformat()}','page':1,'sort':'updated','order':'desc','per_page':30,'response_detail':'full'})
if resp.get('_error'):
 print(f"# Monitor GitHub\n\n- GitHub no respondió: {resp['_error']}");raise SystemExit
items=[];seen=set()
for o in walk(resp.get('data',resp)):
 title=o.get('title');url=o.get('html_url')
 if not title or not url or 'api.github.com' in str(url) or url in seen:continue
 seen.add(url);repo=''
 ru=o.get('repository_url') or ''
 if ru:repo=ru.rstrip('/').split('/')[-1]
 labels=[]
 for lab in o.get('labels') or []:
  labels.append(lab.get('name') if isinstance(lab,dict) else str(lab))
 items.append({'title':clean(title,120),'url':url,'updated':o.get('updated_at') or o.get('created_at') or '', 'state':o.get('state') or '', 'pr':bool(o.get('pull_request')),'repo':repo,'labels':labels})
items.sort(key=lambda x:x['updated'],reverse=True)
state=load();changed=[]
for x in items:
 fingerprint=f"{x['updated']}|{x['state']}"
 if DRY or state.get(x['url'])!=fingerprint:changed.append(x)
 state[x['url']]=fingerprint
# Conservar solo elementos aún visibles en la consulta reciente.
state={k:v for k,v in state.items() if k in {x['url'] for x in items}}
if not DRY:save(state)
if not changed:raise SystemExit
print('# Monitor GitHub — novedades\n')
print(f"**Corte:** {NOW.strftime('%Y-%m-%d %H:%M')} · **Cuenta:** softvibeslab · **Modo:** solo lectura\n")
for x in changed[:15]:
 kind='PR' if x['pr'] else 'Issue';repo=f" · {x['repo']}" if x['repo'] else ''
 labs=f" · etiquetas: {', '.join(x['labels'][:4])}" if x['labels'] else ''
 print(f"- **{kind}: {x['title']}** · {x['state']}{repo}{labs}")
print('\n## Evaluación')
open_items=[x for x in changed if x['state']=='open']
print(f"- Cambios detectados: **{len(changed)}**; abiertos: **{len(open_items)}**.")
print('- Priorizar PR con pruebas fallidas, issues bloqueantes y elementos sin responsable antes de iniciar trabajo nuevo.')
print('- Sugerencia para Notion: crear o actualizar una tarea solo después de aprobarla en Telegram.')
print('\n**Control:** no se modificó GitHub ni Notion.')
