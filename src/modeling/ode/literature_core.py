"""Six independent ODE states, with source rate identifiers retained."""
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT/'experiments/ode-model/configs'
SOURCE_PATH = CONFIG_DIR/'literature_core_source.json'
PROJECT_PATH = CONFIG_DIR/'literature_core_project.json'
STATES = ['G_trimer', 'Ga_GTP', 'scaffold_bound', 'Fus3_active', 'Sst2_active', 'color_au']
RECONSTRUCTED = ['G_trimer','Ga_GTP','Ga_GDP','Gbg_free','scaffold_free',
                 'scaffold_bound','Fus3','Fus3_active','Sst2','Sst2_active','color_au']
CORE_RATE_IDS = ('k4','k41','k5','k6','k7','k71','k8','k9','k91','k10','k11')


class LiteratureCoreModel:
    def __init__(self, parameters_path=PROJECT_PATH, source_path=SOURCE_PATH):
        self.parameters_path = Path(parameters_path).resolve()
        self.parameters = json.loads(self.parameters_path.read_text())
        if self.parameters.get('schema_version') != 1:
            raise ValueError('Unsupported parameter schema')
        self.source_path = Path(source_path).resolve()
        self.source = json.loads(self.source_path.read_text())
        if self.source.get('time_unit') != 's' or self.source.get('concentration_unit') != 'uM':
            raise ValueError('Source units must be s and uM')
        self.rates = {k: self.source['parameters'][k]['value'] for k in CORE_RATE_IDS}
        if not all(np.isfinite(v) and v >= 0 for v in self.rates.values()):
            raise ValueError('Source rates must be finite and nonnegative')
        self.input = self._read_group('input', ('u_max_per_second','K_L_normalized'))
        self.output = self._read_group('output', ('b','a','K','n','delta'))
        for name in ('K_L_normalized',):
            if self.input[name] <= 0:
                raise ValueError(f'{name} must be positive')
        for name in ('K','n'):
            if self.output[name] <= 0:
                raise ValueError(f'{name} must be positive')
        y = self.source['initial_uM']
        if not all(np.isfinite(v) and v >= 0 for v in y.values()):
            raise ValueError('Source initial states must be finite and nonnegative')
        self.pools = np.array([
            y['G_trimer']+y['Ga_GTP']+y['Ga_GDP'],
            y['G_trimer']+y['Gbg_free']+y['scaffold_bound'],
            y['scaffold_free']+y['scaffold_bound'],
            y['Fus3']+y['Fus3_active'], y['Sst2']+y['Sst2_active']])
        if self.pools[3] <= 0:
            raise ValueError('Total Fus3 must be positive')
        self.initial = np.array([y[name] for name in STATES[:-1]]+[0.])

    def _read_group(self, group, names):
        result = {}
        for name in names:
            entry = self.parameters[group][name]
            if not all(entry.get(key) for key in ('status','source','unit')):
                raise ValueError(f'{group}.{name} needs status, source and unit')
            value = float(entry['value'])
            if not np.isfinite(value) or value < 0:
                raise ValueError(f'{group}.{name} must be finite and nonnegative')
            result[name] = value
        return result

    def reconstruct(self, y):
        """Expand a six-state vector or trajectory into the reference ordering."""
        H,A,Q,Fp,Zp,C = np.asarray(y)
        Ta,Tb,Ts,Tf,Tz = self.pools
        return np.array([H,A,Ta-H-A,Tb-H-Q,Ts-Q,Q,Tf-Fp,Fp,Tz-Zp,Zp,C])

    def drive(self, ligand):
        if not np.isfinite(ligand) or ligand < 0:
            raise ValueError('Normalized ligand must be finite and nonnegative')
        return self.input['u_max_per_second']*ligand/(self.input['K_L_normalized']+ligand)

    def rhs(self, t, y, ligand):
        H,A,D,B,S,Q,F,Fp,Z,Zp,C = self.reconstruct(y)
        p, o = self.rates, self.output
        act = self.drive(ligand)*H
        hydrolysis = (p['k4']+p['k41']*Zp)*A
        reassembly = p['k5']*D*B
        dq = p['k6']*S*B-(p['k7']+p['k71']*Zp)*Q
        df = p['k8']*Q*F-(p['k9']+p['k91']*Z)*Fp
        dz = p['k10']*Fp*Z-p['k11']*Zp
        m = Fp/self.pools[3]
        # A tiny negative intermediate solver iterate must not enter a fractional power.
        positive_m = max(float(m), 0.)
        h = positive_m**o['n']/(o['K']**o['n']+positive_m**o['n'])
        dc = (o['b']+o['a']*h-o['delta']*C)/3600
        return np.array([-act+reassembly,act-hydrolysis,dq,df,dz,dc])

    def solve(self, ligand, times, method='Radau'):
        self.drive(ligand)
        times = np.asarray(times, dtype=float)
        if times.ndim != 1 or len(times)<2 or not np.isfinite(times).all() or times[0]!=0 or np.any(np.diff(times)<=0):
            raise ValueError('Times must be finite, start at zero and increase strictly')
        sol = solve_ivp(lambda t,y:self.rhs(t,y,ligand), (0,times[-1]),self.initial,
                        t_eval=times,method=method,rtol=1e-9,atol=1e-12)
        if not sol.success:
            raise RuntimeError(sol.message)
        return sol
