#!/usr/bin/env python3
"""Generate a static Teacher Nessa site from Pages CMS JSON.
Run: python3 scripts/compilar.py
No external libraries needed. GitHub Actions runs this on each CMS edit.
"""
from pathlib import Path
import json, shutil, sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
for name in ['index.html', 'editar.html', '404.html', 'robots.txt', '.nojekyll']:
 source=ROOT/name
 if source.exists():shutil.copy2(source,OUT/name)
(OUT/'datos').mkdir(exist_ok=True)
(OUT/'descargas').mkdir(exist_ok=True)
for folder in ['assets']:
 src=ROOT/folder
 if src.exists():shutil.copytree(src,OUT/folder,dirs_exist_ok=True)
site=json.loads((ROOT/'content'/'sitio.json').read_text(encoding='utf8'))
materiales=[];public_files=set();seen=set();bad=[]
# Publish original English grammar/vocabulary and music, Spanish values worksheets for 1 ESO,
# and classroom rubrics. Curricular programming, private data and other subjects remain hidden.
LEGACY_PUBLIC={
 'I4-03':'Gramática',
 'C1-01':'Gramática',
 'E3-07':'Canciones',
 'I4-13':'Canciones',
 'I4-05':'Canciones',
 'I4-06':'Canciones',
 'E3-06':'Canciones',
 'I1-10':'Rúbricas',
 'I2-16':'Vocabulario',
 'E3-15':'Canciones',
 'A1-05':'Atención Educativa',
 'A1-11':'Atención Educativa',
 'A1-14':'Atención Educativa',
 'A2-04':'Atención Educativa',
}
PUBLIC_KINDS={'Gramática','Vocabulario','Canciones','Rúbricas','Atención Educativa'}
LEVEL_ORDER={'1ESO':0,'2ESO':1,'ATENCION':2,'AMBOS':3}
AUDIO_TYPES={'.mp3','.m4a','.ogg','.wav'}
VIDEO_TYPES={'.mp4','.webm'}
SUPPORTED={'.pdf','.png','.jpg','.jpeg','.webp','.docx','.mp3','.m4a','.ogg','.wav','.mp4','.webm'}
GROUPS={'1A','1B','1C','2A','2B','AE','GENERAL'}
for file in sorted((ROOT/'content'/'materiales').glob('*.json')):
 try:record=json.loads(file.read_text(encoding='utf8'))
 except Exception as e:raise ValueError(f'JSON inválido: {file.name}: {e}')
 code=str(record.get('id',file.stem))
 if code in seen:raise ValueError(f'ID repetido: {code}')
 seen.add(code)
 if not record.get('published',False):continue
 if record.get('internal') or code.startswith('T1-'):continue
 if record.get('category')=='Tutoría 2.º ESO':continue
 kind=record.get('public_kind') or LEGACY_PUBLIC.get(code,'')
 if kind not in PUBLIC_KINDS:continue
 category=record.get('category','')
 if category=='Atención Educativa':
  level='ATENCION'
 elif category=='Inglés 1.º ESO':
  level='1ESO'
 elif category=='Inglés 2.º ESO':
  level='2ESO'
 elif category=='Inglés 1.º y 2.º':
  level='AMBOS'
 else:
  continue  # Never expose school administrative or personal collections.
 if level=='ATENCION' and kind!='Atención Educativa' and kind!='Canciones':continue
 if kind=='Atención Educativa' and level!='ATENCION':continue
 if record.get('rights_checked') is not True or record.get('privacy_checked') is not True:continue
 entry={
  'id':code,'title':record.get('title','Recurso sin título'),
  'description':record.get('description',''),
  'usage':record.get('usage',''),
  'category':category,
  'topic':record.get('topic',''),
  'kind':kind,'level':level,
  'course_label':{'1ESO':'Inglés · 1.º ESO','2ESO':'Inglés · 2.º ESO','AMBOS':'Inglés · 1.º y 2.º ESO','ATENCION':'Atención Educativa · 1.º ESO'}[level],
  'music_group':record.get('music_group',''),
  'file':record.get('reference_file') or 'Material de Teacher Nessa',
  'section':code.split('-')[0],
  'download':None,'downloads':[],'audio':None,'video':None,
  'access':'Recurso original revisado y disponible para uso educativo.'
 }
 requested=[record.get('asset'),record.get('extra_asset')]
 visited=set()
 for source in requested:
  path=str(source or '').lstrip('/')
  if path in visited or not path:continue
  visited.add(path)
  if not path.startswith('recursos/') or '..' in Path(path).parts:continue
  original=ROOT/path
  if not original.is_file() or original.suffix.lower() not in SUPPORTED:
   bad.append(f'{code}: archivo indicado no encontrado o formato no permitido: {path}')
   continue
  suffix=original.suffix.lower()
  is_media=suffix in AUDIO_TYPES or suffix in VIDEO_TYPES
  if is_media:
   verified=(record.get('audio_verified') is True and record.get('music_group') in GROUPS)
   if verified and record.get('listen_enabled') is True:
    if suffix in AUDIO_TYPES and entry['audio'] is None:entry['audio']=path
    if suffix in VIDEO_TYPES and entry['video'] is None:entry['video']=path
    public_files.add(path)
   elif record.get('listen_enabled'):
    bad.append(f'{code}: audio/vídeo sin verificación y grupo confirmados')
   if verified and record.get('download_enabled') is True:
    entry['downloads'].append({'url':path,'name':original.name})
    public_files.add(path)
  elif record.get('download_enabled') is True:
   entry['downloads'].append({'url':path,'name':original.name})
   public_files.add(path)
 if entry['downloads']:
  entry['download']=entry['downloads'][0]['url']
  entry['file']=entry['downloads'][0]['name']
 elif entry['audio'] or entry['video']:
  entry['file']=Path(entry['audio'] or entry['video']).name
 else:
  continue  # Do not advertise a resource without a real published file.
 materiales.append(entry)
