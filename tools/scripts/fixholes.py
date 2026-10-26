import sys,os,json,numpy as np
from PIL import Image
from scipy import ndimage
def fix(src,dst,seed_thr=254,minpx=1500,hard=250,soft=238):
  a=np.asarray(Image.open(src).convert('RGBA')).astype(np.float32)
  rgb=a[...,:3];al=a[...,3]/255.0
  lum=rgb.min(axis=2)
  seed=(lum>=seed_thr)&(al>=0.98)
  lab,n=ndimage.label(seed)
  if n==0: return 0
  sizes=ndimage.sum(seed,lab,range(1,n+1))
  keep=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>=minpx])
  if not keep.any(): return 0
  # grow within near-white (>=hard) connected to kept seeds
  near=(lum>=hard)&(al>=0.98)
  lab2,_=ndimage.label(near)
  ids=np.unique(lab2[keep]);ids=ids[ids>0]
  core=np.isin(lab2,ids)
  ring=ndimage.binary_dilation(core,iterations=2)&~core&(lum>=soft)
  na=al.copy()
  na[core]=0
  ramp=np.clip((hard-lum)/(hard-soft),0,1)
  na[ring]=np.minimum(na[ring],ramp[ring])
  aa=na[...,None]
  out_rgb=np.where((aa>0.01)&(aa<0.999)&ring[...,None],(rgb-255*(1-aa))/np.maximum(aa,0.01),rgb)
  out=np.dstack([np.clip(out_rgb,0,255),na*255]).astype(np.uint8)
  Image.fromarray(out,'RGBA').save(dst,'WEBP',quality=92,alpha_quality=100,method=4)
  return int(core.sum())
if __name__=='__main__':
  h=json.load(open(sys.argv[1]));src=sys.argv[2];dst=sys.argv[3];os.makedirs(dst,exist_ok=True);res={}
  for f in h:
    res[f]=fix(os.path.join(src,f),os.path.join(dst,f))
  json.dump(res,open(sys.argv[4],'w'));print(len(res),sum(1 for v in res.values() if v))
