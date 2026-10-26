import sys, numpy as np
from PIL import Image
from scipy import ndimage
def cut(src, dst, soft=238, hard=250):
    im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
    lum = im.min(axis=2)
    cand = lum >= soft
    lab, n = ndimage.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:,0], lab[:,-1]]))) - {0}
    bg = np.isin(lab, list(border))
    a = np.ones(lum.shape, np.float32)
    ramp = np.clip((hard - lum) / max(hard - soft, 1), 0, 1)
    a[bg] = ramp[bg]
    a[bg & (lum >= hard)] = 0
    # de-fringe: unmultiply white
    al = a[..., None]
    rgb = np.where(al > 0.01, (im - 255 * (1 - al)) / np.maximum(al, 0.01), im)
    rgb = np.clip(rgb, 0, 255)
    out = np.dstack([rgb, a * 255]).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(dst, 'WEBP', quality=92, alpha_quality=100, method=4)
    return float((a > 0.99).mean())
if __name__ == '__main__':
    s, d = sys.argv[1], sys.argv[2]
    soft = int(sys.argv[3]) if len(sys.argv) > 3 else 238
    hard = int(sys.argv[4]) if len(sys.argv) > 4 else 250
    print(d, round(cut(s, d, soft, hard), 4))
