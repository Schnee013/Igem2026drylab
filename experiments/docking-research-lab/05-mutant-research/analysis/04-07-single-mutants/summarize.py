"""Rebuild analysis tables from existing batch outputs; no scientific programs run."""
import argparse,csv,hashlib,json,re,statistics
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
H={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def track(p):H[str(p.relative_to(ROOT))]=sha(p);return p
def read(p):return json.loads(track(p).read_text())
def entries(c):return {(int(n),t) for n,v in c['contacts'].items() for t in v['types']}
def fmt(x):return f'{D(str(x)):+.3f}'
def contact(run):
 folder=run/'top1_contacts';sel=read(folder/'selection.json');meta=read(folder/'ifp/metadata.json')
 assert sel['source_sha256']==sha(run/'poses.pdbqt') and sel['analyzed_pose_count']==1
 assert meta['n_poses']==1 and meta['receptor_sha256']==sha(run.parent/'receptor.json') and meta['sdf_sha256']==sha(folder/'top1.sdf')
 with track(folder/'contact_residues.csv').open() as f:rows=list(csv.DictReader(f))
 c={r['original_number']:{'residue':r['residue'],'types':sorted(r['interaction_types'].split(';'))} for r in rows}
 with track(folder/'ifp/ifp_presence.csv').open() as f:table=list(csv.reader(f))
 assert len(table)==5
 parsed={}
 for i,v in enumerate(table[4][1:],1):
  if v.lower()=='true':parsed.setdefault(table[1][i],set()).add(table[2][i])
 assert parsed=={x['residue']:set(x['types']) for x in c.values()}
 summary=read(run/'summary.json');score,mode=min((D(str(v['affinity_kcal_per_mol'])),v['mode']) for v in summary['modes'])
 poses=track(run/'poses.pdbqt').read_text();ps=[]
 for m,body in re.findall(r'^MODEL\s+(\d+)[^\n]*\n(.*?)^ENDMDL',poses,re.M|re.S):ps.append((D(re.search(r'^REMARK VINA RESULT:\s+([-+\d.eE]+)',body,re.M)[1]),int(m)))
 assert (score,mode)==min(ps)==(D(str(sel['vina_score_kcal_mol'])),sel['selected_original_mode'])
 return {'score':str(score),'model':mode,'poses':len(ps),'count':len(c),'entry_count':sum(len(v['types']) for v in c.values()),'contacts':c,'source':str(folder.relative_to(ROOT))}
def changes(w,m):
 a=entries(w);b=entries(m)
 def labels(xs,c):return [c['contacts'][str(n)]['residue']+':'+t for n,t in sorted(xs)]
 return {'gained':labels(b-a,m),'lost':labels(a-b,w),'gained_residues':[m['contacts'][n]['residue'] for n in sorted(m['contacts'].keys()-w['contacts'].keys(),key=int)],'lost_residues':[w['contacts'][n]['residue'] for n in sorted(w['contacts'].keys()-m['contacts'].keys(),key=int)],'identity_changes':[{'number':int(n),'wt':w['contacts'][n]['residue'],'mutant':m['contacts'][n]['residue']} for n in sorted(w['contacts'].keys()&m['contacts'].keys(),key=int) if w['contacts'][n]['residue']!=m['contacts'][n]['residue']]}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-only',action='store_true');args=p.parse_args()
 records=[];wt={}
 for batch in sorted((ROOT/'outputs/batches').iterdir()):
  if not re.match(r'^\d\d-',batch.name) or not 4<=int(batch.name[:2])<=7:continue
  tag=batch.name[:2];base=batch/'run-01'
  if not base.exists():continue
  for run in sorted(base.iterdir()):
   if not (run/'input.pdb').is_file():continue
   alias=run.name;variant=re.sub(r'^\d\d_','',alias).upper();variant='baseline' if variant=='BASELINE' else variant
   c={lig:contact(run/lig) for lig in ['ascr3','ascr18']}
   config=read(run/'ascr3/run.json');config18=read(run/'ascr18/run.json')
   assert config['return_code']==config18['return_code']==0
   seed=int(config['config']['values']['seed']);assert seed==int(config18['config']['values']['seed'])
   model=read(run/'af_model_selection.json')['af_model'] if (run/'af_model_selection.json').exists() else 0
   r={'batch':tag,'run':'run-01','variant':variant,'alias':alias,'af_model':model,'seed':seed,'cpu':config['runtime_overrides']['cpu'],'source':str(run.relative_to(ROOT)),'rmsd_A':read(run/'alignment.json')['ca_rmsd_after_angstrom'],'S3':c['ascr3']['score'],'S18':c['ascr18']['score'],**c}
   r['record_id']=f'{tag}/run-01/{variant}/af{model}/seed{seed}';r['G']=str(D(r['S18'])-D(r['S3']))
   if variant=='baseline':wt[tag]=r
   else:records.append(r)
 for r in records:
  w=wt[r['batch']];r['baseline_record_id']=w['record_id'];r['reference_sensitivity']={}
  for tag,base in wt.items():
   a=D(r['S3'])-D(base['S3']);b=D(r['S18'])-D(base['S18']);r['reference_sensitivity'][tag]={'deltaS3':str(a),'deltaS18':str(b),'D':str(b-a)}
  r.update(r['reference_sensitivity'][r['batch']]);r['D_source']=r['D'];r['contact_changes_vs_source_WT']={}
  for lig in ['ascr3','ascr18']:
   c=r[lig];bc=w[lig];e=entries(c);we=entries(bc)
   c.update(changes=changes(bc,c),jaccard_to_WT=len(e&we)/len(e|we),gained_entries=len(e-we),lost_entries=len(we-e))
   r['contact_changes_vs_source_WT'][lig]=c['changes']
 singles=[r for r in records if re.fullmatch(r'[A-Z]\d+[A-Z]',r['variant'])];combos=[r for r in records if r not in singles]
 assert len({r['record_id'] for r in records})==len(records)
 selection=ROOT/'outputs/batches/07-af3-w338-saturation/manifests/w338c-model-selection.json';track(selection)
 panel=[r for r in singles if (r['batch']=='05' and r['variant'][:-1] in ['N84','V110','V368']) or (r['batch']=='07' and r['variant'][:-1]=='W338')]
 assert len(panel)==76
 stats={}
 for site in ['N84','V110','V368','W338']:
  rr=[r for r in panel if r['variant'][:-1]==site];ds=[D(r['D']) for r in rr]
  stats[site]={'n':len(rr),'D_positive':sum(x>0 for x in ds),'D_negative':sum(x<0 for x in ds),'D_zero':sum(x==0 for x in ds),'D_median':str(statistics.median(ds)),'D_min':str(min(ds)),'D_max':str(max(ds)),'both_improve':sum(D(r['deltaS3'])<0 and D(r['deltaS18'])<0 for r in rr),'only3_improves':sum(D(r['deltaS3'])<0 and D(r['deltaS18'])>0 for r in rr),'only18_improves':sum(D(r['deltaS3'])>0 and D(r['deltaS18'])<0 for r in rr),'both_worse':sum(D(r['deltaS3'])>0 and D(r['deltaS18'])>0 for r in rr),'contacts':{}}
  for lig in ['ascr3','ascr18']:
   cs=[r[lig] for r in rr]
   def has(c,n,t=None):return str(n) in c['contacts'] and (t is None or t in c['contacts'][str(n)]['types'])
   stats[site]['contacts'][lig]={'median_residues':statistics.median(c['count'] for c in cs),'range_residues':[min(c['count'] for c in cs),max(c['count'] for c in cs)],'median_jaccard':statistics.median(c['jaccard_to_WT'] for c in cs),'direct_site_count':sum(has(c,int(site[1:])) for c in cs),'R189_Anionic':sum(has(c,189,'Anionic') for c in cs),'338_Hydrophobic':sum(has(c,338,'Hydrophobic') for c in cs),'R189_Anionic_and_338_Hydrophobic':sum(has(c,189,'Anionic') and has(c,338,'Hydrophobic') for c in cs),'residue_frequency':{str(n):sum(has(c,n) for c in cs) for n in sorted({int(n) for c in cs for n in c['contacts']})}}
 payload={'schema_version':1,'definition':'D=deltaS18-deltaS3; each source WT; minimum-score pose only; no pooled ranking','WT':wt,'records':singles,'saturation_view':{'record_ids':[r['record_id'] for r in panel],'site_statistics':stats},'source_sha256':H}
 print(f'SUMMARY PASS: {len(singles)} single-mutant records; {len({r["variant"] for r in singles})} designs; {len(wt)} WT; {len(combos)} combinations; 76 saturation records')
 if args.check_only:return
 for name,rows in [('single-mutants',singles),('combination-mutants',combos)]:
  obj=payload if name=='single-mutants' else {'definition':payload['definition'],'WT':wt,'records':rows,'source_sha256':H}
  if name=='combination-mutants' and (OUT/'data/combination-mutants.json').exists():
   previous=json.loads((OUT/'data/combination-mutants.json').read_text())
   newer=[r for r in previous['records'] if int(r['batch'])>7]
   if newer:
    obj={**previous,'records':rows+newer,'WT':wt,'source_sha256':{**previous.get('source_sha256',{}),**H}}
  (OUT/'data').mkdir(exist_ok=True)
  (OUT/'data'/f'{name}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
  if name=='combination-mutants':continue
  lines=[f'# Phase2：{"单突变" if name=="single-mutants" else "组合突变"}完整记录','',f'{len(rows)}条结构记录；每条按来源WT计算D=ΔS18−ΔS3。不同批次同设计分别保留，按批次/名称列示，不跨来源D混排。','', '批次04使用cpu=16；05–07使用cpu=4，均以每次最低分pose为主。替代WT敏感性为算术换基线，详见JSON，不能消除结构来源差异。','', '| 批次 | 设计 | S3 | S18 | ΔS3 | ΔS18 | D | 接触残基#3/#18 | AF模型 | seed |','|---|---|---:|---:|---:|---:|---:|---|---:|---:|']
  for r in rows:lines.append('| '+' | '.join([r['batch'],r['variant'],r['S3'],r['S18'],fmt(r['deltaS3']),fmt(r['deltaS18']),fmt(r['D']),f"{r['ascr3']['count']}/{r['ascr18']['count']}",str(r['af_model']),str(r['seed'])])+' |')
  lines+=['','## 来源WT','', '| 批次 | S3 | S18 | G |','|---|---:|---:|---:|']
  for tag,w in wt.items():lines.append(f"| {tag} | {w['S3']} | {w['S18']} | {fmt(w['G'])} |")
  lines+=['',f'每条记录的接触原表、增减条目、WT敏感性、来源及哈希见[完整数据](data/{name}.json)。']
  report_name='single-mutant-scores.md' if name=='single-mutants' else 'combination-mutant-scores.md'
  (OUT/report_name).write_text('\n'.join(lines)+'\n')
 # This view is derived exclusively from the canonical single-mutant data.
 lines=['# 四位点饱和单突变统计','', '数据入口：[完整单突变数据](data/single-mutants.json)。主视图固定选择05的N84/V110/V368和07的W338，各19种；重复设计的其他来源留在完整记录中。每次最低分pose为主，描述统计不作为独立重复或显著性证据。','', '| 位点 | D正/负/零 | D中位数 | D范围 | 两者改善 | 仅#3改善 | 仅#18改善 | 两者变差 |','|---|---|---:|---|---:|---:|---:|---:|']
 for site,s in stats.items():lines.append(f"| {site} | {s['D_positive']}/{s['D_negative']}/{s['D_zero']} | {fmt(s['D_median'])} | {fmt(s['D_min'])}～{fmt(s['D_max'])} | {s['both_improve']} | {s['only3_improves']} | {s['only18_improves']} | {s['both_worse']} |")
 lines+=['','## 接触统计','', '按原编号＋类型匹配；Jaccard为交集/并集条目数，不是坐标RMSD。频数为19个设计中的检出数，不是占有率。','', '| 位点/配体 | 残基中位数（范围） | Jaccard中位数 | 突变位点接触 | R189 Anionic | 338 Hydrophobic | 共现 |','|---|---|---:|---:|---:|---:|---:|']
 for site,s in stats.items():
  for lig,c in s['contacts'].items():lines.append(f"| {site}/{lig} | {c['median_residues']}（{c['range_residues'][0]}–{c['range_residues'][1]}） | {c['median_jaccard']:.3f} | {c['direct_site_count']}/19 | {c['R189_Anionic']}/19 | {c['338_Hydrophobic']}/19 | {c['R189_Anionic_and_338_Hydrophobic']}/19 |")
 for site in stats:
  lines+=['',f'## {site}','', '| 替换 | ΔS3 | ΔS18 | D_source | D_WT04 | D_WT05 | D_WT06 | D_WT07 | #3/#18接触 | TM RMSD Å | AF模型 |','|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|']
  for r in sorted([r for r in panel if r['variant'][:-1]==site],key=lambda r:D(r['D']),reverse=True):lines.append('| '+' | '.join([r['variant'],fmt(r['deltaS3']),fmt(r['deltaS18']),fmt(r['D']),*[fmt(r['reference_sensitivity'][b]['D']) for b in ['04','05','06','07']],f"{r['ascr3']['count']}/{r['ascr18']['count']}",f"{r['rmsd_A']:.3f}",str(r['af_model'])])+' |')
 (OUT/'saturation-statistics.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
