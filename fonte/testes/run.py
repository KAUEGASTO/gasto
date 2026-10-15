from playwright.sync_api import sync_playwright
import json,sys
sys.path.insert(0,'.'); from fixtures import F
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    pg.goto('file:///home/claude/cartao.html'); pg.wait_for_timeout(400)
    for k,f in F.items():
        r=pg.evaluate("([t,D])=>{ const rows=parseInvoiceText(t,D); return {rows, meta:PARSE_META, kinds:rows.map(r=>kindOf(r)), parc:rows.map(r=>{const pm=PARC_RE.exec(r.desc); return pm?[pm[1]||pm[3]||pm[5]||pm[7],pm[2]||pm[4]||pm[6]||pm[8]].join('/'):''})} }",[f['lines'].strip(),f['D']])
        M=r['meta']; e=f['exp']
        ok = len(r['rows'])==e['n'] and M['bankTotal']==e['total'] and abs(M['readTotal']-e['total'])<0.02 and M['due']==e['due'] and len(M['holders'])==e['holders']
        print(('OK  ' if ok else 'FALHA'),k, M.get('bank'),'| linhas',len(r['rows']),'/',e['n'],'| banco',M['bankTotal'],'lido',M['readTotal'],'| venc',M['due'],'| cartões',[(h['name'],h['final'],h['total']) for h in M['holders']],'| não lidas',M['unread'])
        if not ok or '-v' in sys.argv:
            for x,kd,pc in zip(r['rows'],r['kinds'],r['parc']): print('     ',x['date'],x['desc'],x['value'],'CR' if x['credit'] else '',kd,pc,x.get('holder'))
    print(errs); b.close()
