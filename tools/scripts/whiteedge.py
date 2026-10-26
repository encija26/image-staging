import numpy as np
from PIL import Image,ImageFilter
from scipy import ndimage
def edge(src,dst,strength=0.13,width=5,halo=0.16):
  im=Image.open(src).convert('RGBA');a=np.asarray(im).astype(np.float32)
  rgb=a[...,:3];al=a[...,3]/255
  inside=al>0.5
  d=ndimage.distance_transform_edt(inside)
  lum=rgb.min(axis=2)
  w=np.clip((lum-200)/40,0,1)  # only pale pixels
  f=1-strength*np.exp(-d/width)*w*inside
  rgb2=rgb*f[...,None]
  prod=Image.fromarray(np.dstack([rgb2,a[...,3]]).astype(np.uint8),'RGBA')
  # soft halo behind
  h=Image.fromarray((inside*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
  ha=(np.asarray(h).astype(np.float32)*halo).astype(np.uint8)
  base=Image.merge('RGBA',(Image.new('L',im.size,110),)*3+(Image.fromarray(ha),))
  base.alpha_composite(prod);base.save(dst,'WEBP',quality=92,alpha_quality=100,method=4)
