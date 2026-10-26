import json,re
A={int(k):v for k,v in json.load(open('all.json')).items()};O={int(k):v for k,v in json.load(open('out1.json')).items()}
cur={k:{c:(O[k][c] if (k in O and c in O[k]) else v[c]) for c in 'ADGLP'} for k,v in A.items()}
orig={k:dict(v) for k,v in cur.items()}
bh=lambda d:re.sub(r'^BH [|I] Studio\s*','',d.replace('\n',' ')).split(' — ')[0].strip()
def wb(s): return r'(?<![A-Za-z])'+re.escape(s)+r'(?![A-Za-z])'
log=[]
# family renames
for old,new in [('Aylsham','Saint-Germain'),('Clovelly','Trianon'),('Bled','Vincennes'),('Natchez','Vaux'),('Woodstock','Cassis'),('Braemar','Mariager')]:
  for k in A:
    if bh(cur[k]['D']).startswith(old+' '):
      cur[k]['D']=cur[k]['D'].replace('\n'+old+' ','\n'+new+' ',1)
      assert new in cur[k]['D'],k
# specific G fixes
def rep(k,a,b):
  assert a in cur[k]['G'],(k,a); cur[k]['G']=cur[k]['G'].replace(a,b)
k=[k for k in A if bh(cur[k]['D']).startswith('Vaux ')][0]
rep(k,'not least in the old river towns of the lower Mississippi, where Natchez began as a French fort.','not least in the great houses around Paris, such as the château of Vaux-le-Vicomte.')
for k in A:
  if bh(cur[k]['D']).startswith('Vincennes '): rep(k,'it filled the coffee houses of Europe by the millions','it filled the cafés of Paris and the coffee houses of Europe by the millions')
  if bh(cur[k]['D']).startswith('Cassis ') and 'made a formal seat comfortable enough for a long dinner.' in cur[k]['G']:
    rep(k,'made a formal seat comfortable enough for a long dinner.','made a formal seat comfortable enough for a long dinner, nowhere more elegantly than in the dining rooms of nineteenth-century France.')
# colour renames
def colour(rows,old,new,gwords=None):
  for k in rows:
    h,s,t=cur[k]['D'].partition('— In ')
    t2=re.sub(wb(old),new,t,count=1); assert t2!=t,(k,old,t); cur[k]['D']=h+s+t2
    cur[k]['P']=re.sub(wb(old),new,cur[k]['P'],count=1)
    cur[k]['L']=re.sub(wb(old),new,cur[k]['L'])
    g=cur[k]['G']
    for gw in (gwords or [old]):
      g=re.sub(wb(gw),new,g); g=re.sub(wb(gw.lower()),new.lower(),g)
    if g!=cur[k]['G']: log.append((k,old,new,[s[:170] for s in re.split(r'(?<=[.!?])\s',g) if new.lower() in s.lower()]))
    cur[k]['G']=g
colour([970,971,1012],'Fern Green','Malachite',['Fern Green','Fern'])
colour([1095,1098,1282],'Peacock','Teal')
colour([1023,1158,1210],'Aegean','Sea Mist')
colour([1178],'Terracotta','Blood Orange')
colour([1194],'Dove','Smoke'); colour([1226],'Stone','Smoke')
colour([1121],'Flax','Greige')
for k in [943,944,945]: colour([k],'Ticking Stripe','Stripe',['Ticking Stripe','ticking stripe'])
# Iron -> Jet (colour words only)
scope=[k for k,v in A.items() if v['A'] in('Next - go live','Notes review before live')]
for k in scope:
  h,s,t=cur[k]['D'].partition('— In ')
  if not re.search(r'\bIron\b',t): continue
  t2=re.sub(r'^Jet with Iron Base$','Jet',t); t2=re.sub(r'\bIron\b','Jet',t2)
  cur[k]['D']=h+s+t2
  p=cur[k]['P']; p2='Jet' if p=='Jet with Iron Base' else re.sub(r'\bIron\b','Jet',p); cur[k]['P']=p2
  L=cur[k]['L']; L=re.sub(r'matte Iron finish','matte Jet finish',L); L=re.sub(r'\bin Iron\b','in Jet',L); cur[k]['L']=L
  log.append((k,'Iron','Jet',[t2,p2,re.findall(r'[^,.;]*\bJet\b[^,.;]*',L)[:2]]))
# status
for k in scope:
  if A[k]['A']=='Notes review before live': cur[k]['A']='Next - go live'
ch={k:v for k,v in cur.items() if v!=orig[k] or k in O}
json.dump({str(k):v for k,v in ch.items()},open('out2.json','w'),ensure_ascii=False)
print(len(ch))
for x in log: print(x)
# leftover checks
print('Iron left in titles:',[k for k in scope if re.search(r'— In .*\bIron\b',cur[k]['D'])])
print('Ticking left in Salcombe G:',[k for k in [943,944,945] if 'ticking' in cur[k]['G'].lower()])
print('old fam names in G:',[k for k in cur if re.search(r'\b(Aylsham|Clovelly|Natchez|Woodstock|Braemar)\b',cur[k]['G']) and bh(cur[k]['D']).split()[0] in ('Saint-Germain','Trianon','Vaux','Cassis','Mariager')])
print('em:',[k for k,v in ch.items() if re.search('[—–]',v['G']+v['L'])])
