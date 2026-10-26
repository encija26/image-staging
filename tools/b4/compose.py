import json,re,math
rows=json.load(open('rows.json'));S=json.load(open('specs.json'))['S']
def num(x): 
  x=float(x); return str(int(x)) if x==int(x) else str(x)
def dims(v):
  d={}
  for n,k in re.findall(r'([\d.]+)\s*"\s*([lwhd])',v.replace('”','"')): d[{'d':'l'}.get(k,k)]=n
  if not d:
    m=re.match(r'\s*([\d.]+)\s*"?\s*$',v)
    if m: d['x']=m.group(1)
  return d
def fmt3(d):
  p=[]
  if 'h' in d: p.append(f"Height {num(d['h'])} in")
  if 'w' in d: p.append(f"Width {num(d['w'])} in")
  if 'l' in d: p.append(f"Depth {num(d['l'])} in")
  return ', '.join(p)
SEAT=re.compile(r'\b(sofa|loveseat|sectional|chair|stool|ottoman|pouf|chaise|settee|armchair|recliner|glider|rocker|seat|daybed|futon)s?\b|\bbench(es)?\b',re.I)
NOTSEAT=re.compile(r'\b(table|desk|bed frame|platform bed|cabinet|vanity|bookcase|shelf)\b',re.I)
OTHER=[(r'^floor to (the )?underside of (table|desk)','Floor to underside of top'),(r'^floor to underside of (sideboard|vanity|stool|cabinet|console)','Floor to underside'),
 (r'^(table ?top|tabletop) thickness$|^thickness of top$','Tabletop thickness'),(r'^(leg clearance|clearance in between legs|inner clearance( dimensions)?)$','Clearance between legs'),
 (r'^inner drawer dimensions?$','Drawer interior'),(r'^(adjustable )?shelf dimensions?$','Shelf'),(r'^floor to (the )?bottom of side ?rail$','Under-bed clearance'),
 (r'^top of seat to top of backrest$|^backrest height from seat$','Back height above seat'),(r'^armrest height from seat$','Arm height above seat'),
 (r'^(cushion thi[ck]+ness|thickness of cushion)$','Cushion thickness'),(r'^(bathroom )?(vanity )?(sink|basin) dimensions$|^basin dimensions$','Basin')]
def sp_back(sp,title):
  return bool(re.search(r'chair|sofa|loveseat|sectional|settee|armchair|recliner|glider|rocker',title,re.I)) or any('backrest' in a.lower() for a,b in sp)
