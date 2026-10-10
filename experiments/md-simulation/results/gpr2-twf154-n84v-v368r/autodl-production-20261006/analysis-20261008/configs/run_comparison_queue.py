"""Run recorded comparison commands after all real driver completions exist."""
import json,os,sys,time,subprocess
from pathlib import Path
recipe=json.loads(Path(sys.argv[1]).read_text());b=json.loads(Path(recipe['batch_config']).read_text());out=Path(recipe['output_dir']);out.mkdir(parents=True,exist_ok=True)
deadline=time.monotonic()+7200
while True:
 ready=[]
 for case in b['cases']:
  path=Path(b['output_root'])/case['id']/'evidence/driver_completion.json'
  ready.append(path.exists() and json.loads(path.read_text())['status']=='PASS')
 if all(ready):break
 if time.monotonic()>deadline:raise SystemExit('comparison HOLD: missing case completion')
 time.sleep(20)
os.chdir(recipe['cwd'])
for command in recipe['commands']:
 print('START',command['name'],flush=True)
 (out/(command['name']+'.command.json')).write_text(json.dumps(command,indent=2)+'\n')
 with (out/(command['name']+'.log')).open('w') as log:
  result=subprocess.run(command['argv'],stdout=log,stderr=subprocess.STDOUT)
 (out/(command['name']+'.exit')).write_text(str(result.returncode)+'\n')
 print('EXIT',command['name'],result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
print('COMPARISON_COMMANDS_COMPLETE',flush=True)
