#!/usr/bin/env python3
"""Asistente de reuniones de solo lectura; salida vacía si no hay reunión próxima."""
from __future__ import annotations
import json, os, re, subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ=ZoneInfo(os.getenv('NOTEBOOKVIBES_TIMEZONE', 'America/Cancun')); NOW=datetime.now(TZ)
LOOKAHEAD=int(os.getenv('MEETING_LOOKAHEAD_MINUTES','75'))
DRY=os.getenv('MEETING_DRY_RUN','0')=='1'
STATE=Path(os.getenv('MEETING_ASSISTANT_STATE', str(Path.home()/'.local/state/notebookvibes/meeting_assistant_state.json')))

def clean(x,n=140):
    s=re.sub(r'\s+',' ',str(x or '')).strip(); return s if len(s)<=n else s[:n-1]+'…'
def call(slug,payload,timeout=50):
    try:
        p=subprocess.run(['composio','execute',slug,'-d',json.dumps(payload,ensure_ascii=False)],capture_output=True,text=True,timeout=timeout)
        if p.returncode: return {'_error':clean(p.stderr or p.stdout,240)}
        d=json.loads(p.stdout)
        if isinstance(d,dict) and (d.get('successful') is False or d.get('error')): return {'_error':clean(d.get('error') or 'successful=false',240)}
        return d
    except Exception as e: return {'_error':clean(e,240)}
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)
def start_of(o):
    s=o.get('start')
    if isinstance(s,dict): return s.get('dateTime') or s.get('date') or ''
    return s or o.get('start_time') or ''
def parse_dt(s):
    try:
        if 'T' not in s: return None
        return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(TZ)
    except Exception: return None

def load_state():
    try: return json.loads(STATE.read_text())
    except Exception: return {}
def save_state(d):
    STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(d,ensure_ascii=False,indent=2))

end=NOW+timedelta(minutes=LOOKAHEAD)
cal=call('GOOGLECALENDAR_EVENTS_LIST_ALL_CALENDARS',{
 'q':'','time_min':NOW.isoformat(),'time_max':end.isoformat(),'event_types':[],'calendar_ids':[],
 'show_deleted':False,'single_events':True,'response_detail':'full','max_results_per_calendar':20})
if cal.get('_error'):
    print(f"# Asistente de reuniones\n\n- Calendar no respondió: {cal['_error']}")
    raise SystemExit

state=load_state(); cutoff=(NOW-timedelta(days=7)).isoformat()
state={k:v for k,v in state.items() if isinstance(v,str) and v>=cutoff}
events=[]; seen=set()
for o in walk(cal.get('data',cal)):
    title=o.get('summary') or o.get('title'); raw=start_of(o); dt=parse_dt(raw)
    if not title or not dt or not (NOW-timedelta(minutes=5)<=dt<=end): continue
    # El mismo evento puede aparecer en varios calendarios accesibles.
    key=f'{str(title).strip().casefold()}|{dt.isoformat()}'
    if key in seen or (key in state and not DRY): continue
    seen.add(key)
    events.append((dt,key,clean(title,110),o))
events.sort(key=lambda x:x[0])
if not events: raise SystemExit

print('# Asistente de reuniones\n')
print(f"**Ventana:** {NOW.strftime('%Y-%m-%d %H:%M')}–{end.strftime('%Y-%m-%d %H:%M')} · **Zona:** America/Cancun · **Modo:** solo lectura\n")
for dt,key,title,o in events:
    # Una palabra significativa ayuda a buscar contexto sin exponer todo el calendario.
    words=[w for w in re.findall(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_-]+',title) if len(w)>=4 and w.lower() not in {'reunión','meeting','daily','dayli'}]
    term=' '.join(words[:4]) or title
    mail=call('GMAIL_FETCH_EMAILS',{'query':f'newer_than:30d "{term}"','user_id':'me','verbose':False,'ids_only':False,'label_ids':[],'page_token':'','max_results':5,'include_payload':False,'include_spam_trash':False})
    notion=call('NOTION_SEARCH_NOTION_PAGE',{'query':term[:80],'direction':'descending','page_size':5,'timestamp':'last_edited_time','filter_value':'page','start_cursor':'','filter_property':'object','filter_properties':[]})
    mail_subjects=[]
    if not mail.get('_error'):
        for x in walk(mail.get('data',mail)):
            if x.get('subject') and x.get('subject') not in mail_subjects: mail_subjects.append(clean(x['subject'],100))
    notion_titles=[]
    if not notion.get('_error'):
        for x in walk(notion.get('data',notion)):
            t=x.get('title')
            if isinstance(t,str) and t and t not in notion_titles: notion_titles.append(clean(t,100))
    print(f"## {dt.strftime('%H:%M')} — {title}")
    print(f"- **Faltan:** {max(0,int((dt-NOW).total_seconds()//60))} minutos")
    print(f"- **Objetivo sugerido:** confirmar resultado esperado, decisiones pendientes y responsable del siguiente paso.")
    print('- **Contexto Gmail:** '+('; '.join(mail_subjects[:3]) if mail_subjects else 'sin coincidencias verificables'))
    print('- **Contexto Notion:** '+('; '.join(notion_titles[:3]) if notion_titles else 'sin coincidencias verificables'))
    print('- **Preguntas:** ¿qué decisión debe salir hoy? ¿qué bloquea el avance? ¿quién hace qué y para cuándo?\n')
    state[key]=NOW.isoformat()
if not DRY: save_state(state)
print('**Control:** no se modificó Calendar, Gmail ni Notion.')
