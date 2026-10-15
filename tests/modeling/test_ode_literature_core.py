"""Validate the source reconstruction, output merge and portable CLI."""
import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from scipy.integrate import solve_ivp

from src.modeling.ode.literature_core import LiteratureCoreModel, PROJECT_PATH, ROOT, SOURCE_PATH


def full_rhs(t, y, model, ligand):
    """Independent full-state mass balances from Delft Table 4.1 reactions."""
    H,A,D,B,S,Q,F,Fp,Z,Zp,C = y
    p,o = model.rates,model.output
    act = model.drive(ligand)*H
    hyd = (p['k4']+p['k41']*Zp)*A
    re = p['k5']*D*B
    ass = p['k6']*S*B
    dis = (p['k7']+p['k71']*Zp)*Q
    fon = p['k8']*Q*F
    foff = (p['k9']+p['k91']*Z)*Fp
    zon = p['k10']*Fp*Z
    zoff = p['k11']*Zp
    m = max(Fp/model.pools[3],0.)
    dc = (o['b']+o['a']*m**o['n']/(o['K']**o['n']+m**o['n'])-o['delta']*C)/3600
    return np.array([-act+re,act-hyd,hyd-re,act-re-ass+dis,-ass+dis,
                     ass-dis,-fon+foff,fon-foff,-zon+zoff,zon-zoff,dc])


class LiteratureCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = LiteratureCoreModel()
        cls.times = np.unique(np.r_[0,np.geomspace(.001,900,80),np.linspace(900,28800,80)])

    def test_reduction_matches_all_full_states(self):
        for ligand in (0,1e-6,.1,1,10):
            with self.subTest(ligand=ligand):
                reduced=self.model.solve(ligand,self.times)
                full=solve_ivp(lambda t,y:full_rhs(t,y,self.model,ligand),
                               (0,self.times[-1]),self.model.reconstruct(self.model.initial),
                               t_eval=self.times,method='BDF',rtol=1e-9,atol=1e-12)
                self.assertTrue(full.success)
                np.testing.assert_allclose(self.model.reconstruct(reduced.y),full.y,atol=1e-7,rtol=0)

    def test_physical_domain_and_conservation(self):
        y=self.model.reconstruct(self.model.solve(1,self.times).y)
        self.assertGreaterEqual(float(y.min()),-1e-9)
        pools=np.array([y[0]+y[1]+y[2],y[0]+y[3]+y[5],y[4]+y[5],y[6]+y[7],y[8]+y[9]])
        np.testing.assert_allclose(pools,np.repeat(self.model.pools[:,None],len(self.times),axis=1),atol=1e-12,rtol=0)

    def test_zero_input_color_matches_hour_unit_analytical_solution(self):
        o=self.model.output
        sol=self.model.solve(0,self.times)
        expected=o['b']/o['delta']*(-np.expm1(-o['delta']*self.times/3600))
        np.testing.assert_allclose(sol.y[5],expected,atol=1e-8,rtol=0)

    def test_output_is_exact_merge_of_original_scenario(self):
        old=json.loads((ROOT/'experiments/ode-model/configs/minimal_normalized_scenario.json').read_text())
        t,g,c=old['transcription'],old['gal_output'],old['color']
        m=np.linspace(0,1,1001)
        tf=t['basal_activity']+t['efficacy']*m**t['hill_coefficient']/(t['half_activation']**t['hill_coefficient']+m**t['hill_coefficient'])
        direct=c['production_rate_per_hour']*(g['leak_rate']+g['copy_number']*g['gain_rate']*tf/(g['half_activation']+tf))
        o=self.model.output
        merged=o['b']+o['a']*m**o['n']/(o['K']**o['n']+m**o['n'])
        np.testing.assert_allclose(merged,direct,atol=1e-14,rtol=0)
        self.assertEqual(o['delta'],c['loss_rate_per_hour'])

    def test_changed_endpoints_and_zero_loss(self):
        config=json.loads(PROJECT_PATH.read_text())
        replacements={'input':{'u_max_per_second':.002,'K_L_normalized':.3},
                      'output':{'b':.01,'a':.15,'K':.4,'n':1.5,'delta':0.}}
        for group,values in replacements.items():
            for key,value in values.items():
                config[group][key]['value']=value
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'endpoints.json';path.write_text(json.dumps(config))
            model=LiteratureCoreModel(path)
            reduced=model.solve(.2,self.times)
            full=solve_ivp(lambda t,y:full_rhs(t,y,model,.2),(0,self.times[-1]),
                           model.reconstruct(model.initial),t_eval=self.times,
                           method='BDF',rtol=1e-9,atol=1e-12)
            self.assertTrue(full.success)
            np.testing.assert_allclose(model.reconstruct(reduced.y),full.y,atol=1e-7,rtol=0)
            np.testing.assert_allclose(model.solve(0,self.times).y[5],.01*self.times/3600,atol=1e-8,rtol=0)

    def test_invalid_inputs_and_times_rejected(self):
        for ligand in (-1,np.nan,np.inf):
            with self.assertRaises(ValueError): self.model.solve(ligand,[0,1])
        for times in ([],[0],[1,2],[0,0],[0,np.nan],[[0,1],[2,3]]):
            with self.assertRaises(ValueError): self.model.solve(1,times)

    def test_invalid_parameters_and_source_rejected(self):
        base=json.loads(PROJECT_PATH.read_text())
        source=json.loads(SOURCE_PATH.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json'
            for value in (0,-1,float('nan')):
                config=copy.deepcopy(base);config['input']['K_L_normalized']['value']=value
                path.write_text(json.dumps(config))
                with self.assertRaises(ValueError): LiteratureCoreModel(path)
            config=copy.deepcopy(base);config['output']['b']['source']=''
            path.write_text(json.dumps(config))
            with self.assertRaises(ValueError): LiteratureCoreModel(path)
            source['time_unit']='h';path.write_text(json.dumps(source))
            with self.assertRaises(ValueError): LiteratureCoreModel(source_path=path)

    def test_cli_works_outside_repo_and_binds_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'run'
            result=subprocess.run([sys.executable,str(ROOT/'src/modeling/ode/run_literature_core.py'),
                                   '--hours','.1','--ligand','0','.1','--output',str(dest)],
                                  cwd=tmp,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            record=json.loads((dest/'run.json').read_text())
            self.assertEqual(record['status'],'TERMINAL_NORMAL')
            self.assertIn('src/modeling/ode/literature_core.py',record['sha256'])
            with (dest/'timecourses.csv').open() as f: rows=list(csv.DictReader(f))
            self.assertTrue(rows)
            self.assertEqual({row['ligand_normalized'] for row in rows},{'0.0','0.1'})

    def test_repeat_run_preserves_all_existing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'run'
            command=[sys.executable,str(ROOT/'src/modeling/ode/run_literature_core.py'),
                     '--output',str(dest)]
            first=subprocess.run(command,cwd=tmp,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            plot=subprocess.run([sys.executable,str(ROOT/'src/modeling/ode/plot_literature_core.py'),
                                 str(dest/'timecourses.csv')],cwd=tmp,capture_output=True,text=True)
            self.assertEqual(plot.returncode,0,plot.stderr)
            before={p.name:p.read_bytes() for p in dest.iterdir()}
            repeat=subprocess.run(command+['--hours','.1','--ligand','0'],
                                  cwd=tmp,capture_output=True,text=True)
            self.assertNotEqual(repeat.returncode,0)
            self.assertIn('choose a new directory',repeat.stderr)
            self.assertEqual(before,{p.name:p.read_bytes() for p in dest.iterdir()})
            self.assertEqual(len((dest/'run_state_events.tsv').read_text().splitlines()),2)

    def test_existing_empty_directory_or_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind in ('directory','file'):
                dest=Path(tmp)/kind
                if kind=='directory': dest.mkdir()
                else: dest.write_text('preserve me')
                result=subprocess.run([sys.executable,str(ROOT/'src/modeling/ode/run_literature_core.py'),
                                       '--output',str(dest)],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('already exists',result.stderr)
                if kind=='directory': self.assertEqual(list(dest.iterdir()),[])
                else: self.assertEqual(dest.read_text(),'preserve me')


if __name__=='__main__':
    unittest.main()
