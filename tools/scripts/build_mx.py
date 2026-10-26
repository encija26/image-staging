import json,re,sys,os
from openpyxl import Workbook
B='/home/claude/bh/b3/'
F=json.load(open(B+'out/final.json'));rows=json.load(open(B+'rows.json'));P=json.load(open(B+'pricing.json'))
PL=json.load(open(B+'img/plan.json'));plan=PL['plan'];cls=PL['cls']
skip=set(json.load(open(B+'img/skip.json'))) if os.path.exists(B+'img/skip.json') else set()
base='https://raw.githubusercontent.com/encija26/image-staging/main/modway/batch3/'
def para_rt(text,mode):
  ch=[]
  for para in [p for p in text.split('\n\n') if p.strip()]:
    if mode=='L':
      m=re.match(r'([A-Z][^:\n]{0,40}:)\s*(.*)',para,re.S)
      kids=[{"type":"text","value":m.group(1)+' ',"bold":True},{"type":"text","value":m.group(2).strip()}] if m else [{"type":"text","value":para}]
    else:
      if '\n' in para:
        h,b=para.split('\n',1);kids=[{"type":"text","value":h.strip(),"bold":True},{"type":"text","value":"\n"+b.strip()}]
      else: kids=[{"type":"text","value":para}]
    ch.append({"type":"paragraph","children":kids})
  return json.dumps({"type":"root","children":ch},ensure_ascii=False)
ALT={'front':'front view','angle':'three-quarter view showing the full profile','side':'side view showing the depth','back':'rear view','top':'shown from above','top-angle':'shown from above at an angle','open':'shown opened out'}
hdr=['Handle','Command','Title','Body HTML','Vendor','Type','Tags','Tags Command','Status','Published','Template Suffix','Category: ID',
'Metafield: title_tag [string]','Metafield: description_tag [string]','Metafield: custom.materials_and_dimensions [rich_text_field]','Metafield: custom.care_and_notes [rich_text_field]','Metafield: custom.source_vendor [single_line_text_field]','Metafield: custom.lead_time [single_line_text_field]',
'Option1 Name','Option1 Value','Variant Command','Variant SKU','Variant Price','Variant Cost','Variant Taxable','Variant Inventory Tracker','Variant Inventory Policy','Variant Fulfillment Service','Variant Requires Shipping','Variant Inventory Qty','Variant Image','Variant Weight Unit','Variant Metafield: custom.ships_from [date]',
'Image Src','Image Command','Image Position','Image Alt Text']
only=set(sys.argv[1].split(',')) if len(sys.argv)>1 and sys.argv[1] else None
out=sys.argv[2] if len(sys.argv)>2 else B+'mx/BH_Modway_Batch3.xlsx'
OUT=[];report=[]
for nm,p in F['products'].items():
  if only and p['handle'] not in only: continue
  rs=[str(r) for r in sorted(p['rows'],key=lambda r:r)]
  rs=[r for r in rs if r not in skip and plan.get(r)]
  if not rs: report.append(('NOIMG',nm));continue
  r0=F['rows'][rs[0]]
  name=re.sub(r'^BH \| Studio\s*','',r0['D'].replace('\n',' ')).split(' — In')[0].strip()
  lead='Ships Now' if any(P[r]['qty']>0 for r in rs) else 'Ships Later'
  body=''.join(f'<p>{x.strip()}</p>' for x in r0['G'].split('\n\n') if x.strip())
  pos=0;first=True
  for r in rs:
    R=F['rows'][r];colour=rows[r]['P'].strip();pr=P[r]
    for i,im in enumerate(plan[r]):
      pos+=1;row={h:'' for h in hdr}
      slot=im['slot']
      if slot=='detail':
        alt=f"Close view of {cls[r].get('detail_feature') or R.get('detail_alt_feature') or 'the detail'} on the {name} in {colour}."
      else:
        alt=f"{name} in {colour}, {ALT.get(slot,slot)}."+((' '+R.get('materials_alt','')) if slot in('front',) or (i==0 and slot!='front') else '')
      row.update({'Handle':p['handle'],'Image Src':base+im['out'],'Image Command':'REPLACE','Image Position':pos,'Image Alt Text':alt.strip()})
      if i==0:
        stock=pr['qty']>0
        row.update({'Option1 Name':'Color','Option1 Value':colour,'Variant Command':'MERGE','Variant SKU':rows[r]['N'].strip(),'Variant Price':pr['retail'],'Variant Cost':pr['cost'],'Variant Taxable':'TRUE',
          'Variant Inventory Tracker':'shopify' if stock else '','Variant Inventory Policy':'deny' if stock else 'continue',
          'Variant Fulfillment Service':'manual','Variant Requires Shipping':'TRUE','Variant Inventory Qty':pr['qty'] if stock else '',
          'Variant Image':base+im['out'],'Variant Weight Unit':'lb','Variant Metafield: custom.ships_from [date]':pr['ships_from'] if pr['ships_from'] not in('','NODATE') else ''})
      if first:
        row.update({'Command':'NEW','Title':'BH | Studio '+name,'Body HTML':body,'Vendor':'Bramley House','Type':p['type'],'Tags':p['tags'],'Tags Command':'REPLACE','Status':'Active','Published':'TRUE',
          'Template Suffix':p['template'],'Category: ID':p['category_id'],'Metafield: title_tag [string]':p['seo_title'],'Metafield: description_tag [string]':p['seo_desc'],
          'Metafield: custom.materials_and_dimensions [rich_text_field]':para_rt(R['L'],'L'),'Metafield: custom.care_and_notes [rich_text_field]':para_rt(R['M'],'M'),
          'Metafield: custom.source_vendor [single_line_text_field]':'modway','Metafield: custom.lead_time [single_line_text_field]':lead})
        first=False
      OUT.append(row)
os.makedirs(os.path.dirname(out),exist_ok=True)
wb=Workbook();ws=wb.active;ws.title='Products';ws.append(hdr)
for r in OUT: ws.append([r[h] for h in hdr])
wb.save(out);print(out,len(OUT),'rows;',report)
