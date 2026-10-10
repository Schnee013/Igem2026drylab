import json,subprocess,os,pathlib
b=pathlib.Path('/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis/_mechanism_20261010')
py='/ifs1/User/dengwei/igem/envs/roy_md-analysis-py311/bin/python'
cfg=b/'pair_detail_config.json'
s=b/'source_v2/experiments/md-simulation/analysis/chctrl/analyze_local_mechanism.py'
env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',CHIMERIC_MD_REPS='1')
status=[]
for c in json.loads(cfg.read_text())['cases']:
 with (b/(c['id']+'.pair.log')).open('w') as f:code=subprocess.call(['nice','-n','10',py,str(s),'--config',str(cfg),'--pair-detail','--case',c['id']],env=env,stdout=f,stderr=subprocess.STDOUT)
 status.append(dict(case=c['id'],exit_code=code))
 (b/'pair_queue_status.json').write_text(json.dumps(status,indent=2)+'\n')
