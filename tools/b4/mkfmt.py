import json,re,openpyxl
p=json.load(open('plan.json'));L=json.load(open('L_new.json'))
SID=860942802;RED={"red":0.7529412}
u16=lambda s:len(s.encode('utf-16-le'))//2
def groups(rs):
  rs=sorted(int(r) for r in rs);g=[];s=e=None
  for r in rs:
    if s is None: s=e=r
    elif r==e+1: e=r
    else: g.append((s,e));s=e=r
  if s is not None: g.append((s,e))
  return g
def lruns(t):
  t=t.strip();runs=[];pos=0
  for para in t.split('\n\n'):
    m=re.match(r'([A-Z][^:\n]{0,40}:)',para)
    if m:
      runs.append({"startIndex":pos,"format":{"bold":True}})
      runs.append({"startIndex":pos+u16(m.group(1)),"format":{"bold":False}})
    pos+=u16(para)+2
  if runs and runs[0]['startIndex']==0: pass
  return runs
req=[]
TF={"foregroundColor":RED,"fontFamily":"Arial","fontSize":9}
for s,e in groups(p['JK']):
  req.append({"repeatCell":{"range":{"sheetId":SID,"startRowIndex":s-1,"endRowIndex":e,"startColumnIndex":9,"endColumnIndex":11},"cell":{"userEnteredFormat":{"textFormat":TF}},"fields":"userEnteredFormat.textFormat"}})
for s,e in groups(p['LL']):
  rows=[{"values":[{"userEnteredFormat":{"textFormat":TF,"wrapStrategy":"WRAP"},"textFormatRuns":lruns(L[str(r)][0])}]} for r in range(s,e+1)]
  req.append({"updateCells":{"start":{"sheetId":SID,"rowIndex":s-1,"columnIndex":11},"rows":rows,"fields":"userEnteredFormat.textFormat,userEnteredFormat.wrapStrategy,textFormatRuns"}})
for s,e in groups(p['HH']):
  rows=[]
  for r in range(s,e+1):
    n=p['HH'][str(r)]
    # need utf16 length of old text; recompute
    rows.append(r)
  req.append(('H',s,e))
# H: compute from sheet2
ws=openpyxl.load_workbook('sheet2.xlsx',read_only=True,data_only=True)['Modway Curation']
cur={i:r[7] for i,r in enumerate(ws.iter_rows(min_row=5,max_col=8,values_only=True),5)}
out=[]
for x in req:
  if isinstance(x,tuple):
    _,s,e=x;rows=[]
    for r in range(s,e+1):
      old=(cur[r] or '').rstrip();st=u16(old)+2 if old else 0
      runs=([{"startIndex":0,"format":{}}] if st else [])+[{"startIndex":st,"format":{"foregroundColor":RED}}]
      rows.append({"values":[{"textFormatRuns":runs}]})
    out.append({"updateCells":{"start":{"sheetId":SID,"rowIndex":s-1,"columnIndex":7},"rows":rows,"fields":"textFormatRuns"}})
  else: out.append(x)
s=json.dumps(out,separators=(',',':'));print(len(out),len(s))
json.dump(out,open('freq.json','w'),separators=(',',':'))
