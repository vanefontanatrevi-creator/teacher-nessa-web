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
for file in sorted((ROOT/'content'/'materiales').glob('*.json')):
 try:record=json.loads(file.read_text(encoding='utf8'))
 except Exception as e: raise ValueError(f'JSON inválido: {file.name}: {e}')
 code=record.get('id',file.stem)
 if code in seen:raise ValueError(f'ID repetido: {code}')
 seen.add(code)
 if not record.get('published',False):continue
 category=record.get('category','Inglés 1.º ESO')
 entry={
  'id':str(code),'title':record.get('title','Recurso sin título'),
  'description':record.get('description',''),
  'usage':record.get('usage',''),
  'category':category,'topic':record.get('topic',''),
  'file':record.get('reference_file') or 'Sin fichero identificado',
  'section':str(code).split('-')[0], 'download':None,
  'access':'Ficha de catálogo. Descarga pendiente de revisión o de archivo.',
 }
 # Avoid making internal files discoverable in the compiled website.
 if record.get('internal') or str(code).startswith('T1-'):
  entry['file']='Uso interno · versión pública sin datos personales'
  entry['access']='Ficha informativa. No se publican los originales internos de Tutoría.'
 else:
  asset=str(record.get('asset') or '').lstrip('/')
  if asset.startswith('recursos/') and '..' not in Path(asset).parts and (ROOT/asset).is_file():
   if all(record.get(key) is True for key in ['download_enabled','rights_checked','privacy_checked']):
    entry['download']=asset
    entry['file']=Path(asset).name
    entry['access']='Recurso original disponible para descarga gratuita y educativa.'
    public_files.add(asset)
  elif record.get('download_enabled'):
   bad.append(f'{code}: descarga solicitada pero sin verificaciones o archivo existente')
 materiales.append(entry)
materiales.sort(key=lambda x:(next((i for i,p in enumerate(('I','E','C','A','T')) if x['id'].startswith(p)),5),x['id']))
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
# Public guide available in the site
src=ROOT/'descargas'/'GUIA_DE_USO.html';
if src.exists():shutil.copy2(src,OUT/'descargas'/'GUIA_DE_USO.html')
src=ROOT/'descargas'/'Catalogo_Teacher_Nessa_Publico.pdf'
if src.exists():shutil.copy2(src,OUT/'descargas'/src.name)
# GitHub Pages domain: optional and only when configured / purchased
cname=ROOT/'CNAME'
if cname.exists():shutil.copy2(cname,OUT/'CNAME')
print(f'Sitio generado. Fichas: {len(materiales)} · Descargas: {len(public_files)}')
for err in bad:print('Aviso:',err,file=sys.stderr)
