#!/usr/bin/env python3
"""Fixed remaining four-case registry; share unchanged qualified runtime/resource checks."""
from types import SimpleNamespace
from dual_runtime import GMX,GMX_SHA,CORES,now,need,sha,read,save,module,env,load_core,SixCore,children,live,affinity
import remaining_closed_v1 as closed
BATCHES={'raw':('raw_n84v_ascr3','raw_v368r_ascr18'),'lid':('v368r_ascr3_lid_rebuilt_own_pose_v1','native_wt_ascr3_lid_rebuilt_own_pose_v1')}
COUNTS={'raw_n84v_ascr3':146021,'raw_v368r_ascr18':145979,'v368r_ascr3_lid_rebuilt_own_pose_v1':145905,'native_wt_ascr3_lid_rebuilt_own_pose_v1':145681}
CASES={c:{'work':'runs/'+c+'/rep1_codex_v1','records':'operator_records/production_'+c+'_v1','qualifier':'operator_records/qualification_'+c+'_v1','atoms':n} for c,n in COUNTS.items()}
def case_validator(case):
 need(case in CASES,'Case outside authorized remaining registry')
 c=SimpleNamespace(PREFIX=case+'_rep1_production',CHECKS=closed.CHECKS,event=closed.event)
 c.validate_closed=lambda *args:closed.validate_closed(*args,case=case,natoms=CASES[case]['atoms'],prefix=c.PREFIX)
 return c
