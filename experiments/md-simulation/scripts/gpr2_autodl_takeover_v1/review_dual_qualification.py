#!/usr/bin/env python3
"""Supplement the executed qualifier with source-labelled energy review; preserve originals."""
import argparse, json, math, re
from pathlib import Path
import dual_runtime as d

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args()
    b=a.bundle.resolve();root=b/'operator_records/dual_qualification_v1';q=root/'qualification.json';data=d.read(q)
    d.need(data['status']=='PASS_OWN_TWO_CASE_SIX_THREAD_FORCE_AND_RESTART','Qualification did not pass')
    for rel,h in data['evidence_sha256'].items():d.need(d.sha(root/rel)==h,'Evidence changed: '+rel)
    refs={str(q):d.sha(q)};comparisons=[]
    for case in d.CASES:
        for frame in ('start_state','after_restart'):
            values=[]
            for mode in ('baseline','candidate'):
                p=root/case/(frame+'_'+mode+'.energy.xvg');text=p.read_text();refs[str(p)]=d.sha(p)
                legends={int(i):name for i,name in re.findall(r'@\s+s(\d+)\s+legend\s+"([^"]+)"',text)}
                rows=[list(map(float,l.split())) for l in text.splitlines() if l.strip() and not l.lstrip().startswith(('#','@'))]
                d.need(len(rows)==1 and set(legends)==set(range(len(rows[0])-1)),'Ambiguous energy columns')
                v={legends[i]:rows[0][i+1] for i in legends};d.need(set(v)=={'Potential','Temperature','Pressure'} and all(math.isfinite(x) for x in v.values()),'Invalid energy data')
                values.append(v)
            delta={k:values[1][k]-values[0][k] for k in values[0]}
            original=root/case/(frame+'.comparison.json');c=d.read(original);refs[str(original)]=d.sha(original)
            d.need(delta['Potential']==c['candidate_minus_baseline'][0] and abs(delta['Potential'])<=c['potential_empirical_max'],'Potential acceptance differs')
            d.need(all(v['relative_rms']<=c['force_empirical_max'] for v in c['force'].values()),'Force comparison failed')
            comparisons.append({'case':case,'frame':frame,'baseline':values[0],'candidate':values[1],'candidate_minus_baseline':delta,'force':c['force']})
        own=b/d.CASES[case]['records']/'initial_review.json';review=d.read(own);refs[str(own)]=d.sha(own)
        d.need(review['production_tpr_sha256']==data['cases'][case]['production_tpr_sha256']==d.sha(b/d.CASES[case]['work']/'production.tpr'),'Own formal input changed')
        for e in review.get('evidence',[]):d.need(d.sha(e['path'])==e['sha256'],'Own review evidence changed');refs[e['path']]=e['sha256']
        start=data['cases'][case]['formal_source_start_ps']
        for phase,offset in (('first',20),('restart',40)):
            p=root/case/('validation_'+phase)/'closed_segment.json';s=d.read(p);refs[str(p)]=d.sha(p)
            d.need(s['pass'] and s['end_ps']==start+offset,'Own simultaneous/restart closure failed')
    out=root/'dual_production_review.json';d.need(not out.exists(),'Review already exists')
    d.save(out,{'status':'ACCEPT_OWN_TWO_CASE_DUAL_PRODUCTION','reviewed_at':d.now(),'qualification_sha256':d.sha(q),'evidence_sha256':refs,'energy_column_correction':'Original comparison energy_names swapped Temperature and Pressure. This review reads actual XVG legends; raw data and original comparisons remain unchanged. Potential was correctly indexed; original potential and force acceptance is unchanged.','comparisons':comparisons,'accepted_scope':'Own unchanged WT formal19728ps checkpoint and N84V formal0 TPR; six threads each, nstlist200, original physics. Independent preparation, runtime, structure and native restart evidence remains required.','limits':data['limits'],'production_credit_ns':0})
    print(json.dumps({'review':str(out),'status':d.read(out)['status'],'max_abs_potential_delta':max(abs(x['candidate_minus_baseline']['Potential']) for x in comparisons)}))
if __name__=='__main__':main()