materiales.sort(key=lambda x:(LEVEL_ORDER.get(x['level'],99),('Gramática','Vocabulario','Canciones','Rúbricas','Atención Educativa').index(x['kind']),x['id']))
# Copy only the explicitly enabled downloads, never the whole private review library.
for relative in sorted(public_files):
 dest=OUT/relative;dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/relative,dest)
(OUT/'datos'/'materiales.js').write_text('window.TN_MATERIALS='+json.dumps(materiales,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')
(OUT/'datos'/'sitio.js').write_text('window.TN_SITE='+json.dumps(site,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')
# News cards managed through Pages CMS.
news=[]
for nfile in (ROOT/'content'/'novedades').glob('*.json'):
 item=json.loads(nfile.read_text(encoding='utf8'))
 if item.get('published',False):
  image=str(item.get('image') or '').lstrip('/')
  if not (image.startswith('assets/uploads/') and '..' not in Path(image).parts and (ROOT/image).is_file()):image=''
  news.append({'title':item.get('title',''),'body':item.get('body',''), 'image':image,'sort':item.get('sort',0), 'published':True})
(OUT/'datos'/'novedades.js').write_text('window.TN_NEWS='+json.dumps(news,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')

(OUT/'datos'/'estado.json').write_text(json.dumps({'fichas_publicas':len(materiales),'descargas':len(public_files),'avisos':bad},ensure_ascii=False,indent=2),encoding='utf8')
# Old general catalogs are deliberately excluded: they contain out-of-scope material.\n# GitHub Pages domain: optional and only when configured / purchased
cname=ROOT/'CNAME'
if cname.exists():shutil.copy2(cname,OUT/'CNAME')
print(f'Sitio generado. Fichas: {len(materiales)} · Descargas: {len(public_files)}')
for err in bad:print('Aviso:',err,file=sys.stderr)
