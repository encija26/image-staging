# AI cutout (rembg isnet) + hairline edge. Usage: aicut(src_jpg, dst_webp)
from rembg import remove, new_session
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage
_s=None
def aicut(src,dst,fill=1700):
  global _s
  if _s is None: _s=new_session('isnet-general-use')
  o=remove(Image.open(src).convert('RGB'),session=_s).convert('RGBA')
  a=np.asarray(o)[...,3].copy(); a[a<12]=0; o.putalpha(Image.fromarray(a))
  ys,xs=np.where(a>20); o=o.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
  sc=fill/max(o.size); o=o.resize((round(o.width*sc),round(o.height*sc)),Image.LANCZOS)
  c=Image.new('RGBA',(2000,2000),(0,0,0,0)); c.paste(o,((2000-o.width)//2,(2000-o.height)//2),o)
  A=np.asarray(c).astype(np.float32); rgb=A[...,:3]; al=A[...,3]
  solid=al>=250
  idx=ndimage.distance_transform_edt(~solid,return_distances=False,return_indices=True)
  rgb2=rgb[idx[0],idx[1]]
  al2=np.asarray(Image.fromarray(al.astype(np.uint8)).filter(ImageFilter.MinFilter(3))).astype(np.float32)
  al2=np.clip((al2-60)*255/195,0,255)
  inside=al2>128; d=ndimage.distance_transform_edt(inside)
  w=np.clip((rgb2.min(axis=2)-200)/40,0,1)
  rgb2=rgb2*(1-0.10*np.exp(-d/2.5)*w*inside)[...,None]
  prod=Image.fromarray(np.dstack([rgb2,al2]).astype(np.uint8),'RGBA')
  h=Image.fromarray((inside*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
  base=Image.merge('RGBA',(Image.new('L',(2000,2000),120),)*3+(Image.fromarray((np.asarray(h)*0.10).astype(np.uint8)),))
  base.alpha_composite(prod); base.save(dst,'WEBP',quality=92,alpha_quality=100,method=4)
  return base
