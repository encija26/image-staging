import sys,os,concurrent.futures as cf
sys.path.insert(0,'/home/claude/bh/scripts');from cutout import cut
B='/home/claude/bh/b3/';os.makedirs(B+'img/out',exist_ok=True)
jobs=[l.split('\t') for l in open(B+'img/jobs.txt').read().split('\n') if l]
def go(j):
  s,o,p=j;dst=B+'img/out/'+o
  if os.path.exists(dst): return o,None
  try: return o,cut(B+s,dst,252 if p=='1' else 238,255 if p=='1' else 250)
  except Exception as e: return o,'ERR '+str(e)
with cf.ProcessPoolExecutor(2) as ex:
  for i,(o,r) in enumerate(ex.map(go,jobs)):
    if i%100==0: print(i,o,r,flush=True)
print('DONE',len(jobs),flush=True)
