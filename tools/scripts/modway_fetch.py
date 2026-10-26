import json,re,html,sys,time,concurrent.futures as cf,urllib.request,urllib.parse
rows=json.load(open('rows.json'))
def get(u):
    for i in range(3):
        try:
            req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return urllib.request.urlopen(req,timeout=40).read().decode('utf-8','replace')
        except Exception as e: err=e; time.sleep(2)
    raise err
skus=sorted({r['N'].strip() for r in rows.values() if r['N']})
def base(s):
    m=re.match(r'(EEI-\d+)',s); return m.group(1) if m else s
bases=sorted({base(s) for s in skus})
def find(b):
    d=json.loads(get('https://modway.com/search/suggest.json?'+urllib.parse.urlencode({'q':b,'resources[type]':'product','resources[limit]':10})))
    return b,[p['handle'] for p in d['resources']['results']['products']]
handles={}
with cf.ThreadPoolExecutor(8) as ex:
    for b,h in ex.map(find,bases): handles[b]=h
prod={}
def load(h):
    j=json.loads(get(f'https://modway.com/products/{h}.js'))
    page=get(f'https://modway.com/products/{h}')
    t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',page)))
    care=sorted(set(m.strip() for m in re.findall(r'Fabric Composition (.{0,400}?Cleaning Code: ?\w+)',t)))
    swatch=re.findall(r'Swatch - ([^"(]+?) \((SW-\d+)\)',page)
    i=t.find('Refined');desc=''
    m=re.search(r'Description\s*(.{50,2500}?)(?:Specifications|Dimensions|Features)',t)
    return h,{'title':j['title'],'variants':[(v['id'],v['sku'],v['option1']) for v in j['variants']],
      'media':[(m_['position'],m_.get('alt'),m_['src'].split('?')[0]) for m_ in j['media']],
      'care':care,'body_html':(j.get('description') or '')[:4000]}
allh=sorted({h for hs in handles.values() for h in hs})
with cf.ThreadPoolExecutor(6) as ex:
    for h,d in ex.map(load,allh): prod[h]=d
sku2h={}
for h,d in prod.items():
    for vid,s,o in d['variants']: sku2h[s]=(h,vid,o)
json.dump({'handles':handles,'prod':prod,'sku2h':sku2h},open('modway.json','w'),ensure_ascii=False)
miss=[(k,r['N']) for k,r in rows.items() if r['N'].strip() not in sku2h]
print(len(bases),'bases',len(allh),'handles; missing SKUs:',miss)
