import json,subprocess,os,pathlib,time
base=pathlib.Path('/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis/_mechanism_20261010')
config=base/'mechanism_config.json'
cfg=json.loads(config.read_text())
py='/ifs1/User/dengwei/igem/envs/roy_md-analysis-py311/bin/python'
script=base/'source/experiments/md-simulation/analysis/chctrl/analyze_local_mechanism.py'
env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',CHIMERIC_MD_REPS='1')
status=[]
with (base/'prepare.log').open('w') as log:
 code=subprocess.call([py,str(script),'--config',str(config),'--prepare'],stdout=log,stderr=subprocess.STDOUT,env=env)
assert code==0, 'prepare failed; see prepare.log'
for case in cfg['cases']:
 with (base/(case['id']+'.log')).open('w') as log:
  code=subprocess.call(['nice','-n','10',py,str(script),'--config',str(config),'--case',case['id']],stdout=log,stderr=subprocess.STDOUT,env=env)
 status.append(dict(case=case['id'],exit_code=code,finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
 (base/'queue_status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status),flush=True)
