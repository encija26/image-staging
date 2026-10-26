import json,re,html,urllib.request,concurrent.futures as cf,time
m=json.load(open('modway.json'))
rows=json.load(open('rows.json'))
need={m['sku2h'][r['N'].strip()][0] for r in rows.values() if r['N'].strip() in m['sku2h']}
def get(u):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read().decode('utf-8','replace')
        except Exception as e: err=e;time.sleep(2)
    raise err
def parse(h):
    page=get('https://modway.com/products/'+h)
    t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',page)))
    out={}
    for mm in re.finditer(r'Fabric details (.{1,40}?) (SW-\d+) Fabric Composition (.*?) Care Instructions (.*?)(?= Fabric details| \{|$)',t):
        col,sw,comp,care=mm.groups()
        out.setdefault(col.strip(),{'swatch':sw,'composition':comp.strip()[:200],'care':care.strip()[:1200]})
    # specs block
    sp=''
    i=t.find('Specifications')
    if i>0: sp=t[i:i+2500]
    return h,out,sp
with cf.ThreadPoolExecutor(6) as ex:
    for h,c,sp in ex.map(parse,sorted(need)):
        m['prod'][h]['care_by_colour']=c; m['prod'][h]['specs_text']=sp
json.dump(m,open('modway.json','w'),ensure_ascii=False)
nocare=[h for h in need if not m['prod'][h]['care_by_colour']]
print(len(need),'products;',len(nocare),'without fabric care blocks')
print(nocare)
