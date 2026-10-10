"""Read-only audit of completed runs; optionally write a new score report."""
from model_selection import load_manifest, model_note
import argparse,json,re,math
from decimal import Decimal
from pathlib import Path
from configure_received import ROOT,BATCH,LIGANDS,verify_report,validate_config,require,digest

def main():
    p=argparse.ArgumentParser(); p.add_argument('--write-report',action='store_true'); a=p.parse_args()
    manifest=load_manifest(BATCH); records=[]; warnings=[]
    for j in manifest['jobs']:
        d=BATCH/'run-01'/j['alias']; verify_report(d/'alignment_provenance.json'); verify_report(d/'preparation_validation.json')
        row={'af_model':j['selected_model'],'variant':j['id'],'alias':j['alias'],'rmsd_A':json.loads((d/'alignment.json').read_text())['ca_rmsd_after_angstrom']}
        for lig in ['ascr3','ascr18']:
            f=d/lig; verify_report(f/'config_provenance.json'); validation=verify_report(f/'docking_validation.json')
            validate_config(f/'vina.conf',d/'receptor.pdbqt',LIGANDS/f'{lig}_deprotonated.pdbqt')
            r=json.loads((f/'run.json').read_text()); require(r['return_code']==0 and r['vina_version']=='AutoDock Vina v1.2.5','Run/version failure')
            require(r['runtime_overrides']=={'cpu':4,'spacing':0.375,'min_rmsd':1.0,'max_evals':0},'Runtime mismatch')
            for entry in [r['config'],r['output'],*r['inputs'].values()]: require(digest(Path(entry['path']))==entry['sha256'],'Run hash mismatch')
            text=(f/'poses.pdbqt').read_text(); blocks=re.findall(r'^MODEL\s+(\d+)[^\n]*\n(.*?)^ENDMDL',text,re.M|re.S); scores=[]
            for mode,block in blocks:
                matches=re.findall(r'^REMARK VINA RESULT:\s+([-+\d.eE]+)',block,re.M); require(len(matches)==1,'Missing/duplicate score')
                value=Decimal(matches[0]); require(value.is_finite(),'Nonfinite score'); scores.append((value,int(mode)))
            require(1<=len(scores)<=9 and len({v[1] for v in scores})==len(scores),'Pose inventory mismatch')
            best,mode=min(scores)
            summary=json.loads((f/'summary.json').read_text())
            require(sorted(scores)==sorted((Decimal(str(v['affinity_kcal_per_mol'])),v['mode']) for v in summary['modes']),'Log/pose score mismatch')
            require(validation['pose_count']==len(scores) and Decimal(str(validation['lowest_score']))==best and validation['selected_model']==mode,'Selection mismatch')
            if (f/'vina.stderr.txt').read_text().strip(): warnings.append(str(f/'vina.stderr.txt'))
            row[lig]={'score':str(best),'model':mode,'poses':len(scores),'run_dir':str(f.relative_to(ROOT))}
        records.append(row)
    require(len(records)==20,'Expected 20 receptors')
    wt=next(r for r in records if r['variant']=='baseline')
    for row in records:
        d3=Decimal(row['ascr3']['score'])-Decimal(wt['ascr3']['score']); d18=Decimal(row['ascr18']['score'])-Decimal(wt['ascr18']['score'])
        row.update(deltaS3=str(d3),deltaS18=str(d18),D=str(d18-d3))
    ranked=sorted([r for r in records if r['variant']!='baseline'],key=lambda r:Decimal(r['D']),reverse=True)
    print('AUDIT PASS: 40 runs; hashes, parameters, pose/log agreement and minimum-pose selection verified')
    print('Nonempty stderr logs:',len(warnings))
    for label,rows in [('D positive end',ranked[:5]),('D negative end',list(reversed(ranked[-5:])))]:
        print(label)
        for r in rows: print(r['variant'],r['deltaS3'],r['deltaS18'],r['D'])
    if a.write_report:
        out=BATCH/'run-01/score-audit'; require(not out.exists(),f'Refusing overwrite: {out}'); out.mkdir()
        payload={'run_count':40,'baseline':wt,'records':records,'stderr_logs_to_review':warnings,'definition':'D=deltaS18-deltaS3; minimum-score pose per run; lowest MODEL breaks ties'}
        (out/'scores.json').write_text(json.dumps(payload,indent=2)+'\n')
        lines=['# 批次07：首轮最低分pose评分','',
               '40个任务的来源哈希、冻结参数、日志/构象评分一致性及最低分pose选择核验通过。',
               '',f'本轮WT：ascr#3 = {wt["ascr3"]["score"]}；ascr#18 = {wt["ascr18"]["score"]} kcal/mol。',
               '','ΔS = 突变体−本轮WT；D = ΔS18−ΔS3。正D相对偏向#3，负D相对偏向#18。',
               model_note(manifest),
               '本表为同一seed=1919的一轮评分排序。大幅D需要同时结合两个ΔS判断，评分不能直接解释为实验亲和力。',
               '','| 突变 | S3 | S18 | ΔS3 | ΔS18 | D | #3/#18 MODEL |','|---|---:|---:|---:|---:|---:|---|']
        for r in ranked: lines.append(f'| {r["variant"]} | {r["ascr3"]["score"]} | {r["ascr18"]["score"]} | {r["deltaS3"]} | {r["deltaS18"]} | {r["D"]} | {r["ascr3"]["model"]}/{r["ascr18"]["model"]} |')
        lines+=['','W338替换的局部结构与候选最低分pose需结合PyMOL检查。','',f'非空stderr日志：{len(warnings)}。']
        (out/'scores.md').write_text('\n'.join(lines)+'\n')
        print(out/'scores.md')
if __name__=='__main__': main()
