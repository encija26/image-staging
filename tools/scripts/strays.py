import sys,os,json,numpy as np
from PIL import Image
from scipy import ndimage
def strays(path):
  a=np.asarray(Image.open(path))[...,3]>40
  small=a[::4,::4]
  lab,n=ndimage.label(small)
  if n<2: return None
  s=ndimage.sum(small,lab,range(1,n+1));big=s.max()
  objs=ndimage.find_objects(lab)
  bi=int(np.argmax(s));by,bx=objs[bi]
  out=[]
  for i,(sz,(ys,xs)) in enumerate(zip(s,objs)):
    if i==bi or sz<15: continue
    # outside main bbox horizontally or vertically
    if xs.start>bx.stop+10 or xs.stop<bx.start-10 or ys.start>by.stop+10 or ys.stop<by.start-10:
      out.append(int(sz))
  return out if len(out)>=2 else None
fs=sys.argv[2:] if len(sys.argv)>2 else sorted(os.listdir(sys.argv[1]))
res={}
for f in fs:
  r=strays(os.path.join(sys.argv[1],f))
  if r: res[f]=r
json.dump(res,open('strays.json','w'));print(len(res));print('\n'.join(list(res)[:60]))
