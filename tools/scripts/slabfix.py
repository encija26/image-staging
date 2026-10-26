# Remove floor slab from an existing cutout: AI mask on the live image, then keep the original pixels only inside the closed+filled AI mask.
from rembg import remove, new_session
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage
_s=None
def slabfix(src,dst,close=21):
  global _s
  if _s is None: _s=new_session('isnet-general-use')
  im=Image.open(src).convert('RGBA');W,H=im.size
  bg=Image.new('RGBA',im.size,(255,255,255,255));bg.alpha_composite(im)
  m=np.asarray(remove(bg.convert('RGB'),session=_s,only_mask=True)).astype(np.float32)/255
  mb=m>0.5
  st=ndimage.generate_binary_structure(2,1)
  mc=ndimage.binary_closing(mb,structure=st,iterations=close)
  mc=ndimage.binary_fill_holes(mc)
  mc=ndimage.binary_dilation(mc,iterations=2)
  soft=np.asarray(Image.fromarray((mc*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)/255
  a=np.asarray(im).astype(np.float32)
  oa=a[...,3]/255
  na=np.minimum(oa,soft)
  out=np.dstack([a[...,:3],na*255]).astype(np.uint8)
  Image.fromarray(out,'RGBA').save(dst,'WEBP',quality=92,alpha_quality=100,method=4)
  return (oa>0.5).sum(),(na>0.5).sum()
