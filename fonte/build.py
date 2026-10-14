#!/usr/bin/env python3
"""Gera o app instalável (pasta app/site) a partir do arquivo único do Gastô (cartao.html).
Uso: python3 build.py [url_supabase] [chave_anon]
Sem url/chave o app roda só no aparelho (igual ao protótipo)."""
import sys, re, json, os, shutil
from PIL import Image
ROOT=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(ROOT,'cartao.html'); OUT=os.path.join(ROOT,'..')
url = sys.argv[1] if len(sys.argv)>1 else ''; key = sys.argv[2] if len(sys.argv)>2 else ''
src=open(SRC,encoding='utf-8').read()
ver=re.search(r'const APP_VERSION = "([^"]+)"',src).group(1)
title_line, rest = src.split('\n',1)
assert title_line.startswith('<title>')
# CSS/HTML até o <script> principal vai no head/body
head_part, body_part = rest.split('\n<div class="wrap" id="app"></div>',1)
os.makedirs(OUT,exist_ok=True)
head=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<title>Gastô</title>
<meta name="description" content="Controle dos gastos do cartão de crédito da família">
<meta name="theme-color" content="#2f5be0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Gastô">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Gastô">
<meta property="og:title" content="Gastô · Seu cartão sob controle">
<meta property="og:description" content="Gastos do cartão da família, metas por categoria e faturas num só lugar. Instale no celular e use com quem divide o cartão com você.">
<meta property="og:url" content="https://kauegasto.github.io/gasto/">
<meta property="og:image" content="https://kauegasto.github.io/gasto/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<script>window.GASTO_CLOUD={json.dumps({"url":url,"key":key})};</script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.75.0/dist/umd/supabase.js"></script>
{head_part}
</head>
<body>
<div class="wrap" id="app"></div>'''
tail='''
<script>if("serviceWorker" in navigator) window.addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));</script>
</body>
</html>
'''
open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(head+body_part.rstrip()+tail)
man={"name":"Gastô","short_name":"Gastô","description":"Controle dos gastos do cartão de crédito da família","lang":"pt-BR",
 "start_url":"./","scope":"./","display":"standalone","orientation":"portrait","background_color":"#f3f4f8","theme_color":"#2f5be0",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"},
          {"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
open(os.path.join(OUT,'manifest.json'),'w').write(json.dumps(man,ensure_ascii=False,indent=1))
im=Image.open(os.path.join(ROOT,'icone-1024.png')).convert('RGB')
shutil.copy(os.path.join(ROOT,'og-image.png'),os.path.join(OUT,'og-image.png'))
for n,s in [('icon-192.png',192),('icon-512.png',512),('apple-touch-icon.png',180)]: im.resize((s,s),Image.LANCZOS).save(os.path.join(OUT,n),optimize=True)
sw='''// Gastô __VER__: guarda o app no celular para abrir rápido e funcionar sem internet.
const C="gasto-__VER__";
const SHELL=["./","./index.html","./manifest.json","./icon-192.png","./icon-512.png","./apple-touch-icon.png"];
self.addEventListener("install",e=>{ e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener("activate",e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k))))); self.clients.claim(); });
self.addEventListener("fetch",e=>{
  const r=e.request; if(r.method!=="GET") return; const u=new URL(r.url);
  if(/supabase\\.(co|in)$/.test(u.hostname)) return;               // dados e login: sempre direto
  if(u.origin===location.origin){                                 // o app: tenta a versão nova, senão usa a guardada
    e.respondWith(fetch(r,{cache:"no-cache"}).then(res=>{ const cp=res.clone(); caches.open(C).then(c=>c.put(r,cp)); return res; })
      .catch(()=>caches.match(r).then(x=>x||caches.match("./index.html")))); return; }
  if(/cdn\\.jsdelivr\\.net|cdnjs\\.cloudflare\\.com|fonts\\.(googleapis|gstatic)\\.com/.test(u.hostname))   // bibliotecas e fontes
    e.respondWith(caches.match(r).then(x=>x||fetch(r).then(res=>{ const cp=res.clone(); caches.open(C).then(c=>c.put(r,cp)); return res; })));
});
'''.replace('__VER__',ver)
open(os.path.join(OUT,'sw.js'),'w').write(sw)
open(os.path.join(OUT,'.nojekyll'),'w').write('')
print('ok', ver, 'cloud' if url else 'local')
