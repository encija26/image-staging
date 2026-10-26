import json,re
ALL={int(k):v for k,v in json.load(open('all.json')).items()}
E={}
def add(rows,old,new,scope='fabric'):
  for r in rows: E.setdefault(r,[]).append((old,new,scope))
add([974,977,978,1013,1053,1131,1143,1147,1150,1166,1169,1193,1196,1246,1284],'Charcoal','Pewter')
add([874,1041,1122,1124,1137],'Charcoal Frame','Jet Frame','frame')
add([996,1001,1276],'Moss','Fern')
for r,c in [(1054,'Ink'),(1055,'Dove'),(1056,'Cream'),(1059,'Cream'),(1060,'Cream'),(1061,'Flax'),(1065,'Stone'),(1066,'Dove'),(1067,'Cream'),(1068,'Cream')]:
  add([r],c,'Heathered '+c,'heather')
add([959,961,969,1026,1057,1080,1094,1099,1120,1122,1130,1134,1136,1145,1146,1148,1179,1180,1183,1185,1192,1200,1224,1267,1283],'Flax','Oyster')
add([887,942],'Flax','Cream')
add([1132],'Aegean','Deep Aegean')
add([1195],'Terracotta','Blood Orange')
json.dump({str(k):v for k,v in E.items()},open('plan1.json','w'))
def wb(s): return r'(?<![A-Za-z])'+re.escape(s)+r'(?![A-Za-z])'
out={};review=[]
for r,eds in E.items():
  v=ALL[r];new={c:v[c] for c in 'DGLP'}
  for old,nw,scope in eds:
    # D: only in colour slot after '— In'
    h,sep,t=new['D'].partition('— In ')
    assert sep,r
    if scope=='heather':
      t2=re.sub(r'^'+re.escape(old)+r'\b',nw,t)
    else:
      t2=re.sub(wb(old),nw,t,count=1)
    assert t2!=t,(r,old,t)
    new['D']=h+sep+t2
    new['P']=re.sub(wb(old),nw,new['P'],count=1) if old in new['P'] else (re.sub(r'^'+re.escape(old),nw,new['P']) )
    if scope=='heather':
      new['L']=re.sub(r'(in )'+re.escape(old)+r'\b',r'\1'+nw,new['L'],count=1)
    else:
      new['L']=re.sub(wb(old),nw,new['L'])
      if scope!='frame':
        lo=old.lower();ln=nw.lower()
        g=re.sub(wb(lo),ln,new['G']); g=re.sub(wb(old),nw,g)
        if g!=new['G']: review.append((r,old,nw,[s for s in re.split(r'(?<=[.!?])\s',g) if ln in s.lower()]))
        new['G']=g
      else:
        g=re.sub(r'charcoal (frame|legs|base)',r'jet \1',new['G'],flags=re.I)
        if g!=new['G']: review.append((r,old,nw,[s for s in re.split(r'(?<=[.!?])\s',g) if 'jet' in s.lower()]))
        new['G']=g
  out[r]=new
json.dump({str(k):v for k,v in out.items()},open('out1.json','w'),ensure_ascii=False)
print(len(out),'rows')
for r in out: 
  if ALL[r]['P']==out[r]['P']: print('P unchanged',r,ALL[r]['P'])
for x in review: print(x[0],x[1],'->',x[2],'|',' || '.join(s[:160] for s in x[3]))
