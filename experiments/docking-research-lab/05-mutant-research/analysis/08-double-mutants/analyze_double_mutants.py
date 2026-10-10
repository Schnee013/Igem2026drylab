"""Aggregate completed batch08 scores/contacts against validated historical parents; no science programs."""
import json,sys,math
from rdkit import Chem
from decimal import Decimal as D
from pathlib import Path
from summarize import ROOT,OUT,H,read,track,contact,changes,entries,sha,fmt
BATCH=ROOT/'outputs/batches/08-af3-double-mutants'
sys.path.insert(0,str(BATCH/'cli'))
from configure_received import verify_report,PARAMS
from model_selection import load_manifest
from contacts_received import INTERACTIONS

def verify_historical(path):
    report=read(path)
    for name,h in report['files'].items():
        name=name.replace('/05-af3-saturation-combinations/','/05-af3-n84-v110-v368-saturations/')
        actual=Path(name)
        assert sha(actual)==h, f'Historical source changed: {actual}'
        track(actual)
    return report

def check_contact_protocol(run):
    meta=read(run/'top1_contacts/ifp/metadata.json')
    assert meta['prolif_version']=='2.1.0' and meta['n_poses']==1
    assert meta['vicinity_cutoff_A']==6.0 and meta['interactions']==INTERACTIONS

def load_existing(r):
    r=dict(r);run=ROOT/r['source']
    for lig in ['ascr3','ascr18']:
        for report in ['config_provenance.json','docking_validation.json']:
            verify_historical(run/lig/report)
        check_contact_protocol(run/lig)
        fresh=contact(run/lig)
        assert fresh['score']==r[lig]['score'] and fresh['contacts']==r[lig]['contacts']
        r[lig]=fresh
        cfg=read(run/lig/'run.json')
        assert int(cfg['config']['values']['seed'])==1919 and cfg['runtime_overrides']['cpu']==4
        for k,v in PARAMS.items():assert float(cfg['config']['values'][k])==v
    return r

def geometry(a,b):
    paths=[track(ROOT/r['source']/'top1.sdf') for r in [a,b]]
    mols=[Chem.RemoveHs(Chem.SDMolSupplier(str(p),removeHs=False)[0]) for p in paths]
    assert Chem.MolToSmiles(mols[0],isomericSmiles=True)==Chem.MolToSmiles(mols[1],isomericSmiles=True)
    matches=mols[1].GetSubstructMatches(mols[0],uniquify=False,useChirality=True,maxMatches=10000)
    assert matches and len(matches)<10000
    aa=mols[0].GetConformer().GetPositions();bb=mols[1].GetConformer().GetPositions()
    rmsd=min(math.sqrt(sum(sum((aa[i][k]-bb[j][k])**2 for k in range(3)) for i,j in enumerate(match))/len(aa)) for match in matches)
    return {'heavy_atom_rmsd_no_fit_A':rmsd,'centroid_shift_A':float(sum((aa.mean(axis=0)-bb.mean(axis=0))**2)**0.5),'atom_count':len(aa),'method':'same stereochemical graph; minimum over equivalent atom mappings; shared receptor-aligned frame; no ligand fitting'}

