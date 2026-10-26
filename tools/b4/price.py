import openpyxl,json,math
tp=json.load(open('trade.json'))
wb=openpyxl.load_workbook('sheet2.xlsx',read_only=True,data_only=True)
ws=wb['Modway Curation']
def mult(c): return 1.95 if c<=300 else 1.60 if c>=1500 else 1.95-0.35*(c-300)/1200
def retail(c):
  raw=c*mult(c); r=math.ceil((raw+1)/10)*10-1
  # smallest number ending in 9 >= raw
  r=math.floor(raw/10)*10+9
  if r<raw: r+=10
  return r
out={};stats={'priced':0,'changed':0,'new':0,'same':0,'nocost':[],'odd':[]}
for i,row in enumerate(ws.iter_rows(min_row=5,max_col=16,values_only=True),start=5):
  A,N=row[0],row[13]
  if not N: continue
  if (A or '').strip()=='Live': continue
  sku=str(N).strip(); J=row[9]
  try: J=float(J)
  except: J=None
  c=tp.get(sku)
  if c is None: stats['nocost'].append((i,sku,J)); continue
  st='same' if J is not None and abs(J-c)<0.005 else ('new' if J is None else 'changed')
  stats[st]+=1; stats['priced']+=1
  odd = abs(c*4-round(c*4))>1e-6
  if odd: stats['odd'].append(i)
  out[i]={'sku':sku,'old':J,'cost':c,'retail':retail(c),'st':st,'odd':odd}
json.dump(out,open('price_out.json','w'))
print({k:(v if not isinstance(v,list) else len(v)) for k,v in stats.items()})
tot_c=sum(v['cost'] for v in out.values()); tot_r=sum(v['retail'] for v in out.values())
net=sum(v['retail']-v['cost']-0.029*v['retail']-0.30 for v in out.values())
import statistics
print('blended gross',round(1-tot_c/tot_r,4),'net',round(net/tot_r,4),'median gross',round(statistics.median(1-v['cost']/v['retail'] for v in out.values()),4),'median markup',round(statistics.median(v['retail']/v['cost']-1 for v in out.values()),4))
ch=[v for v in out.values() if v['st']=='changed']
print('changes up',sum(1 for v in ch if v['cost']>v['old']),'down',sum(1 for v in ch if v['cost']<v['old']))
print(sorted(ch,key=lambda v:-abs(v['cost']-v['old']))[:8])
print('nocost sample',stats['nocost'][:40])
# monotonic check
pts=sorted((v['cost'],v['retail']) for v in out.values())
print('mono ok',all(pts[k][1]<=pts[k+1][1] for k in range(len(pts)-1)))
