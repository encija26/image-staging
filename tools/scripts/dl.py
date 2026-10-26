import json,os,re,urllib.request,concurrent.futures as cf
from PIL import Image
B='/home/claude/bh/b3/'
rows=json.load(open(B+'rows.json'));m=json.load(open(B+'modway.json'));P=json.load(open(B+'pricing.json'))
jobs=[];meta={}
for k in P:
  sku=rows[k]['N'].strip();h,vid,opt=m['sku2h'][sku]
  med=[x for x in m['prod'][h]['media'] if (x[1] or '').strip()==opt and 'allout' not in x[2].lower()]
  if not med:
    import re as _r
    med=[x for x in m['prod'][h]['media'] if _r.match(_r.escape(sku)+r'[._]',x[2].split('/')[-1]) and 'allout' not in x[2].lower()]
  meta[k]=[]
  for pos,alt,src in med:
    fn=src.split('/')[-1]; u=('https:'+src) if src.startswith('//') else src
    d=B+f'img/src/{k}';os.makedirs(d,exist_ok=True)
    jobs.append((u,f'{d}/{pos:03d}_{fn}'));meta[k].append(f'{pos:03d}_{fn}')
def go(j):
  u,p=j
  if not os.path.exists(p):
    urllib.request.urlretrieve(u,p)
  im=Image.open(p).convert('RGB');w,h=im.size;px=im.load()
  ring=[px[x,0] for x in range(0,w,4)]+[px[x,h-1] for x in range(0,w,4)]+[px[0,y] for y in range(0,h,4)]+[px[w-1,y] for y in range(0,h,4)]
  return p,sum(1 for q in ring if min(q)>=250)/len(ring),(w,h)
res={}
with cf.ThreadPoolExecutor(12) as ex:
  for p,wr,sz in ex.map(go,jobs): res[p]=(round(wr,3),sz)
json.dump({'meta':meta,'white':res},open(B+'img/index.json','w'))
print(len(jobs),'images',sum(1 for v in res.values() if v[0]>=0.995),'studio')
nomedia=[k for k,v in meta.items() if not v];print('no media rows',nomedia)
