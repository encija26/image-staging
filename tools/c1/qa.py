import json,glob,re,collections
P={};pk={}
for f in sorted(glob.glob('/home/claude/bh/c1/packets/p*.json')):
  d=json.load(open(f))
  for p in d['products']:
    for r in p['rows']: P[r['row']]=r;pk[r['row']]=p['handle']
O={}
for f in sorted(glob.glob('/home/claude/bh/c1/out/p*.json')): O.update(json.load(open(f)))
iss=collections.defaultdict(list)
NAT=re.compile(r'wood(en)? leg|wood frame|wooden|solid (hard)?wood|wood veneer|veneer|rattan|\bcane\b|travertine|(?<!faux )marble|natural stone|mango wood|oak|walnut|ash wood|acacia|bamboo|teak|pine',re.I)
for k,r in P.items():
  if k not in O: iss['missing'].append(k);continue
  m=O[k]['M']; mat=r['materials_and_dimensions'].split('\n\n')[0]
  if re.search('[—–]',m): iss['dash'].append(k)
  care=r['modway_fabric_care']
  for w in ['wash','launder','dry-clean','dry clean','removable','machine']:
    if re.search(w,m,re.I) and not re.search(w,care,re.I) and not (w in('dry-clean','dry clean') and 'solvent' in m.lower()):
      iss['word:'+w].append(k)
  if 'Natural Variation' in m and not NAT.search(mat): iss['natvar_without_natural'].append(k)
  if NAT.search(mat) and 'Natural Variation' not in m and not re.search(r'faux|engineered wood with',mat,re.I): iss['natural_no_note?'].append(k)
  if re.search(r'handmade',m,re.I): iss['handmade'].append(k)
  if re.search(r'(strap|kit|hardware|fixings?|bolts?)[^.]{0,30}\b(included|supplied)\b',m,re.I): iss['included/supplied'].append(k)
  heads=[b.split('\n')[0] for b in m.split('\n\n')]
  if len(set(heads))!=len(heads): iss['dup_head'].append(k)
  if any('\n' not in b for b in m.split('\n\n')): iss['block_no_body'].append(k)
  n=len(m.split()); 
  if n<40 or n>260: iss[f'len'].append((k,n))
# identical within product
by=collections.defaultdict(set)
for k in O:
  if k in pk: by[pk[k]].add(O[k]['M'])
iss['product_variants_differ']=[h for h,s in by.items() if len(s)>1]
for a,b in iss.items(): print(a,len(b),b[:12])
print('rows',len(O),'of',len(P),'review notes',sum(1 for v in O.values() if v.get('R')))
