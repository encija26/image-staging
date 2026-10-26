import json,re,os
B='/home/claude/bh/b3/'
F=json.load(open(B+'out/final.json'));rows=json.load(open(B+'rows.json'));P=json.load(open(B+'pricing.json'))
SID=860942802
RED={"red":0.7529,"green":0,"blue":0};GOLD={"red":0.749,"green":0.565,"blue":0}
def runs(text,boldspans):
  rs=[];pos=0
  marks=sorted(boldspans)
  out=[];cur=0
  for a,b in marks:
    if a>cur: out.append((cur,False))
    out.append((a,True));cur=b
  if cur<len(text): out.append((cur,False))
  if not out or out[0][0]!=0: out.insert(0,(0,False))
  res=[];seen=set()
  for s,b in out:
    if s in seen or s>=len(text): continue
    seen.add(s);res.append({"startIndex":s,"format":{"bold":b,"foregroundColorStyle":{"rgbColor":RED}}})
  return res
def L_spans(t):
  sp=[];off=0
  for para in t.split('\n\n'):
    m=re.match(r'([A-Z][^:\n]{0,40}:)',para)
    if m: sp.append((off,off+len(m.group(1))))
    off+=len(para)+2
  return sp
def M_spans(t):
  sp=[];off=0
  for para in t.split('\n\n'):
    first=para.split('\n')[0]
    if '\n' in para: sp.append((off,off+len(first)))
    off+=len(para)+2
  return sp
def cellreq(r,c,val,spans,extra=None,fields="userEnteredValue,textFormatRuns"):
  v={"userEnteredValue":{"stringValue":val},"textFormatRuns":runs(val,spans)}
  if extra: v.update(extra); 
  return {"updateCells":{"range":{"sheetId":SID,"startRowIndex":r-1,"endRowIndex":r,"startColumnIndex":c,"endColumnIndex":c+1},"rows":[{"values":[v]}],"fields":fields}}
reqs={}
def add(k,q): reqs.setdefault(int(k),[]).append(q)
norm=lambda s:(s or '').replace('\r','').strip()
for k,r in F['rows'].items():
  o=rows[k]
  if norm(r['D'])!=norm(o['D']):
    d=r['D']; v={"userEnteredValue":{"stringValue":d},"textFormatRuns":[{"startIndex":0,"format":{"bold":True,"foregroundColorStyle":{"rgbColor":GOLD}}},{"startIndex":12,"format":{"bold":False,"foregroundColorStyle":{"rgbColor":RED}}}]}
    add(k,{"updateCells":{"range":{"sheetId":SID,"startRowIndex":int(k)-1,"endRowIndex":int(k),"startColumnIndex":3,"endColumnIndex":4},"rows":[{"values":[v]}],"fields":"userEnteredValue,textFormatRuns"}})
  if norm(r['G'])!=norm(o['G']):
    add(k,cellreq(int(k),6,r['G'],[],{"userEnteredFormat":{"backgroundColorStyle":{"rgbColor":{"red":1,"green":0.949,"blue":0.8}},"wrapStrategy":"WRAP"},"note":"Claude 25 Oct: "+(r.get('G_note') or 'House Note edited.')},"userEnteredValue,textFormatRuns,userEnteredFormat.backgroundColorStyle,userEnteredFormat.wrapStrategy,note"))
  if norm(r['L'])!=norm(o['L']): add(k,cellreq(int(k),11,r['L'],L_spans(r['L'])))
  if norm(r['M'])!=norm(o['M']): add(k,cellreq(int(k),12,r['M'],M_spans(r['M'])))
  p=P[k]
  if p['sheet_cost']!=p['cost'] or (p['sheet_retail']!=p['retail']):
    add(k,{"updateCells":{"range":{"sheetId":SID,"startRowIndex":int(k)-1,"endRowIndex":int(k),"startColumnIndex":9,"endColumnIndex":11},"rows":[{"values":[
      {"userEnteredValue":{"numberValue":p['cost']},"userEnteredFormat":{"numberFormat":{"type":"CURRENCY","pattern":"$#,##0.00"},"textFormat":{"foregroundColorStyle":{"rgbColor":RED}}}},
      {"userEnteredValue":{"numberValue":p['retail']},"userEnteredFormat":{"numberFormat":{"type":"CURRENCY","pattern":"$#,##0"},"textFormat":{"foregroundColorStyle":{"rgbColor":RED}}}}]}],
      "fields":"userEnteredValue,userEnteredFormat.numberFormat,userEnteredFormat.textFormat.foregroundColorStyle"}})
ks=sorted(reqs)
print(len(ks),'rows to update;',sum(len(v) for v in reqs.values()),'cell writes')
os.makedirs(B+'push',exist_ok=True)
for f in os.listdir(B+'push'): os.remove(B+'push/'+f)
chunk=[];n=0;size=0
for k in ks:
  chunk+=reqs[k];size+=len(json.dumps(reqs[k]))
  if size>45000:
    json.dump(chunk,open(B+f'push/c{n:02d}.json','w'),ensure_ascii=False);n+=1;chunk=[];size=0
if chunk: json.dump(chunk,open(B+f'push/c{n:02d}.json','w'),ensure_ascii=False);n+=1
# wrap+height for touched rows
fmt=[]
for k in ks:
  fmt.append({"updateDimensionProperties":{"range":{"sheetId":SID,"dimension":"ROWS","startIndex":k-1,"endIndex":k},"properties":{"pixelSize":260},"fields":"pixelSize"}})
fmt.append({"repeatCell":{"range":{"sheetId":SID,"startRowIndex":10,"endRowIndex":636,"startColumnIndex":3,"endColumnIndex":13},"cell":{"userEnteredFormat":{"wrapStrategy":"WRAP"}},"fields":"userEnteredFormat.wrapStrategy"}})
json.dump(fmt,open(B+f'push/c{n:02d}_format.json','w'))
print(n+1,'files',[ (f,os.path.getsize(B+'push/'+f)//1000) for f in sorted(os.listdir(B+'push'))])
