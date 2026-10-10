#!/usr/bin/env python3
"""Compile an own accepted2750ps preparation into the original zero-clock100ns TPR."""
import argparse, json, os, re, shutil, sys
from pathlib import Path
import dual_runtime as d
import prepare_existing_npt as core
import qualify_n84v_production as q

CASES=('raw_n84v_ascr3','raw_v368r_ascr18','v368r_ascr3_lid_rebuilt_own_pose_v1','native_wt_ascr3_lid_rebuilt_own_pose_v1')

def compile_one(b,case):
    w=b/'runs'/case/'rep1_codex_v1';done=d.read(w/'preparation_complete.json')
    d.need(done['case_id']==case and done['preparation_pass'] and done['final_time_ps']==2750,'Own full preparation not accepted')
    fresh='lid_rebuilt' in case
    final=w/('npt05.new_lid_validated.json' if fresh else 'npt05.validated.json');v=d.read(final)
    d.need(v['case_id']==case and v['end_ps']==2750 and v['pass' if fresh else 'pass_stage'],'Own final stage failed')
    thermo=v['thermo'] if fresh else v;d.need(thermo['box_density_settled'],'Own final drift screen failed')
    source={}
    if fresh:
        record=b/'operator_records'/('new_lid_prep_'+case+'_v1');plan=d.read(record/'source_review.json');source.update(plan['source_sha256'])
        for stage in ('em','heat','hold','npt01','npt02','npt03','npt04','npt05'):
            p=w/(stage+'.new_lid_validated.json');s=d.read(p);d.need(s['pass'] and s['case_id']==case,'Own fresh stage failed')
            for name,h in s['files_sha256'].items():d.need(d.sha(name)==h,'Accepted fresh-stage evidence changed')
            source[str(p.relative_to(b))]=d.sha(p)
        structure=record/'npt05/structure.json';npt_dump=record/'npt05/tpr_dump.log'
    else:
        plan=core.verify_sources(b,case);source.update(plan['source_sha256'])
        for stage,_,_ in core.STAGES:
            p=w/(stage+'.validated.json');s=d.read(p);d.need(s['pass_stage'] and s['case_id']==case,'Own NPT stage failed');core.validate_manifest(w,s['output_sha256'],core.stage_output_names(stage));source[str(p.relative_to(b))]=d.sha(p)
        structure=w/'npt05.structure.json';npt_dump=w/'npt05.tpr.dump.txt'
    for name,h in source.items():d.need(d.sha(b/name)==h,'Own immutable preparation source changed')
    d.need(d.read(structure)['pass'],'Own final structure failed')
    d.need(not (w/'production.tpr').exists() and not (w/'source_preflight.json').exists(),'Existing production compilation requires identity review, not overwrite')
    out=b/'operator_records'/('production_compile_'+case+'_v1');out.mkdir(exist_ok=False)
    d.need(d.sha(d.GMX)==d.GMX_SHA,'Pinned A binary changed')
    mdp=b/'compute/mdp/production.mdp';d.need(d.sha(mdp)==q.MDP_SHA,'Original production physical/output MDP changed');shutil.copyfile(mdp,w/'production.mdp')
    def run(args,name,stdin=None):return core.command(args,out/(name+'.log'),w,stdin)
    text=run([d.GMX,'grompp','-f','production.mdp','-c','npt05.gro','-t','npt05.cpt','-p','topol.top','-n','index.ndx','-o','production.tpr','-po','production_mdout.mdp','-pp','production_processed.top'],'grompp')
    d.need(not re.search(r'WARNING\s+\d+|Fatal error',text),'Neutral production compilation warning')
    expected=core.mdp(mdp.read_text());actual=core.mdp((w/'production_mdout.mdp').read_text());d.need(all(core.same_mdp_value(actual.get(k,''),val) for k,val in expected.items()),'Production MDP readback differs')
    d.need(not re.search(r'^\s*\[\s*(position_restraints|dihedral_restraints)\s*\]',(w/'production_processed.top').read_text(),re.M),'Production restraints present')
    tpr=run([d.GMX,'dump','-s',w/'production.tpr'],'production_tpr_dump');cp=run([d.GMX,'dump','-cp',w/'npt05.cpt'],'npt05_checkpoint_dump');nt=int((w/'npt05.gro').read_text().splitlines()[1])
    for key,val in {'natoms':nt,'tinit':0,'init-step':0,'dt':.002,'nsteps':50000000,'nstxout':0,'nstvout':0,'nstfout':0,'nstxout-compressed':5000,'nstenergy':500,'nstlog':5000}.items():d.need(core.scalar(tpr,key)==val,'Production clock/output mismatch: '+key)
    d.need(core.scalar(cp,'#atoms')==nt and core.scalar(cp,'t')==2750,'Wrong own preparation CPT');core.state_match(tpr,w/'npt05.gro');core.state_match(cp,w/'npt05.gro')
    d.need(q.scientific_prefix(tpr)==q.scientific_prefix(npt_dump.read_text()),'Force/coupling/topology differs from own accepted unrestrained NPT')
    errors={}
    for name,count in [('x',nt),('v',nt),('box',3)]:
        left=core.dump_vectors(tpr,name,count);right=core.dump_vectors(cp,name,count)
        d.need(all(abs(a-b)<=1e-7+1e-5*max(abs(a),abs(b)) for x,y in zip(left,right) for a,b in zip(x,y)),'Own full state differs: '+name);errors[name]=max(abs(a-b) for x,y in zip(left,right) for a,b in zip(x,y))
    for p in [w/'preparation_complete.json',final,structure,w/'npt05.cpt',w/'npt05.gro',w/'npt05.tpr',w/'input_contract.json',w/'topol.top']:
        source[str(p.relative_to(b))]=d.sha(p)
    report={'case_id':case,'source_purpose':'Own authorized mother/pose and actual accepted preparation; exploratory rep1, no E2 production credit','source_preparation_ps':2750,'production_clock_ps':[0,100000],'atom_count':nt,'preparation_evidence':thermo,'structure':d.read(structure),'production_tpr_sha256':d.sha(w/'production.tpr'),'source_sha256':source,'source_x_v_box_max_dump_error':errors,'production_ready':False,'remaining':'Own numerical, zero-start/CPT-restart and six-thread dual qualification; compilation alone never releases production'}
    d.save(w/'source_preflight.json',report)
    files=list(out.iterdir())+[w/n for n in ('production.mdp','production.tpr','production_mdout.mdp','production_processed.top','source_preflight.json','input_contract.json','preparation_complete.json')]+[final,structure]+([record/'source_review.json'] if fresh else [])
    archive=out/'segment_001';archive.mkdir();d.save(archive/'closed_segment.json',{'case_id':case,'stage':'own_zero_clock_compilation','stage_kind':'input_preparation','production_credit_ns':0,'start_ps':0,'end_ps':0,'pass':True,'files':[{'path':str(p),'sha256':d.sha(p)} for p in files if p.is_file()]})
    print(json.dumps({'case_id':case,'own_zero_clock_tpr_compiled':True,'production_ready':False}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--case',choices=CASES,required=True);a=ap.parse_args();os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1');compile_one(a.bundle.resolve(),a.case)
if __name__=='__main__':main()
