"""Regenerate synthetic paired inputs using the frozen r04 ODE parameters."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy


def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(input_dir, output, source):
    # PR #19 supplies the shared core; regression replay remains independent.
    from src.modeling.ode.literature_core import LiteratureCoreModel
    from src.modeling.ode import literature_core

    scenario = json.loads((input_dir/'scenario.json').read_text())
    design = json.loads((input_dir/'generation-design.json').read_text())
    protocol = scenario['protocol']
    rates = scenario['release_rates_fmol_per_worm_h']
    models = {ch: LiteratureCoreModel(input_dir/f'channel{ch}.json', source) for ch in ('3', '18')}
    hours = protocol['sensor_read_time_h']
    for ch, model in models.items():
        adapter = model.parameters['calibration_adapter']
        if adapter['channel'] != ch or adapter['read_time_h'] != hours:
            raise ValueError('Channel configuration and protocol disagree')
    output.mkdir(parents=True, exist_ok=False)
    absorbance = protocol['epsilon_L_mol_cm']*protocol['effective_path_length_cm']*1e-6
    blank = {ch: model.solve(0., [0., hours*3600]).y[-1, -1] for ch, model in models.items()}

    def concentrations(target, background, denominator=None):
        q3 = rates['target_ascr3']['value']
        q18 = rates['target_ascr18']['value']
        if denominator is not None:
            total = q3+q18
            q3, q18 = total/(1+denominator), total*denominator/(1+denominator)
        factor = (protocol['collection_duration_h']*protocol['recovery_fraction'] /
                  (1000*protocol['effective_collection_volume_mL']*protocol['sensor_sample_dilution_factor']))
        return ((q3*target+rates['background_ascr3']['value']*background)*factor,
                (q18*target+rates['background_ascr18']['value']*background)*factor)

    def endpoint(ch, s3, s18):
        model = models[ch]
        a = model.parameters['calibration_adapter']
        ligand = (a['S3_weight']*s3+a['S18_weight']*s18)/a['ligand_reference_nM']
        pigment = float(model.solve(ligand, [0., hours*3600]).y[-1, -1])
        if not np.isfinite(pigment) or pigment < 0:
            raise ValueError('Nonphysical pigment endpoint')
        return ligand, pigment, float(absorbance*(pigment-blank[ch]))

    training, endpoints, evaluation = [], [], []
    for target in design['training_targets']:
        for background in design['training_backgrounds']:
            name = f'SIM-V4-T{target:g}-B{background:g}'
            s3, s18 = concentrations(target, background)
            signals = {}
            for ch in models:
                ligand, pigment, signal = endpoint(ch, s3, s18)
                w3, w18 = design['assumed_pigment_slopes'][ch]
                assumed = protocol['blank_pigment_equivalent_uM']+w3*s3+w18*s18
                signals[ch] = signal
                endpoints.append(dict(sample_id=name, channel=ch,
                    target_density_J2_per_100cm3=target, background_density_L4_per_100cm3=background,
                    ascr3_nM=s3, ascr18_nM=s18, effective_L=ligand, assumed_pigment_uM=assumed,
                    ode_pigment_uM=pigment, error_uM=pigment-assumed, ode_A480=absorbance*pigment,
                    ode_A480_blank_corrected=signal, data_origin='synthetic_assumption'))
            training.append(dict(sample_id=name, target=target, background=background,
                                 x3=signals['3'], x18=signals['18'], data_origin='synthetic_ODE', split='calibration'))
    endpoints.sort(key=lambda row: (0 if row['channel']=='3' else 1))
    base_ratio = rates['target_ascr18']['value']/rates['target_ascr3']['value']
    for denominator in design['target_ratio_denominators']:
        for target in design['evaluation_targets']:
            for background in design['evaluation_backgrounds']:
                s3, s18 = concentrations(target, background, denominator)
                signals = {ch: endpoint(ch, s3, s18)[2] for ch in models}
                evaluation.append(dict(sample_id=f'SIM-RATIO{denominator}-T{target:g}-B{background:g}',
                    split='heldout_same_generator' if np.isclose(denominator, base_ratio) else 'ratio_shift_stress',
                    mi_ascr3_to_ascr18=f'1:{denominator}', target=float(target), background=float(background),
                    x3=signals['3'], x18=signals['18'], data_origin='synthetic_ODE'))
    outputs = {'ode-endpoints.csv': endpoints, 'calibration.csv': training, 'evaluation.csv': evaluation}
    for name, rows in outputs.items():
        write_csv(output/name, rows)
    paths = [input_dir/name for name in ('scenario.json', 'generation-design.json', 'channel3.json', 'channel18.json')]
    paths += [source, Path(literature_core.__file__), Path(__file__)]
    record = dict(observed_at=datetime.now(timezone.utc).isoformat(),
        scope='Frozen-parameter synthetic ODE regeneration; no refitting or empirical calibration',
        software=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        solver=dict(method='Radau', rtol=1e-9, atol=1e-12),
        units=dict(ligand='nM before adapter normalization', pigment='uM equivalent', signal='blank-corrected A480',
                   target='Mi J2/100 cm3', background='Ce L4/100 cm3'),
        inputs=[dict(path=str(p.resolve()), sha256=sha(p)) for p in paths],
        outputs={name: dict(rows=len(rows), sha256=sha(output/name)) for name, rows in outputs.items()})
    (output/'generation.json').write_text(json.dumps(record, indent=2)+'\n')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    generate(args.input_dir, args.output, args.source)