def main():
    source=read(OUT/'data/single-mutants.json');manifest=read(BATCH/'manifests/double-mutants.json');received=load_manifest(BATCH)
    track(BATCH/'manifests/received-af3.json')
    wt={k:load_existing(source['WT'][k]) for k in ['05','07']}
    parent_names={p['variant'] for r in manifest['variants'] for p in r['parents']}
    parents={n:load_existing(next(r for r in source['records'] if r['variant']==n and r['batch']==('07' if n.startswith('W338') else '05'))) for n in sorted(parent_names)}
    def metrics(r,w):
        x=D(r['S3'])-D(w['S3']);y=D(r['S18'])-D(w['S18']);return {'deltaS3':str(x),'deltaS18':str(y),'D':str(y-x)}
    for p in parents.values():p['common_WT05']=metrics(p,wt['05'])
    rows=[]
    for design,j in zip(manifest['variants'],received['jobs']):
        assert design['id']==j['id']
        run=BATCH/'run-01'/j['alias'];al=read(run/'alignment.json');assert al['matched_ca_count']==153
        for name in ['alignment_provenance.json','preparation_validation.json']:
            verify_report(run/name);track(run/name)
        assert read(run/'af_model_selection.json')['af_model']==0
        cs={lig:contact(run/lig) for lig in ['ascr3','ascr18']}
        for lig in cs:
            check_contact_protocol(run/lig)
            for name in ['config_provenance.json','docking_validation.json','top1_contacts/validation.json']:
                verify_report(run/lig/name);track(run/lig/name)
            cfg=read(run/lig/'run.json');assert cfg['runtime_overrides']=={'cpu':4,'spacing':0.375,'min_rmsd':1.0,'max_evals':0}
            for k,v in PARAMS.items():assert float(cfg['config']['values'][k])==v
            assert cfg['inputs']['ligand']['sha256']==read(ROOT/wt['05']['source']/lig/'run.json')['inputs']['ligand']['sha256']
        r={'batch':'08','run':'run-01','variant':j['id'],'alias':j['alias'],'record_id':f"08/run-01/{j['id']}/af0/seed1919",'module':design['module'],'role':design['role'],'af_model':0,'seed':1919,'cpu':4,'source':str(run.relative_to(ROOT)),'rmsd_A':al['ca_rmsd_after_angstrom'],'S3':cs['ascr3']['score'],'S18':cs['ascr18']['score'],**cs}
        r['G']=str(D(r['S18'])-D(r['S3']));r['baseline_record_id']=wt['05']['record_id'];r['baseline_kind']='reused common WT05, not same-batch WT'
        r['reference_sensitivity']={k:metrics(r,w) for k,w in wt.items()};r.update(r['reference_sensitivity']['05'])
        r['parents']={}
        for name in j['id'].split('_'):
            p=parents[name];dx=D(r['S3'])-D(p['S3']);dy=D(r['S18'])-D(p['S18'])
            r['parents'][name]={'record_id':p['record_id'],'score_change3':str(dx),'score_change18':str(dy),'D_change':str(dy-dx),'contacts':{}}
            for lig in cs:
                a=entries(p[lig]);b=entries(r[lig]);r['parents'][name]['contacts'][lig]={**changes(p[lig],r[lig]),'retained_entries':len(a&b),'parent_entries':len(a),'combination_entries':len(b),'jaccard':len(a&b)/len(a|b),'geometry':geometry(p[lig],r[lig])}
        pa,pb=[parents[n] for n in j['id'].split('_')];r['epsilon']={}
        for k,w in wt.items():
            x=D(r['S3'])-D(pa['S3'])-D(pb['S3'])+D(w['S3']);y=D(r['S18'])-D(pa['S18'])-D(pb['S18'])+D(w['S18']);r['epsilon'][k]={'S3':str(x),'S18':str(y),'D':str(y-x)}
        rows.append(r)
    p=OUT/'data/combination-mutants.json';previous=json.loads(p.read_text());historic=[r for r in previous['records'] if r['batch']!='08']
    result={'schema_version':2,'definition':'D=deltaS18-deltaS3; batch08 common WT05, WT07 sensitivity; historical records retain declared baseline','WT':previous['WT'],'parents_batch08':parents,'records':historic+rows,'batch08_audit':{'combinations':18,'docking_runs':36,'contact_runs':36,'parents':14,'WT':2,'all_AF_models':0,'all_selected_Vina_models':sorted({r[l]['model'] for r in rows for l in cs}),'min_rmsd_A':min(r['rmsd_A'] for r in rows),'max_rmsd_A':max(r['rmsd_A'] for r in rows)},'source_sha256':{**previous.get('source_sha256',{}),**H}}
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# 双突变评分与亲本比较','', '08批18个组合；单位kcal/mol。主参照05-WT，敏感性07-WT。只取最低分pose。完整接触增减与来源哈希见[data/combination-mutants.json](data/combination-mutants.json)。','', '| 模块 | 组合 | S3 | S18 | ΔS3 | ΔS18 | D05 | D07 | 接触#3/#18 | TM RMSD Å |','|---|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for r in rows:lines.append('| '+' | '.join([r['module'],r['variant'],r['S3'],r['S18'],fmt(r['deltaS3']),fmt(r['deltaS18']),fmt(r['D']),fmt(r['reference_sensitivity']['07']['D']),f"{r['ascr3']['count']}/{r['ascr18']['count']}",f"{r['rmsd_A']:.3f}"])+' |')
    lines+=['','## 亲本原始评分及统一WT换算','', '| 亲本 | 批次 | S3 | S18 | ΔS3_WT05 | ΔS18_WT05 | D05 |','|---|---|---:|---:|---:|---:|---:|']
    for n,p in parents.items():lines.append(f"| {n} | {p['batch']} | {p['S3']} | {p['S18']} | {fmt(p['common_WT05']['deltaS3'])} | {fmt(p['common_WT05']['deltaS18'])} | {fmt(p['common_WT05']['D'])} |")
    lines+=['','## 逐亲本增益与接触保留','', 'δ=S(组合)−S(亲本)，负值为评分降低；δD不依赖共同WT。保留条目按原编号＋接触类型匹配，残基身份变化另记于JSON；Jaccard不是配体坐标RMSD。','', '| 组合 | 亲本 | δS3 | δS18 | δD | #3保留/亲本条目 | #18保留/亲本条目 |','|---|---|---:|---:|---:|---|---|']
    for r in rows:
        for n,p in r['parents'].items():lines.append('| '+' | '.join([r['variant'],n,fmt(p['score_change3']),fmt(p['score_change18']),fmt(p['D_change']),*[f"{p['contacts'][l]['retained_entries']}/{p['contacts'][l]['parent_entries']}" for l in ['ascr3','ascr18']]])+' |')
    lines+=['','## 非加和残差','', 'ε_i=S_i(AB)−S_i(A)−S_i(B)+S_i(WT)。跨独立AF结构计算，不能视为实验协同或显著性。','', '| 组合 | ε3_WT05 | ε18_WT05 | εD_WT05 | εD_WT07 |','|---|---:|---:|---:|---:|']
    for r in rows:lines.append(f"| {r['variant']} | {fmt(r['epsilon']['05']['S3'])} | {fmt(r['epsilon']['05']['S18'])} | {fmt(r['epsilon']['05']['D'])} | {fmt(r['epsilon']['07']['D'])} |")
    lines+=['','## 最低分配体坐标比较','', '在共同受体参考坐标系中，对同一种配体的重原子按相同立体化学图匹配，并在等价原子映射间取最小RMSD；不再拟合配体。质心指重原子几何中心。该量同时反映位置、朝向和构象变化，不能单独分解受体局部变化的贡献。','', '| 组合 | 亲本 | #3 RMSD Å | #3质心位移 Å | #18 RMSD Å | #18质心位移 Å |','|---|---|---:|---:|---:|---:|']
    for r in rows:
        for n,p in r['parents'].items():
            values=[p['contacts'][l]['geometry'][k] for l in ['ascr3','ascr18'] for k in ['heavy_atom_rmsd_no_fit_A','centroid_shift_A']]
            lines.append('| '+r['variant']+' | '+n+' | '+' | '.join(f'{v:.3f}' for v in values)+' |')
    (OUT/'double-mutant-scores.md').write_text('\n'.join(lines)+'\n')
    print('COMPARISON PASS:',json.dumps(result['batch08_audit']))
if __name__=='__main__':main()
