#!/usr/bin/env python3
"""Combine preparation review snapshots without merging distinct WT identities."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def export(snapshot, destination, identity):
    data=json.loads(snapshot.read_text());lines=[f'TITLE     {identity}',f'REMARK 900 SOURCE GRO SHA256 {data["source_sha256"]}']
    for i,a in enumerate(data['atoms'],1):
        rec='ATOM' if a['resnum']<=406 else 'HETATM';res=a['resname'] if a['resnum']<=406 else 'LIG';chain='A' if a['resnum']<=406 else 'L'
        lines.append(f'{rec:<6}{i:5d} {a["atomname"]:>4s} {res:3s} {chain}{a["resnum"]:4d}    '+''.join(f'{v*10:8.3f}' for v in a['xyz_nm'])+f'  1.00  0.00          {a["atomname"][0]:>2s}')
    destination.write_text('\n'.join(lines)+'\nEND\n')
    return {'path':str(destination),'snapshot_source':str(snapshot),'source_gro_sha256':data['source_sha256'],'identity':identity}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--legacy-root',type=Path,required=True);ap.add_argument('--native-root',type=Path,required=True);a=ap.parse_args()
    out=a.legacy_root/'results';combined=[];exports=[];matrices={};sources=[];files=[]
    for family,root in [('legacy',a.legacy_root),('independent_wt',a.native_root)]:
        state=root/'results/e2_review/preheat_status.json';data=json.loads(state.read_text())
        matrix=root/'inputs/matrix02/matrix.json';m=json.loads(matrix.read_text());matrices[family]=m
        selected_path=root/'results/e2_review/selected_run_manifest.json'
        selected={x['case']:x for x in json.loads(selected_path.read_text())['cases']}
        files.append((selected_path,f'inputs/{family}_selected_run_manifest.json'))
        sources.append({'family':family,'status_file':str(state),'status_sha256':digest(state),'as_of_utc':data['as_of_utc'],'matrix_file':str(matrix),'matrix_sha256':digest(matrix)})
        for c in data['cases']:
            ci=next(x for x in m['cases'] if x['id']==c['case'])
            backmut=family=='legacy' and ci['genotype']=='wt'
            identity='INDEPENDENT WT AF3 MODEL 0' if family=='independent_wt' else 'N84V-DERIVED V84N BACK-MUTATED WT' if backmut else ci['genotype'].upper()
            title='独立 WT' if family=='independent_wt' else '回变构建 WT' if backmut else ci['genotype'].upper()
            label=f'{title}–{ci["ligand"]} / '+('重建 lid' if ci['lid']=='rebuilt' else '原始全长 lid')
            item={**c,'family':family,'display_name':label,'receptor_identity':identity,'pose_source':m['ligand_mappings'][ci['pose_mapping']]['seed'],
                  'selected_preparation':selected.get(c['case'])}
            combined.append(item)
            if c['status']!='preheat_qc_pass':continue
            for phase in ['initial','hold']:
                snap=root/'results/e2_review/snapshots'/f'{c["case"]}_{phase}.json';dest=out/f'{c["case"]}_{phase}_complex.pdb'
                exports.append(export(snap,dest,identity+' / '+phase));files.append((dest,dest.name))
    summary={'source_views':sources,'cases':combined,'completed_preheats':sum(c['status']=='preheat_qc_pass' for c in combined),'total':len(combined),
             'scope':'Preparation results only. Independent WT and back-mutated WT have different starting structures and poses; not a matched common-backbone ensemble.'}
    (out/'combined_preheat_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    (out/'review_export_manifest.json').write_text(json.dumps({'structures':exports},ensure_ascii=False,indent=2))
    with (out/'运行清单.csv').open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.writer(h);w.writerow(['组合及来源','状态','预热末态lid配体最近距离Å','配体pose来源','E2结果目录'])
        for c in combined:w.writerow([c['display_name'],'完成125ps' if c['status']=='preheat_qc_pass' else '尚未完成',c.get('geometry',{}).get('lid_ligand_min_heavy_A'),c['pose_source'],c.get('directory','')])
    for name in ['combined_preheat_summary.json','review_export_manifest.json','运行清单.csv','lid_preheat_first_two.png','lid_preheat_first_two.svg']:
        files.append((out/name,name))
    if (out/'production_launch.json').exists():
        files.append((out/'production_launch.json','production_launch.json'))
    files.extend([(a.legacy_root/'runs/refine_open03/candidate_0001.pdb','rebuilt_lid_candidate.pdb'),
                  (a.legacy_root/'inputs/matrix02/matrix.json','inputs/legacy_matrix.json'),
                  (a.native_root/'inputs/matrix02/matrix.json','inputs/independent_wt_matrix.json')])
    manifest={'source_views':sources,'completed_preheats':summary['completed_preheats'],'total':summary['total'],
              'note':'Full-length receptor/ligand review snapshots only; complete membrane/water trajectories and restart files remain on E2. Old back-mutated WT retained.',
              'files':[{'name':name,'sha256':digest(path)} for path,name in files]}
    (out/'review_bundle_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(out/'Gpr2_lid_预热结果.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path,name in files:z.write(path,name)
        z.write(out/'review_bundle_manifest.json','review_bundle_manifest.json')
        z.writestr('预热结果.md',(out/'预热结果.md').read_text().replace(str(out)+'/', ''))
    print(json.dumps({'completed':summary['completed_preheats'],'total':summary['total'],'snapshot_files':len(exports),'zip_bytes':(out/'Gpr2_lid_预热结果.zip').stat().st_size}))


if __name__=='__main__':main()
