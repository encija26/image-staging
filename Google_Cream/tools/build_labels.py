"""Rebuild Google_Cream/BH_MC_ShippingLabels.tsv from the live storefront.
Labels: white-glove (tag shipping-white-glove), large-item (shipping-large-item or
shipping-moes-freight), free (everything else). Exits non-zero, without writing,
if the store returns far fewer rows than the current file (safety check)."""
import collections, os, sys, time, urllib.request, json
OUT = os.path.join(os.path.dirname(__file__), '..', 'BH_MC_ShippingLabels.tsv')
def get(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            if i == 3: raise
            time.sleep(5 * (i + 1))
rows, page = [], 1
while True:
    ps = get(f'https://bramleyhousehome.com/products.json?limit=250&page={page}').get('products', [])
    if not ps: break
    for p in ps:
        t = set(p['tags'])
        lab = 'white-glove' if 'shipping-white-glove' in t else (
            'large-item' if ('shipping-large-item' in t or 'shipping-moes-freight' in t) else 'free')
        for v in p['variants']:
            rows.append((f"shopify_ZZ_{p['id']}_{v['id']}", lab))
    page += 1
old = 0
if os.path.exists(OUT):
    old = sum(1 for _ in open(OUT)) - 1
if old and len(rows) < 0.8 * old:
    print(f'ABORT: {len(rows)} rows vs {old} in current file'); sys.exit(2)
new = 'id\tshipping_label\n' + ''.join(f'{a}\t{b}\n' for a, b in rows)
cur = open(OUT).read() if os.path.exists(OUT) else ''
open(OUT, 'w').write(new)
print('rows', len(rows), dict(collections.Counter(l for _, l in rows)), 'changed' if new != cur else 'unchanged')
