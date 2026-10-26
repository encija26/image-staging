import openpyxl,json,csv
L=json.load(open('L_new.json'));o=json.load(open('price_out.json'))
ws=openpyxl.load_workbook('sheet2.xlsx',read_only=True,data_only=True)['Modway Curation']
cur={}
for i,r in enumerate(ws.iter_rows(min_row=5,max_col=16,values_only=True),5): cur[i]=r
tp=json.load(open('trade.json'))
def m(x): return f"${x:,.2f}".replace('.00','')
JK={};LL={};HN={}
for k,v in o.items():
  i=int(k); JK[i]=(v['cost'],v['retail'])
  K0=cur[i][10]
  notes=[]
  if v['st']=='changed':
    notes.append(f"Cost updated from the Modway trade portal, {m(v['old'])} to {m(v['cost'])}; retail repriced to ${v['retail']:,}.")
    if v['odd']: notes.append("The portal figure is not a standard trade price, so it may be a temporary sale price. Check before go-live.")
  else:
    try: K0=float(K0)
    except: K0=None
    if K0 is not None and K0!=v['retail']: notes.append(f"Retail corrected to ${v['retail']:,} (was ${K0:,.0f}) to match the pricing model's round-up rule.")
  if notes: HN[i]=notes
for k,(txt,info) in L.items():
  i=int(k)
  if (cur[i][11] or '').strip()!=txt.strip(): LL[i]=txt
  iss=info.get('issues',[])
  n=HN.setdefault(i,[])
  if 'not_on_modway' in iss: n.append("Not found on modway.com, so dimensions could not be checked. Check whether this SKU is discontinued.")
  if 'no_seat_height' in iss: n.append("Seat height not published by Modway. Added to the Secure weights list.")
  if 'dims_filled' in iss: n.append("Product dimensions filled from Modway's spec table.")
nocost=[]
for i,r in cur.items():
  if not r[13] or (r[0] or '').strip()=='Live' or str(i) in o: continue
  sku=str(r[13]).strip(); J=r[9]
  n=HN.setdefault(i,[])
  if J not in (None,''): n.append(f"SKU not listed on the Modway trade portal on Oct 26. Cost {m(float(J))} kept from the trade cost table; check whether this colour is discontinued.")
  else: n.append("No trade cost found on the portal or in the trade cost table. Needs a cost before go-live.")
  nocost.append(i)
HN={i:n for i,n in HN.items() if n}
HH={}
for i,n in HN.items():
  old=(cur[i][7] or '').rstrip()
  add="Pricing and specs, Oct 26: "+" ".join(n)
  HH[i]=(old,(old+"\n\n" if old else "")+add)
mx=max(list(JK)+list(LL)+list(HH))
enc=lambda s:s.replace('\n','¶')
with open('import.csv','w',newline='') as f:
  w=csv.writer(f)
  for i in range(1,mx+1):
    a=JK.get(i,('',''));w.writerow([a[0],a[1],enc(LL.get(i,'')),enc(HH[i][1]) if i in HH else ''])
json.dump({'JK':list(JK),'LL':list(LL),'HH':{i:len(v[0]) for i,v in HH.items()},'nocost':nocost},open('plan.json','w'))
print(len(JK),len(LL),len(HH),len(nocost),mx)
import os;print(os.path.getsize('import.csv'))
