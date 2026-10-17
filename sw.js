// Gastô 5.34: guarda o app no celular para abrir rápido e funcionar sem internet.
const C="gasto-5.34";
const SHELL=["./","./index.html","./manifest.json","./icon-192.png","./icon-512.png","./apple-touch-icon.png"];
self.addEventListener("install",e=>{ e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener("activate",e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k))))); self.clients.claim(); });
self.addEventListener("fetch",e=>{
  const r=e.request; if(r.method!=="GET") return; const u=new URL(r.url);
  if(/supabase\.(co|in)$/.test(u.hostname)) return;               // dados e login: sempre direto
  if(u.origin===location.origin){                                 // o app: tenta a versão nova, senão usa a guardada
    e.respondWith(fetch(r,{cache:"no-cache"}).then(res=>{ const cp=res.clone(); caches.open(C).then(c=>c.put(r,cp)); return res; })
      .catch(()=>caches.match(r).then(x=>x||caches.match("./index.html")))); return; }
  if(/cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com/.test(u.hostname))   // bibliotecas e fontes
    e.respondWith(caches.match(r).then(x=>x||fetch(r).then(res=>{ const cp=res.clone(); caches.open(C).then(c=>c.put(r,cp)); return res; })));
});
