import sys,os,json,numpy as np
from PIL import Image
from scipy import ndimage
def scan(path,thr=253,minpx=1500):
  a=np.asarray(Image.open(path).convert('RGBA'))
  rgb=a[...,:3];al=a[...,3]
  m=(rgb.min(axis=2)>=thr)&(al>=250)
  lab,n=ndimage.label(m)
  if n==0: return []
  sizes=ndimage.sum(m,lab,range(1,n+1))
  out=[]
  for i,s in enumerate(sizes,1):
    if s<minpx: continue
    ys,xs=np.where(lab==i)
    reg=rgb[ys,xs].astype(float)
    out.append((int(s),round(float(reg.mean()),2),round(float(reg.std()),2)))
  return out
if __name__=='__main__':
  fs=sorted(os.listdir(sys.argv[1]));res={}
  for f in fs:
    r=scan(os.path.join(sys.argv[1],f))
    if r: res[f]=r
  json.dump(res,open(sys.argv[2],'w'));print(len(fs),len(res))
