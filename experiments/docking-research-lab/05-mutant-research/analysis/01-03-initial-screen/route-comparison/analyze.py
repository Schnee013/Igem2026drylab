"""Read existing docking results; compare route-specific score changes. No docking."""
from pathlib import Path
import csv
import hashlib
import json
import os
import re
import statistics as stats

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "vina/src/run_vina.py").is_file())
OUT = Path(__file__).resolve().parent
ROUTES = {'fixed': ROOT/'outputs/batches/01-sidechain-combination/run-01', 'af3': ROOT/'outputs/batches/02-af3-combination/run-01'}
GROUPS = ['baseline', 'N84A_L90A_R345A', 'V110A_R181A_W338A_V368A']
LIGANDS = ['ascr3', 'ascr18']
TM = [n for a,b in [(30,50),(62,83),(101,126),(144,163),(182,201),(326,346),(358,380)] for n in range(a,b+1)]


def write_csv(name, rows):
    with (OUT/name).open('w', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def ca(path):
    return {int(l[22:26]): [float(l[30:38]),float(l[38:46]),float(l[46:54])]
            for l in path.read_text().splitlines() if l.startswith('ATOM') and l[12:16].strip()=='CA'}


def first_pose(path):
    atoms={}
    for l in path.read_text().splitlines():
        if l.startswith('ENDMDL'):break
        if l.startswith(('ATOM','HETATM')) and l.split()[-1] not in ['H','HD','HS']:
            key=(l[6:11].strip(),l[12:16].strip());assert key not in atoms
            atoms[key]=[float(l[30:38]),float(l[38:46]),float(l[46:54])]
    return atoms


def rmsd(a,b,keys):
    return (sum(sum((x-y)**2 for x,y in zip(a[k],b[k])) for k in keys)/len(keys))**0.5


data={};params=[];trace=[];ligand_hashes={l:set() for l in LIGANDS}
for route,folder in ROUTES.items():
    for group in GROUPS:
        for ligand in LIGANDS:
            d=folder/group/ligand;run=json.loads((d/'run.json').read_text());assert run['return_code']==0
            for item in [run['config'],*run['inputs'].values(),run['output']]:
                p=Path(item['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p
                trace.append({'route':route,'group':group,'ligand':ligand,'path':str(p),'sha256':item['sha256']})
            ligand_hashes[ligand].add(run['inputs']['ligand']['sha256'])
            params.append(({k:v for k,v in run['config']['values'].items() if k not in ['receptor','ligand']},run['runtime_overrides'],run['vina_version']))
            scores=[float(x) for x in re.findall(r'^REMARK VINA RESULT:\s+([-\d.]+)',(d/'poses.pdbqt').read_text(),re.M)]
            assert len(scores)==9 and scores==sorted(scores)
            data[route,group,ligand]={'best':scores[0],'top3_mean':stats.mean(scores[:3]),'median9':stats.median(scores)}
assert all(p==params[0] for p in params) and all(len(h)==1 for h in ligand_hashes.values())
rows=[]
for (route,group,ligand),metrics in data.items():
    row={'route':route,'group':group,'ligand':ligand,'n_poses':9}
    for metric,value in metrics.items():
        row[metric]=round(value,6);row['delta_'+metric]=round(value-data[route,'baseline',ligand][metric],6)
    rows.append(row)
write_csv('scores.csv',rows);write_csv('source_trace.csv',trace)
effects=[]
for route in ROUTES:
    for group in GROUPS[1:]:
        for metric in ['best','top3_mean','median9']:
            changes={l:data[route,group,l][metric]-data[route,'baseline',l][metric] for l in LIGANDS}
            effects.append({'route':route,'group':group,'summary':metric,'delta_ascr3':round(changes['ascr3'],6),'delta_ascr18':round(changes['ascr18'],6),'D_ascr18_minus_ascr3':round(changes['ascr18']-changes['ascr3'],6)})
write_csv('differential_response.csv',effects)
geometry=[]
for route,folder in ROUTES.items():
    base=ca(folder/'baseline/input.pdb')
    for group in GROUPS[1:]:
        current=ca(folder/group/'input.pdb')
        for ligand in LIGANDS:
            p=first_pose(folder/group/ligand/'poses.pdbqt');q=first_pose(folder/'baseline'/ligand/'poses.pdbqt');assert p.keys()==q.keys()
            geometry.append({'route':route,'group':group,'ligand':ligand,'TM_CA_RMSD_common_frame_A':round(rmsd(current,base,TM),6),'top_pose_heavy_atom_RMSD_common_frame_A':round(rmsd(p,q,list(p)),6)})
write_csv('geometry_checks.csv',geometry)
(OUT/'validation.json').write_text(json.dumps({'successful_runs':12,'poses_per_run':9,'all_input_output_config_hashes_match':True,'versions_and_parameters_identical':True,'ligand_inputs_identical_across_groups':True,'common_config':params[0],'baseline_TM_CA_RMSD_common_frame_A':rmsd(ca(ROUTES['fixed']/'baseline/input.pdb'),ca(ROUTES['af3']/'baseline/input.pdb'),TM),'pose_RMSD_method':'Same atom serial/name correspondence, common receptor coordinate frame; no ligand fitting or symmetry correction. This is a displacement diagnostic, not a pocket classification.','contact_results_present':{route:len(list(folder.glob('*/*/ifp/metadata.json'))) for route,folder in ROUTES.items()}},indent=2)+'\n')

os.environ.setdefault('MPLCONFIGDIR','/tmp/gpr2-route-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
fig,axes=plt.subplots(1,2,figsize=(11,4.8),sharey=True)
colors=['#2166ac','#d98028'];x=np.arange(2);width=.34
for ax,group,title in zip(axes,GROUPS[1:],['N84A / L90A / R345A','V110A / R181A / W338A / V368A']):
    for i,ligand in enumerate(LIGANDS):
        values=[data[r,group,ligand]['best']-data[r,'baseline',ligand]['best'] for r in ROUTES]
        bars=ax.bar(x+(i-.5)*width,values,width,label=ligand.replace('ascr','ascr#'),color=colors[i])
        for bar,value in zip(bars,values):
            ax.text(bar.get_x()+bar.get_width()/2,value+(.018 if value>=0 else -.018),f'{value:+.3f}',ha='center',va='bottom' if value>=0 else 'top',fontsize=10)
    ax.axhline(0,color='#444',lw=1);ax.set_xticks(x,['Fixed backbone','Full-length AF3\nthen trim']);ax.set_title(title,fontsize=12)
    ax.spines[['top','right']].set_visible(False);ax.set_ylim(-.27,.67)
axes[0].set_ylabel('Mutant − within-route baseline Vina score (kcal/mol)')
axes[1].legend(frameon=False)
fig.suptitle('Mutation-associated docking score changes',fontsize=15)
fig.text(.5,.025,'Best returned pose; one Vina seed per condition. Positive = less favorable score. No experimental ΔΔG inference.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.07,1,.94]);fig.savefig(OUT/'score_changes.png',dpi=180);fig.savefig(OUT/'score_changes.svg');plt.close(fig)
print(json.dumps(effects,indent=2))
