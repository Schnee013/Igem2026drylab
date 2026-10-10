"""Audit a Gpr2 structure handoff without modifying source structures.

This is the archived producer for a dated input audit, not an MD metric driver.
Inputs and output location are required command-line arguments.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

AA=dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),'ARNDCQEGHILKMFPSTWYV'))

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def pdb(p):
    out=[]
    for line in p.read_text().splitlines():
        if line[:6].strip() not in ('ATOM','HETATM'): continue
        name=line[12:16].strip()
        elem=line[76:78].strip() if p.suffix!='.pdbqt' else name[0]
        if not elem: elem=name[0]
        if elem.startswith('H'): continue
        out.append(dict(key=(line[21],int(line[22:26]),line[26],name),name=name,resid=int(line[22:26]),resname=line[17:20].strip(),element=elem,xyz=[float(line[x:x+8]) for x in (30,38,46)],b=float(line[60:66])))
    return out

def coords(rows): return np.array([x['xyz'] for x in rows])
def rms(x,y): return float(np.sqrt(np.mean(np.sum((x-y)**2,axis=1))))
def label(a): return f"{a['resname']}{a['resid']}:{a['name']}"

def sdf(p):
    lines=p.read_text().splitlines(); n=int(lines[3][:3]); nb=int(lines[3][3:6]); atoms=[]
    for i,l in enumerate(lines[4:4+n],1):
        element=l[31:34].strip()
        if element!='H': atoms.append(dict(xyz=[float(l[k:k+10]) for k in (0,10,20)],element=element,index=i))
    chg=[l for l in lines if l.startswith('M  CHG')]
    return atoms,dict(total_atoms=n,bonds=nb,heavy_atoms=len(atoms),charge_records=chg)

def close_stats(rows,lig):
    d=np.linalg.norm(coords(rows)[:,None,:]-coords(lig)[None,:,:],axis=2)
    flat=np.argsort(d.ravel())[:5]; pairs=[]
    for k in flat:
        i,j=np.unravel_index(k,d.shape)
        pairs.append(dict(receptor=label(rows[i]),ligand_sdf_atom=lig[j]['index'],ligand_element=lig[j]['element'],distance_A=float(d[i,j])))
    return dict(min_distance_A=float(d.min()),pairs_below_1_5A=int((d<1.5).sum()),pairs_below_2A=int((d<2).sum()),residues_within_4A=sorted({rows[i]['resid'] for i in np.where(d.min(axis=1)<4)[0]}),nearest_pairs=pairs)

ap=argparse.ArgumentParser(); ap.add_argument('--handoff',type=Path,required=True); ap.add_argument('--fasta',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
seq=''.join(l.strip() for l in a.fasta.read_text().splitlines() if not l.startswith('>'))
report=dict(producer=dict(path=str(Path(__file__).resolve()),sha256=digest(Path(__file__))),method='Read-only static heavy-atom geometry audit; no minimization, chemistry validation, MD or membrane construction. Distances below 1.5/2 A are descriptive screens, not force-field acceptance thresholds. Confidence summaries use CA B-factor from AF3-export PDB.',python=sys.version,numpy=np.__version__,fasta=dict(path=str(a.fasta),sha256=digest(a.fasta),length=len(seq),residue84=seq[83],residue368=seq[367],lid164_178=seq[163:178]),sources=[],systems={},cross_mutant={})
transformed={}; ligands={}
for system in ('05_n84v','05_v368r'):
    root=a.handoff/system
    files=[root/'af3_original/raw_model0.pdb',root/'docking_receptor/input.pdb',root/'docking_receptor/alignment.json']
    orig=pdb(files[0]); dock=pdb(files[1]); trans=json.loads(files[2].read_text()); R=np.array(trans['rotation_matrix']); t=np.array(trans['translation_vector'])
    idx={x['key']:x for x in orig}; common=[x for x in dock if x['key'] in idx]
    x=coords([idx[z['key']] for z in common]); y=coords(common)
    errors={'row_x_R_plus_t':rms(x@R+t,y),'row_x_RT_plus_t':rms(x@R.T+t,y)}
    convention=min(errors,key=errors.get)
    assert convention=='row_x_R_plus_t' and errors[convention]<.002, errors
    moved=[dict(z,xyz=v.tolist()) for z,v in zip(orig,coords(orig)@R+t)]
    transformed[system]=moved
    ca=[z for z in orig if z['name']=='CA']; recseq=''.join(AA[z['resname']] for z in ca)
    assert len(recseq)==len(seq)
    delta=[dict(resid=i+1,wt=u,model=v) for i,(u,v) in enumerate(zip(seq,recseq)) if u!=v]
    s=dict(full_residues=len(ca),docking_residues=len({z['resid'] for z in dock}),sequence_differences_from_fasta=delta,transform_check=dict(common_heavy_atoms=len(common),rmsd_A=errors,convention=convention),confidence={},ligands={})
    for name,lo,hi in [('n_term',1,21),('lid',164,178),('site84',84,84),('site368',368,368)]:
        b=[z['b'] for z in ca if lo<=z['resid']<=hi]
        s['confidence'][name]=dict(min=min(b),max=max(b),mean=float(np.mean(b)))
    s['transform_check']['rotation_orthogonality_max_error']=float(np.max(np.abs(R.T@R-np.eye(3))))
    s['transform_check']['rotation_determinant']=float(np.linalg.det(R))
    assert {z['resid'] for z in ca}==set(range(1,407))
    assert {z['resid'] for z in dock}==set(range(22,164))|set(range(179,407))
    cif=next((root/'af3_original').glob('*.cif')); files.append(cif)
    cl=cif.read_text().splitlines(); cols=[z.strip() for z in cl if z.startswith('_atom_site.')]; ci={z.split('.',1)[1]:i for i,z in enumerate(cols)}
    catoms=[z.split() for z in cl if z.startswith('ATOM ')]
    cdict={(z[ci['auth_asym_id']],int(z[ci['auth_seq_id']]),z[ci['label_atom_id']]):z for z in catoms}
    errors_cif=[]; errors_b=[]
    for atom in orig:
        v=cdict[(atom['key'][0],atom['resid'],atom['name'])]
        errors_cif.append(float(np.linalg.norm(np.array(atom['xyz'])-np.array([float(v[ci[k]]) for k in ['Cartn_x','Cartn_y','Cartn_z']]))))
        errors_b.append(abs(atom['b']-float(v[ci['B_iso_or_equiv']])))
    s['cif_pdb_check']=dict(max_coordinate_delta_A=max(errors_cif),max_confidence_delta=max(errors_b))
    assert max(errors_cif)<.002 and max(errors_b)<.02
    sulfur=[z for z in moved if z['resname']=='CYS' and z['name']=='SG']; c173=[z for z in sulfur if z['resid']==173]
    if c173: s['cys173_SG_distances_A']={str(z['resid']):float(np.linalg.norm(coords([z])[0]-coords(c173)[0])) for z in sulfur if z['resid']!=173}
    for ligand in ('ascr18','ascr3'):
        sf=root/ligand/'top1.sdf'; pq=root/ligand/'top1.pdbqt'; sel=root/ligand/'selection.json'; poses=root/ligand/'poses.pdbqt'; files.extend([sf,pq,sel,poses])
        li,info=sdf(sf); lp=pdb(pq)
        dist=np.linalg.norm(coords(li)[:,None,:]-coords(lp)[None,:,:],axis=2)
        match=dist.argmin(axis=1)
        info['pdbqt_heavy_atoms']=len(lp); info['sdf_pdbqt_max_nearest_A']=float(dist.min(axis=1).max()); info['sdf_pdbqt_bijective']=len(set(match))==len(li)==len(lp)
        info['sdf_pdbqt_elements_match']=all(x['element']==lp[j]['element'] for x,j in zip(li,match))
        selection=json.loads(sel.read_text()); info['vina_score']=selection['vina_score_kcal_mol']; info['poses_sha256_matches_selection']=digest(poses)==selection['source_sha256']
        for region,subset in [('full',moved),('restored_lid',[z for z in moved if 164<=z['resid']<=178]),('restored_lid_backbone',[z for z in moved if 164<=z['resid']<=178 and z['name'] in ('N','CA','C','O')]),('restored_n_term',[z for z in moved if z['resid']<=21]),('retained_receptor',[z for z in moved if z['resid']>21 and not 164<=z['resid']<=178]),('site84',[z for z in moved if z['resid']==84]),('site368',[z for z in moved if z['resid']==368])]: info[region]=close_stats(subset,li)
        if system=='05_v368r':
            gn=[z for z in moved if z['resid']==368 and z['name'] in ('NE','NH1','NH2')]
            oxy=[z for z in li if z['element']=='O']
            info['arg368_guanidinium_N_to_any_ligand_O_min_A']=float(np.linalg.norm(coords(gn)[:,None,:]-coords(oxy)[None,:,:],axis=2).min())
        if info['sdf_pdbqt_bijective'] and info['sdf_pdbqt_elements_match']:
            q=coords(lp)@R.T-t@R.T
            qq=q[match]
            lid_original=[z for z in orig if 164<=z['resid']<=178]
            inv_min=float(np.linalg.norm(coords(lid_original)[:,None,:]-qq[None,:,:],axis=2).min())
            info['inverse_frame_lid_min_distance_A']=inv_min
            assert abs(inv_min-info['restored_lid']['min_distance_A'])<1e-8
        s['ligands'][ligand]=info; ligands[(system,ligand)]=li
    report['sources'].extend(dict(path=str(p),sha256=digest(p)) for p in files)
    report['systems'][system]=s

maps=[{z['key']:z for z in transformed[s]} for s in ('05_n84v','05_v368r')]
ranges=[(30,50),(62,83),(101,126),(144,163),(182,201),(326,346),(358,380)]
for name,test in [('TM_alignment_CA',lambda z:z['name']=='CA' and any(l<=z['resid']<=h for l,h in ranges)),('lid_backbone',lambda z:164<=z['resid']<=178 and z['name'] in ('N','CA','C','O')),('all_backbone',lambda z:z['name'] in ('N','CA','C','O'))]:
    keys=[k for k,z in maps[0].items() if k in maps[1] and test(z)]
    x,y=[coords([m[k] for k in keys]) for m in maps]
    xc=x-x.mean(0); yc=y-y.mean(0); u,_,vt=np.linalg.svd(xc.T@yc); rr=u@np.diag([1,1,np.linalg.det(u@vt)])@vt
    report['cross_mutant'][name]=dict(atoms=len(keys),in_docking_frame_RMSD_A=rms(x,y),independent_optimal_fit_RMSD_A=rms(xc@rr,yc))
for l in ('ascr18','ascr3'):
    x,y=[coords(ligands[(s,l)]) for s in ('05_n84v','05_v368r')]
    report['cross_mutant'][l]=dict(centroid_distance_A=float(np.linalg.norm(x.mean(0)-y.mean(0))),atom_order_RMSD_A=rms(x,y),atom_order_element_agreement=[z['element'] for z in ligands[('05_n84v',l)]]==[z['element'] for z in ligands[('05_v368r',l)]])
a.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('fasta','cross_mutant')},indent=2))
for name,s in report['systems'].items():
    print(name, 'sequence',s['sequence_differences_from_fasta'],'transform RMSD',s['transform_check']['rmsd_A'],'confidence',s['confidence'])
    for l,v in s['ligands'].items():
        print(l,{k:{q:v[k][q] for q in ('min_distance_A','pairs_below_1_5A','pairs_below_2A')} for k in ('restored_lid','restored_n_term','retained_receptor','site84','site368')})
        print('closest lid:',v['restored_lid']['nearest_pairs'][0], 'coordinate match',v['sdf_pdbqt_max_nearest_A'],'pose checksum',v['poses_sha256_matches_selection'])
