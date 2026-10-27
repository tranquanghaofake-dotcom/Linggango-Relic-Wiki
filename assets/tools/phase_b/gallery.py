"""gallery.html: the shortlist, the generator sheet and every contact sheet (sheets/), filterable by tier and name. Static, no fetch,
so it opens from disk. Usage: python3 -I gallery.py <assets>"""
import sys,os,json,html
A=sys.argv[1]; idx=json.load(open(os.path.join(A,'sheets','index.json')))
items=sorted(idx.items(),key=lambda kv:(kv[1]['tier'],kv[1]['source'].lower(),kv[0]))
rows='\n'.join(f'<figure data-t="{html.escape(v["tier"])}" data-n="{html.escape((v["source"]+" "+k).lower())}"><figcaption>{html.escape(v["source"])} <small>{k} · {v["tier"]} · {v["count"]}</small></figcaption><img loading="lazy" src="sheets/{k}.png" alt="{html.escape(v["source"])}"></figure>' for k,v in items)
page=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Asset library</title>
<style>body{{background:#1e1e22;color:#ddd;font:14px system-ui,sans-serif;margin:16px}}img{{image-rendering:pixelated;max-width:100%}}
figure{{margin:0 0 24px}}figcaption{{margin:0 0 6px;font-weight:600}}small{{color:#999;font-weight:400}}input,select{{background:#2a2a30;color:#ddd;border:1px solid #444;padding:6px}}
.bar{{position:sticky;top:0;background:#1e1e22;padding:8px 0;display:flex;gap:8px;flex-wrap:wrap}}</style>
<h1>Linggango Relic Wiki asset library</h1>
<p>Thumbnails are the first frame, integer scale. Each sheet has a <code>.json</code> beside it mapping cells (20 per row) to catalog ids. Tiers and licences: <code>README.md</code>.</p>
<h2>Shortlist</h2><img src="shortlist.png" alt="shortlist"><p>Details: <code>shortlist.md</code>.</p>
<h2>Generator (fxgen.py), 12 themes</h2><img src="lib/lgw-fxgen/contact_sheet.png" alt="generator">
<h2>Contact sheets ({len(items)})</h2>
<div class="bar"><input id="q" placeholder="filter by name"><select id="t"><option value="">all tiers</option><option>A</option><option>A-SA</option><option>A-perm</option></select></div>
<div id="g">{rows}</div>
<script>const q=document.getElementById('q'),t=document.getElementById('t');function f(){{const s=q.value.toLowerCase(),v=t.value;for(const e of document.querySelectorAll('#g figure'))e.hidden=!(e.dataset.n.includes(s)&&(!v||e.dataset.t===v))}}q.oninput=f;t.onchange=f</script>'''
open(os.path.join(A,'gallery.html'),'w').write(page); print(len(items),'sheets in gallery.html')
