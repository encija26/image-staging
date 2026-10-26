# Usage: make_imgfix.py handles_csv v2dir out.xlsx  -> image-only REPLACE import using -v2 files where present
import sys,subprocess,os,openpyxl,shutil
hs,v2dir,out=sys.argv[1],sys.argv[2],sys.argv[3]
tmp='/tmp/claude-0/-home-claude/c11d7cd1-3db0-5f33-82ed-fdaf2b678021/scratchpad/_full.xlsx'
subprocess.run(['python3','/home/claude/bh/scripts/build_mx.py',hs,tmp],check=True,capture_output=True)
wb=openpyxl.load_workbook(tmp);ws=wb.active;rows=list(ws.iter_rows(values_only=True));h=list(rows[0])
keep=['Handle','Command','Option1 Name','Option1 Value','Variant Command','Variant SKU','Variant Image','Image Src','Image Command','Image Position','Image Alt Text']
v2=set(os.listdir(v2dir));stage='/home/claude/image-staging/modway/batch3/'
o=openpyxl.Workbook();w=o.active;w.title='Products';w.append(keep);n=0;used=set()
for r in rows[1:]:
  d=dict(zip(h,r));d['Command']='MERGE' if d.get('Option1 Value') else None
  for c in ('Image Src','Variant Image'):
    if d.get(c):
      fn=d[c].rsplit('/',1)[1];f2=fn.replace('.webp','-v2.webp')
      if f2 in v2: d[c]=d[c].replace(fn,f2);used.add(f2)
  w.append([d.get(k) or None for k in keep]);n+=1
for f in used: shutil.copy(os.path.join(v2dir,f),stage+f)
o.save(out);print(out,n,'rows',len(used),'v2 files staged')
