import json,os
from PIL import Image,ImageDraw,ImageFont
B='/home/claude/bh/b3/'
idx=json.load(open(B+'img/index.json'));rows=json.load(open(B+'rows.json'))
ps=[]
for i in range(1,9): ps+=json.load(open(B+f'packets/p{i}.json'))
os.makedirs(B+'img/cs',exist_ok=True)
font=ImageFont.load_default()
out={}
for n,p in enumerate(ps):
  rs=[str(r['row']) for r in p['rows'] if str(r['row']) in idx['meta']]
  W=170;cols=max(len(idx['meta'][r]) for r in rs) if rs else 1
  sheet=Image.new('RGB',(W*cols+60,(W+16)*len(rs)),'white');d=ImageDraw.Draw(sheet)
  for i,r in enumerate(rs):
    d.text((2,i*(W+16)+W//2),r,fill='black',font=font)
    for j,f in enumerate(idx['meta'][r]):
      pth=B+f'img/src/{r}/{f}'
      im=Image.open(pth).convert('RGB');im.thumbnail((W-4,W-4))
      sheet.paste(im,(60+j*W,i*(W+16)))
      wr=idx['white'][pth][0]
      d.text((60+j*W,i*(W+16)+W),f'{j+1} w{int(wr*100)}',fill='red' if wr<0.995 else 'black',font=font)
  fn=f'img/cs/{n:03d}.jpg';sheet.save(B+fn,quality=70)
  out[f'{n:03d}']={'product':p['product'],'rows':rs,'files':{r:idx['meta'][r] for r in rs}}
json.dump(out,open(B+'img/cs/index.json','w'),ensure_ascii=False,indent=0)
print(len(out))
