#!/usr/bin/env python3
"""Validate and compare existing shared-driver tables under a batch contract.

Reads metric tables, not trajectories. Block ranges are descriptive variation
within each trajectory and never independent-replicate confidence intervals.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TABLES = {
    'receptor_backbone_rmsd_A': ('convergence/rmsd_summary.csv','backbone_rmsd_A',10001),
    'receptor_CA_Rg_A': ('convergence/rg_summary.csv','rg_A',10001),
    'ligand_heavy_rmsd_A': ('selection_rmsd/selection_rmsd.csv','selection_rmsd_A',10001),
    'receptor_ligand_BSA_A2': ('bsa/bsa.csv','bsa_A2',201),
    'BSA_fraction_of_own_initial': ('bsa/bsa.csv','bsa_fraction_of_initial',201),
    'own_initial_contact_retained_fraction': ('contacts/contact_persistence.csv','retained_fraction',201),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--batch-config',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    batch=json.loads(args.batch_config.read_text())
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    validation,summary,stats,blocks,identities,initial_contacts=[],[],[],[],[],[]
    all_series={};rmsf_tables=[];valid_cases=[]
    for case in batch['cases']:
        cid=case['id'];base=Path(batch['output_root'])/cid;root=base/'analysis'
        checks=[]
        def check(name,condition,detail):
            checks.append({'case_id':cid,'check':name,'status':'PASS' if condition else 'FAIL','detail':detail})
            if not condition:
                raise ValueError(f'{cid}: {name}: {detail}')
        try:
            inputs=json.loads((base/'evidence/input_validation.json').read_text())
            processed=json.loads((base/'evidence/processed_validation.json').read_text())
            completion=json.loads((base/'evidence/driver_completion.json').read_text())
            check('processed_gate',processed['status']=='PASS',str(processed))
            check('seven_real_driver_exits',completion['status']=='PASS' and len(completion['drivers'])==7 and all((base/f'evidence/{name}.log.exit').read_text().strip()=='0' for name in completion['drivers']),str(completion))
            row={'case_id':cid,'label':case['label'],'genotype':case['genotype'],'ligand':case['ligand'],
                 'lid':inputs['input_contract']['lid'],'source_original_case':inputs['input_contract']['source_original_case'],
                 'replicates':1,'window_start_ns':50,'window_end_ns':100,'segments':case['segments'],
                 'full_atoms':case['full_atoms'],'processed_atoms':processed['processed_atoms'],
                 'protein_atoms':inputs['protein_atoms'],'protein_residues':inputs['protein_residues'],
                 'ligand_atoms':inputs['ligand_atoms'],'ligand_heavy_atoms':inputs['ligand_heavy_atoms'],
                 'unique_frames':processed['frames'],'stored_raw_frames':inputs['stored_frames'],
                 'max_heavy_bond_A':processed['heavy_bond_max_A'],'max_relative_ligand_COM_step_A':processed['max_ligand_relative_com_10ps_step_A']}
            series={}
            for metric,(path,column,count) in TABLES.items():
                df=pd.read_csv(root/path)
                check(metric+'_time_grid',len(df)==count and np.allclose(df.time_ns,np.linspace(0,100,count)),f'rows={len(df)}; expected={count}')
                check(metric+'_finite',np.isfinite(df[column]).all(),column)
                if 'rmsd' in metric:
                    check(metric+'_initial_zero',abs(float(df[column].iloc[0]))<1e-4,'frame0 RMSD relative to own frame0')
                series[metric]=df[['time_ns',column]].rename(columns={column:'value'})
            bsa=pd.read_csv(root/'bsa/bsa.csv')
            check('BSA_fraction_reproduction',float(bsa.bsa_A2.iloc[0])>0 and np.allclose(bsa.bsa_fraction_of_initial,bsa.bsa_A2/float(bsa.bsa_A2.iloc[0]),atol=1e-6),'absolute SASA-derived BSA versus stored normalization')
            cp=pd.read_csv(root/'contacts/contact_persistence.csv')
            check('contact_fraction_reproduction',np.allclose(cp.retained_fraction,cp.retained_contacts/cp.initial_contacts) and cp.retained_fraction.iloc[0]==1,'initial-contact counts versus fractions')
            com=pd.read_csv(root/'com_distance/com.csv')
            for cluster,df in com.groupby('cluster'):
                check('COM_'+cluster+'_grid',len(df)==10001 and np.allclose(df.time_ns,np.linspace(0,100,10001)),f'rows={len(df)}')
                check('COM_'+cluster+'_finite',np.isfinite(df.distance_A).all(),'distance_A')
                series['ligand_COM_to_'+cluster+'_A']=df[['time_ns','distance_A']].rename(columns={'distance_A':'value'})
            check('COM_cluster_count',len(com.cluster.unique())==2,str(com.cluster.unique()))
            for metric,df in series.items():
                all_series.setdefault(metric,{})[cid]=df
                for name,start,end,end_inclusive in [('full',0,100,True),('early',0,50,False),('primary',50,100,True)]:
                    selected=df[(df.time_ns>=start)&(df.time_ns<=end if end_inclusive else df.time_ns<end)]
                    values=selected.value.to_numpy()
                    result={'case_id':cid,'metric':metric,'window':name,'start_ns':start,'end_ns':end,
                            'end_inclusive':end_inclusive,'n_samples':len(values),'mean':float(values.mean()),
                            'median':float(np.median(values)),'min':float(values.min()),'max':float(values.max()),
                            'temporal_sd':float(values.std()),'slope_per_ns':float(np.polyfit(selected.time_ns,values,1)[0])}
                    stats.append(result)
                    if name=='primary':
                        row[metric+'_mean']=result['mean'];row[metric+'_max']=result['max'];row[metric+'_slope_per_ns']=result['slope_per_ns']
                for start in range(0,100,10):
                    selected=df[(df.time_ns>=start)&(df.time_ns<=start+10 if start==90 else df.time_ns<start+10)]
                    blocks.append({'case_id':cid,'metric':metric,'start_ns':start,'end_ns':start+10,
                                   'n_samples':len(selected),'mean':float(selected.value.mean()),
                                   'min':float(selected.value.min()),'max':float(selected.value.max())})
            rmsf=pd.read_csv(root/'rmsf/rmsf.csv')
            check('rmsf_residue_mapping',len(rmsf)==inputs['protein_residues'] and rmsf.resid.is_unique and rmsf.resid.tolist()==list(range(1,inputs['protein_residues']+1)),f'residues={len(rmsf)}')
            check('rmsf_finite',np.isfinite(rmsf.rmsf_A).all(),'rmsf_A')
            rmsf['case_id']=cid;rmsf_tables.append(rmsf)
            row['receptor_CA_RMSF_A_mean']=float(rmsf.rmsf_A.mean());row['receptor_CA_RMSF_A_max']=float(rmsf.rmsf_A.max())
            hb=pd.read_csv(root/'hbond/hbond_summary.csv')
            sampling=json.loads((root/'hbond/sampling_window.json').read_text())
            check('hbond_window',sampling['window_ns']==[50,100] and sampling['stride']==50,str(sampling))
            check('hbond_occupancy',hb.empty or (np.isfinite(hb.occupancy).all() and hb.occupancy.between(0,1).all() and hb.n_frames.eq(101).all()),f'pairs={len(hb)}')
            check('hbond_denominator_reproduction',hb.empty or np.allclose(hb.occupancy,hb.events/hb.n_frames),'events / sampled window frames')
            events=pd.read_csv(root/'hbond/hbond_events.csv')
            check('hbond_event_times',events.empty or events.time_ns.between(50,100).all(),f'events={len(events)}')
            row['top_geometric_hbond_occupancy']=float(hb.occupancy.max()) if len(hb) else 0.0
            row['top_geometric_hbond_pair']=str(hb.iloc[0]['pair']) if len(hb) else 'none_detected'
            row['geometric_hbond_pairs_observed']=len(hb)
            contacts=pd.read_csv(root/'contacts/initial_contact_occupancy.csv')
            check('initial_contact_occupancy',np.isfinite(contacts.occupancy).all() and contacts.occupancy.between(0,1).all() and contacts.n_frames.eq(101).all(),f'initial residue pairs={len(contacts)}')
            row['initial_4A_residue_contacts']=len(contacts)
            for r in contacts.to_dict('records'):
                initial_contacts.append({'case_id':cid,**r})
            for path in sorted(root.rglob('*.csv')):
                identities.append({'case_id':cid,'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)})
            summary.append(row);valid_cases.append(cid)
        except Exception as exc:
            checks.append({'case_id':cid,'check':'case_acceptance','status':'FAIL','detail':str(exc)})
        validation.extend(checks)
    pd.DataFrame(validation).to_csv(out/'analysis_validation.tsv',sep='\t',index=False)
    frame=pd.DataFrame(summary);frame.to_csv(out/'six_case_summary.csv',index=False)
    pd.DataFrame(stats).to_csv(out/'time_series_statistics.csv',index=False)
    pd.DataFrame(blocks).to_csv(out/'ten_ns_blocks.csv',index=False)
    pd.DataFrame(identities).to_csv(out/'metric_input_identity.tsv',sep='\t',index=False)
    pd.DataFrame(initial_contacts).to_csv(out/'initial_contact_occupancies.csv',index=False)
    labels={c['id']:c['label'] for c in batch['cases']}
    order=[c['id'] for c in batch['cases'] if c['id'] in valid_cases]
    colors={cid:plt.cm.tab10(i) for i,cid in enumerate(order)}
    overview=['receptor_backbone_rmsd_A','ligand_heavy_rmsd_A','receptor_CA_Rg_A',
              'BSA_fraction_of_own_initial','own_initial_contact_retained_fraction','ligand_COM_to_whole_receptor_A']
    fig,axes=plt.subplots(3,2,figsize=(13,10),sharex=True)
    for ax,metric in zip(axes.flat,overview):
        for cid in order:
            df=all_series[metric][cid]
            ax.plot(df.time_ns,df.value,color=colors[cid],linewidth=.65,alpha=.8,label=labels[cid])
        ax.axvspan(50,100,alpha=.06,color='grey');ax.set_title(metric.replace('_',' '),fontsize=10)
        ax.grid(alpha=.2);ax.set_xlabel('Time (ns)')
    axes[0,0].legend(fontsize=7,loc='upper left')
    fig.suptitle('Six independent starting systems: rep1 each; primary window 50-100 ns',fontsize=12)
    fig.tight_layout();fig.savefig(out/'six_case_timeseries.png',dpi=180);fig.savefig(out/'six_case_timeseries.pdf');plt.close(fig)
    if rmsf_tables:
        rf=pd.concat(rmsf_tables);rf.to_csv(out/'receptor_RMSF_50_100ns.csv',index=False)
        fig,ax=plt.subplots(figsize=(12,4))
        for cid in order:
            df=rf[rf.case_id==cid];ax.plot(df.resid,df.rmsf_A,label=labels[cid],color=colors[cid],linewidth=.9)
        ax.axvspan(164,178,color='grey',alpha=.15,label='ECL2 lid 164-178')
        for resid in [84,368]:ax.axvline(resid,color='grey',linestyle=':',linewidth=.8)
        ax.set_xlabel('Receptor residue (source numbering)');ax.set_ylabel('CA RMSF (A), 50-100 ns');ax.legend(fontsize=7,ncol=2);ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(out/'six_case_receptor_rmsf.png',dpi=180);plt.close(fig)
    block_df=pd.DataFrame(blocks)
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
    for ax,metric in zip(axes.flat,[overview[0],overview[1],overview[3],overview[4]]):
        for cid in order:
            df=block_df[(block_df.case_id==cid)&(block_df.metric==metric)]
            ax.plot(df.start_ns+5,df['mean'],marker='o',ms=3,color=colors[cid],label=labels[cid])
        ax.set_title(metric.replace('_',' '),fontsize=9);ax.grid(alpha=.2);ax.set_xlabel('10 ns block midpoint (ns)')
    axes[0,0].legend(fontsize=7);fig.suptitle('Descriptive temporal blocks; no independent-replicate uncertainty')
    fig.tight_layout();fig.savefig(out/'six_case_ten_ns_blocks.png',dpi=180);plt.close(fig)
    status={'status':'PASS' if len(valid_cases)==len(batch['cases']) else 'PARTIAL',
            'accepted_cases':valid_cases,'expected_cases':[c['id'] for c in batch['cases']],
            'validation_passes':sum(r['status']=='PASS' for r in validation),
            'validation_failures':sum(r['status']=='FAIL' for r in validation),
            'primary_window_ns':[50,100],'dense_spacing_ns':.01,'sparse_spacing_ns':.5,
            'evidence_level':'single_rep_exploratory_only',
            'interpretation_boundary':'actual parents/lids/poses; no mutation causality, affinity rank, or mechanism establishment'}
    (out/'comparison_status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status,indent=2))
    if status['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':
    main()
