# before/after contact sheets: per colour, top row = before, bottom = after
import json,re,os,sys
from PIL import Image, ImageDraw
B='/home/claude/bh/b3/img/';S=sys.argv[1];os.makedirs(S,exist_ok=True)
jobs=json.load(open(B+'ai_jobs.json'))
key=lambda f: re.sub(r'-0\d-[a-z-]+\.webp$','',f)
groups={}
for s,f in jobs:
  if os.path.exists(B+'ai/'+f.replace('.webp','-v2.webp')): groups.setdefault(key(f),[]).append(f)
T=180
def tile(p):
  im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(245,241,232,255));bg.alpha_composite(im);return bg.convert('RGB').resize((T,T))
ks=sorted(groups);pages=[ks[i:i+6] for i in range(0,len(ks),6)]
for n,pg in enumerate(pages):
  W=T*6;H=sum(2*T+20 for _ in pg);sh=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(sh);y=0
  for k in pg:
    d.text((4,y+2),k.replace('bramley-house-',''),fill='black');y+=20
    for i,f in enumerate(sorted(groups[k])[:6]):
      sh.paste(tile(B+'out/'+f),(i*T,y));sh.paste(tile(B+'ai/'+f.replace('.webp','-v2.webp')),(i*T,y+T))
    y+=2*T
  sh.save(f'{S}/ba_{n:02d}.jpg',quality=85)
print(len(ks),'colours',len(pages),'pages')
