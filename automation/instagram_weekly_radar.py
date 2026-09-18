#!/usr/bin/env python3
"""Radar semanal de Instagram Business, exclusivamente de lectura."""
from __future__ import annotations
import concurrent.futures, json, re, subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
TZ=ZoneInfo('America/Cancun'); NOW=datetime.now(TZ); START=NOW-timedelta(days=7)

def clean(x,n=150):
 s=re.sub(r'\s+',' ',str(x or '')).strip(); return s if len(s)<=n else s[:n-1]+'…'
def call(slug,payload,timeout=60):
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
def num(v):
 try:return float(v)
 except:return 0.0
def first_value(o):
 if 'total_value' in o:
  v=o['total_value']; return num(v.get('value') if isinstance(v,dict) else v)
 vals=o.get('values')
 if isinstance(vals,list):return sum(num(x.get('value')) for x in vals if isinstance(x,dict))
 return 0.0

def metrics(resp):
 out={}
 for o in walk(resp.get('data',resp)):
  name=o.get('name')
  if name and ('values' in o or 'total_value' in o):out[str(name)]=first_value(o)
 return out

def media_items(resp):
 found=[]; seen=set()
 for o in walk(resp.get('data',resp)):
  mid=o.get('id'); ts=o.get('timestamp')
  if not mid or not ts or mid in seen:continue
  if not any(k in o for k in ('caption','media_type','permalink','total_like_count','like_count')):continue
  seen.add(mid)
  caption=clean(o.get('caption'),220)
  likes=num(o.get('total_like_count') or o.get('like_count'))
  comments=num(o.get('total_comments_count') or o.get('comments_count'))
  saves=num(o.get('saved_count')); shares=num(o.get('shares_count')); views=num(o.get('total_views_count') or o.get('view_count'))
  score=likes+2*comments+3*saves+2*shares+0.02*views
  found.append({'id':mid,'timestamp':ts,'caption':caption,'type':o.get('media_type') or o.get('media_product_type') or '', 'likes':likes,'comments':comments,'saves':saves,'shares':shares,'views':views,'score':score})
 found.sort(key=lambda x:x['score'],reverse=True);return found

def theme(text):
 t=text.lower()
 groups=[('Tecnología/IA',('program','tecnolog','software','ia ',' ai ','agent','startup','emprend')),
 ('Cerveza/comunidad',('cerveza','beer','beeroffice','tap room','brew')),
 ('Viajes/estilo de vida',('viaje','playa','tulum','cancún','cancun','caribe','vacaciones')),
 ('Cultura/personal',('música','music','cultura','familia','vida','social','causa'))]
 for name,keys in groups:
  if any(k in t for k in keys):return name
 return 'Otros'

profile=call('INSTAGRAM_GET_USER_INFO',{'ig_user_id':'me','fields':'id,username,name,account_type,followers_count,follows_count,media_count','graph_api_version':'v21.0'})
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futs={
  'kpi':pool.submit(call,'INSTAGRAM_GET_USER_INSIGHTS',{'since':int(START.timestamp()),'until':int(NOW.timestamp()),'metric':['views','reach','profile_views','accounts_engaged','total_interactions','likes','comments','shares','saves'],'period':'day','ig_user_id':'me','metric_type':'total_value','graph_api_version':'v21.0'}),
  'growth':pool.submit(call,'INSTAGRAM_GET_USER_INSIGHTS',{'since':int(START.timestamp()),'until':int(NOW.timestamp()),'metric':['follows_and_unfollows'],'period':'day','breakdown':'follow_type','ig_user_id':'me','metric_type':'total_value','graph_api_version':'v21.0'}),
  'media':pool.submit(call,'INSTAGRAM_GET_IG_USER_MEDIA',{'after':'','limit':25,'since':int(START.timestamp()),'until':int(NOW.timestamp()),'before':'','fields':'id,caption,media_type,permalink,timestamp,view_count,reposts_count,saved_count,shares_count,total_like_count,total_comments_count,total_views_count','ig_user_id':'me','graph_api_version':'v21.0','auto_resolve_fb_page_id':True})}
 res={k:f.result() for k,f in futs.items()}

prof={}
for o in walk(profile.get('data',profile)):
 if o.get('username'):
  prof=o;break
m=metrics(res['kpi']); g=metrics(res['growth']); posts=media_items(res['media'])
themes={}
for p in posts: themes[theme(p['caption'])]=themes.get(theme(p['caption']),0)+1
errors={}
for k,v in {'perfil':profile,**res}.items():
 if isinstance(v,dict) and v.get('_error'):errors[k]=v['_error']

print(f"# Radar semanal de Instagram — @{prof.get('username','rogermck')}\n")
print(f"**Periodo:** {START.date().isoformat()} a {NOW.date().isoformat()} · **Zona:** America/Cancun · **Modo:** solo lectura\n")
print('## Estado de cuenta')
print(f"- Seguidores: **{int(num(prof.get('followers_count'))):,}**")
print(f"- Publicaciones acumuladas: **{int(num(prof.get('media_count'))):,}**")
print(f"- Tipo: **{clean(prof.get('account_type') or 'no disponible',40)}**")
print('\n## Indicadores de 7 días')
labels=[('views','Visualizaciones'),('reach','Alcance'),('profile_views','Visitas al perfil'),('accounts_engaged','Cuentas que interactuaron'),('total_interactions','Interacciones'),('likes','Me gusta'),('comments','Comentarios'),('shares','Compartidos'),('saves','Guardados')]
if m:
 for key,label in labels:
  if key in m:print(f"- {label}: **{int(m[key]):,}**")
else:print('- Insights agregados no disponibles en esta ejecución.')
if g:
 for key,val in g.items():print(f"- {clean(key,50)}: **{int(val):,}**")

print('\n## Contenido publicado y rendimiento')
print(f"- Piezas recuperadas en la ventana: **{len(posts)}**")
if themes:
 print('- Mezcla temática: '+', '.join(f'{k} {v}' for k,v in sorted(themes.items(),key=lambda x:x[1],reverse=True)))
if posts:
 print('\n### Piezas destacadas')
 for p in posts[:5]:
  title=clean(p['caption'] or f"{p['type']} sin caption",90)
  print(f"- **{title}** — {int(p['likes'])} me gusta, {int(p['comments'])} comentarios, {int(p['saves'])} guardados, {int(p['shares'])} compartidos, {int(p['views'])} vistas")
else:print('- No se recuperaron publicaciones del periodo.')

print('\n## Recomendaciones')
if posts:
 best=theme(posts[0]['caption']); print(f"1. Repetir y variar el ángulo de **{best}**, que lideró la muestra semanal por interacción ponderada.")
else:print('1. Publicar al menos una pieza medible esta semana para recuperar señal de contenido.')
reach=m.get('reach',0); engaged=m.get('accounts_engaged',0)
if reach and engaged/reach<0.05:print('2. Añadir una llamada a comentar, guardar o compartir; la relación interacción/alcance está por debajo de 5 %.')
else:print('2. Mantener llamadas explícitas a comentar, guardar y compartir para convertir alcance en señal útil.')
print('3. Comparar cada semana por formato y tema; no atribuir nichos a seguidores individuales.')
print('\n## Límites')
print('- El análisis usa datos agregados oficiales y hasta 25 piezas recientes; no representa necesariamente las 575 publicaciones históricas.')
print('- Instagram no ofrece una lista completa de identidades de seguidores mediante esta integración.')
for k,e in errors.items():print(f"- {k}: {clean(e,180)}")
print('- No se publicó, respondió ni modificó contenido.')