def build(r):
  x=rows[r];L=(x['L'] or '').strip();title=(x['D'] or x['C'] or '')
  paras=[p.strip() for p in re.split(r'\n\s*\n',L) if p.strip()]
  mat=next((p for p in paras if p.lower().startswith('materials')),None)
  oldpd=next((p for p in paras if p.lower().startswith('product dimensions')),None)
  wt=next((p for p in paras if p.lower().startswith('weight')),'Weight: TBD.')
  bx=next((p for p in paras if p.lower().startswith('boxed')),'Boxed dimensions: TBD.')
  s=S.get(x['N']);sp=s['specs'] if s else []
  lab={a.lower():b for a,b in sp}
  info={'seating':bool(SEAT.search(title)) and not NOTSEAT.search(title),'issues':[]}
  out=[]
  if mat: out.append(mat)
  ov=next((b for a,b in sp if a.lower().startswith('overall') or a.lower().endswith('product dimensions')),None)
  newpd=f"Product dimensions: {fmt3(dims(ov))}" if ov and fmt3(dims(ov)) else None
  pd=oldpd if (oldpd and 'TBD' not in oldpd) else (newpd or oldpd)
  if pd!=oldpd: info['issues'].append('dims_filled')
  if pd: out.append(pd)
  seath=seatd=armh=None
  for a,b in sp:
    al=a.lower()
    if al=='seat height': d=dims(b);seath=d.get('h') or d.get('x')
    elif al in('seat dimensions','seat dimension','seating dimensions','chair seat dimensions') and seath is None:
      d=dims(b);seath=d.get('h');seatd=d.get('l')
    elif al in('seat dimensions','seat dimension','seating dimensions','chair seat dimensions'):
      seatd=seatd or dims(b).get('l')
    elif al in('floor to top of armrest','armrest height'):
      d=dims(b);armh=d.get('h') or d.get('x')
  if armh is None:
    for a,b in sp:
      if a.lower() in('armrest dimensions','armrest dimension'):
        h=dims(b).get('h')
        if h and seath and float(h)>float(seath): armh=h
  P={}
  if pd:
    for k,n in re.findall(r'(Height|Width|Depth) ([\d.]+) in',pd): P[k[0].lower()]=float(n)
  PH=P.get('h');PM=max(P.values()) if P else None
  info['dropped']=[]
  if seath and PH and not (4<=float(seath)<=PH*0.9 or (float(seath)<=PH and not sp_back(sp,title))):
    info['dropped'].append(('seat height',seath));seath=None
  if seatd and P.get('d') and float(seatd)>P['d']: info['dropped'].append(('seat depth',seatd));seatd=None
  if armh and ((seath and float(armh)<=float(seath)) or (PH and float(armh)>PH)): info['dropped'].append(('arm height',armh));armh=None
  if info['seating'] and not seath and mat:
    mm=re.search(r'([\d.]+)\s*in(?:ches|\.)?\s+seat height|seat height (?:of )?([\d.]+)\s*in',mat,re.I)
    if mm: seath=mm.group(1) or mm.group(2);info['seat_from_desc']=True
  if info['seating']:
    flat=re.search(r'\b(ottoman|ottomans|pouf|poufs|bench|benches|backless|stool|stools)\b',title,re.I) and not re.search(r'back|arm',title,re.I) and not any('backrest' in a.lower() or 'armrest' in a.lower() for a,b in sp)
    if not seath and flat and ov: seath=dims(ov).get('h');info['flat']=True
    if seath: out.append(f"Seat height: {num(seath)} in")
    else: info['issues'].append('no_seat_height')
    if seatd and not re.search(r'\b(ottoman|ottomans|pouf|poufs|stool|stools)\b',title,re.I): out.append(f"Seat depth: {num(seatd)} in")
    if armh: out.append(f"Arm height: {num(armh)} in")
  used=set()
  for a,b in sp:
    for pat,name in OTHER:
      if re.search(pat,a.lower()) and name not in used:
        d=dims(b);v=fmt3(d) if len([k for k in d if k in 'lwh'])>1 else (f"{num(d.get('h') or d.get('x') or d.get('l') or d.get('w'))} in" if d else None)
        bad=False
        vals=[float(d[k]) for k in d]
        if name in('Shelf','Drawer interior','Basin','Clearance between legs') and len(vals)>1:
          if min(vals)<1 or (PM and max(vals)>PM): bad=True
          if name=='Basin' and P.get('w') and float(d.get('w',0))>=0.95*P['w']: bad=True
          if name in('Shelf','Drawer interior') and P.get('d') and float(d.get('l',0))>P['d']: bad=True
        if name=='Floor to underside' and PH and vals and vals[0]>=0.75*PH: bad=True
        if name=='Floor to underside of top' and PH and vals and vals[0]>=PH: bad=True
        if name=='Under-bed clearance' and vals and vals[0]>18: bad=True
        if name=='Tabletop thickness' and vals and vals[0]>4: bad=True
        if bad: info['dropped'].append((name,b));break
        if v and not (name.startswith('Arm height above') and not info['seating']):
          out.append(f"{name}: {v}");used.add(name)
        break
  out.append(wt);out.append(bx)
  if not s: info['issues'].append('not_on_modway')
  return '\n\n'.join(out),info
if __name__=='__main__':
  import collections
  res={};c=collections.Counter()
  for r in rows:
    t,i=build(r);res[r]=[t,i]
    for k in i['issues']: c[k]+=1
    if i['seating']: c['seating']+=1
  json.dump(res,open('L_new.json','w'),ensure_ascii=False);print(c)
  for r in ['700','1400']+[k for k,v in res.items() if v[1]['seating']][:3]:
    print('----',r,rows[r]['D']);print(res[r][0])
