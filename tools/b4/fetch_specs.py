import json,re,html,time,urllib.request,urllib.parse,concurrent.futures as cf
def get(u):
  for i in range(4):
    try:
      return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read().decode('utf-8','replace')
    except Exception as e: err=e;time.sleep(2+i*2)
  raise err
bases=json.load(open('bases.json'));rows=json.load(open('rows.json'))
skus={x['N'] for x in rows.values() if x['N']}
def find(b):
  try:
    d=json.loads(get('https://modway.com/search/suggest.json?'+urllib.parse.urlencode({'q':b,'resources[type]':'product','resources[limit]':10})))
    return b,[p['handle'] for p in d['resources']['results']['products']]
  except Exception as e: return b,[]
H={}
with cf.ThreadPoolExecutor(8) as ex:
  for b,h in ex.map(find,bases): H[b]=h
allh=sorted({h for v in H.values() for h in v})
sku2={}
def js(h):
  try: return h,json.loads(get(f'https://modway.com/products/{h}.js'))
  except Exception: return h,None
with cf.ThreadPoolExecutor(8) as ex:
  for h,j in ex.map(js,allh):
    if not j: continue
    for v in j['variants']:
      if v['sku'] in skus: sku2[v['sku']]={'h':h,'vid':v['id'],'opt':v['title'],'public':v['price']/100}
def specs(sku):
  d=sku2[sku];t=get(f"https://modway.com/products/{d['h']}?variant={d['vid']}")
  m=re.search(r'product-metafield-details__specs-table">(.*?)</table>',t,re.S)
  out=[]
  if m:
    for a,b in re.findall(r'spec-label">\s*(.*?)\s*</td>\s*<td class="product-metafield-details__spec-value">\s*(.*?)\s*</td>',m.group(1),re.S):
      out.append((html.unescape(re.sub('<[^>]+>','',a)).strip(),html.unescape(re.sub('<[^>]+>','',b)).strip()))
  cap=re.search(r'Weight Capacity:\s*([\d,.]+\s*lbs)',html.unescape(t))
  return sku,out,cap.group(1) if cap else None
S={}
with cf.ThreadPoolExecutor(8) as ex:
  for sku,out,cap in ex.map(specs,sorted(sku2)):
    S[sku]=dict(sku2[sku],specs=out,cap=cap)
json.dump({'H':H,'S':S},open('specs.json','w'),ensure_ascii=False)
print(len(allh),'handles',len(S),'skus with specs; missing',len(skus-set(S)))
