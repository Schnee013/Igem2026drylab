"""Regenerate frozen synthetic phone signals or predict from paired blue ratios."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from .calibration import Calibration, eco_scenarios, fit, predict
from src.modeling.economic.eco_model_pkg.config import load_model
from src.modeling.ode.literature_core import LiteratureCoreModel


def read_json(path):
    return json.loads(path.read_text())


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def phone_features(ratios):
    ratios = np.asarray(ratios, dtype=float)
    if ratios.shape != (2,) or not np.isfinite(ratios).all() or np.any(ratios <= 0) or np.any(ratios > 1):
        raise ValueError('Two finite sample/sensor-blank blue ratios in (0,1] required')
    return -np.log10(ratios)


def load_calibration(path):
    d = read_json(path)
    return Calibration(np.array(d['coefficients']), np.array(d['covariance']),
        d['residual_variance'], d['df'], np.array(d['hull_equations']),
        tuple(d['calibration_density_range']), d['protocol_id'], d['evidence_status'],
        'spike_count', d['condition_number'])


def predict_ratios(model, ratios, eco):
    x = phone_features(ratios)
    prediction = predict(model, x, protocol_id=model.protocol_id)
    result = eco_scenarios(prediction, eco)
    result['scenarios'] = [{k: v for k, v in row.items() if k in ('density', 'density_unit', 'band')}
                           for row in result.get('scenarios', [])]
    return dict(blue_ratios=list(ratios), phone_delta_A=x.tolist(), prediction=prediction,
                eco=result, scope='synthetic phone example; actual device/matrix calibration required')


def regenerate(package, source, eco_config, output):
    scenario = read_json(package/'matrix.json')
    plan = read_json(package/'dual-r04/sampling-plan.json')
    protocol = scenario['protocol']
    phone = scenario['phone_readout']
    factor = (protocol['soil_volume_cm3']/100 * protocol['collection_duration_h'] *
              protocol['recovery_fraction'] / (1000 * protocol['effective_collection_volume_mL'] *
              protocol['sensor_sample_dilution_factor']))
    conversion = phone['molecular_weight_g_mol']*1e-6
    blank = protocol['blank_pigment_equivalent_uM']*conversion
    hours = protocol['sensor_read_time_h']
    rates = scenario['release_rates_fmol_per_worm_h']
    models = {ch: LiteratureCoreModel(package/f'ode-r07/channel{ch}.json', source) for ch in ('3', '18')}
    for ch, model in models.items():
        adapter = model.parameters['calibration_adapter']
        if (adapter['matrix_sha256'] != hashlib.sha256((package/'matrix.json').read_bytes()).hexdigest()
                or adapter['protocol_id'] != protocol['protocol_id']
                or adapter['channel'] != ch or adapter['read_time_h'] != hours
                or [adapter['S3_weight'], adapter['S18_weight']] != scenario['sensor_response']['weights'][ch]):
            raise ValueError('Frozen scenario and channel adapter disagree')
    training_pairs = plan['training_pairs']
    heldout_pairs = plan['heldout_pairs']+plan['additional_no_background_threshold_pairs']
    if set(map(tuple, training_pairs)) & set(map(tuple, heldout_pairs)):
        raise ValueError('Training and heldout density pairs overlap')
    output.mkdir(parents=True, exist_ok=False)

    def simulate(target, background):
        ligands = [(rates[f'target_ascr{ch}']['value']*target +
                    rates[f'background_ascr{ch}']['value']*background)*factor for ch in ('3', '18')]
        row = dict(sample_id=f'SIM-V7-T{target}-B{background}', target=target, background=background)
        for ch, model in models.items():
            adapter = model.parameters['calibration_adapter']
            ligand = np.dot(scenario['sensor_response']['weights'][ch], ligands)/adapter['ligand_reference_nM']
            c = float(model.solve(ligand, [0, hours*3600]).y[-1, -1])*conversion
            x = phone['slope_mL_per_mg']*(c-blank)
            # A zero-input sample is its own blank; remove solver roundoff only.
            if target == 0 and background == 0 and abs(x) < 1e-12:
                x = 0.0
            row.update({f'c{ch}_mg_mL': c, f'x{ch}': x, f'B{ch}_over_blank': float(10**(-x))})
        return row

    train = [simulate(*pair) for pair in training_pairs]
    heldout = [simulate(*pair) for pair in heldout_pairs]
    endpoints = [simulate(r['target_density_J2_per_100cm3'], r['background_density_L4_per_100cm3'])
                 for r in scenario['rows']]
    x = np.array([[r['x3'], r['x18']] for r in train])
    y = np.array([r['target'] for r in train])
    model = fit(x, y, sample_ids=[r['sample_id'] for r in train], protocol_id=protocol['protocol_id'],
                evidence_status='simulated', reference_basis='spike_count')
    eco = load_model(eco_config)
    metrics = {}
    for split, rows in [('calibration', train), ('heldout', heldout)]:
        estimates = []
        for row in rows:
            row['result'] = predict_ratios(model, [row['B3_over_blank'], row['B18_over_blank']], eco)
            estimates.append(row['result']['prediction']['density'])
        errors = np.array(estimates)-np.array([r['target'] for r in rows])
        metrics[split] = dict(n=len(rows), rmse=float(np.sqrt(np.mean(errors**2))),
                             mae=float(np.mean(abs(errors))), max_absolute_error=float(max(abs(errors))))
        save(output/f'{split}.json', rows)
    comparisons = {}
    for filename, rows in [('dual-r04/calibration-pairs.csv', train),
                           ('dual-r04/heldout-pairs.csv', heldout), ('ode-r07/endpoints.csv', endpoints)]:
        with (package/filename).open(newline='') as handle:
            saved = {(float(r['target']), float(r['background'])): r for r in csv.DictReader(handle)}
        if set(saved) != {(r['target'], r['background']) for r in rows}:
            raise ValueError('Frozen reference and regenerated density sets differ')
        comparisons[filename] = max(abs(r[key]-float(saved[(r['target'], r['background'])][key]))
            for r in rows for key in ('c3_mg_mL', 'c18_mg_mL', 'x3', 'x18'))
    frozen_model = load_calibration(package/'dual-r04/model.json')
    beta_error = float(max(abs(model.coefficients-frozen_model.coefficients)))
    report = dict(scope='Frozen ODE regeneration and simulated phone regression, no new fitting of ODE',
        coefficients=model.coefficients.tolist(), metrics=metrics, max_reference_difference=comparisons,
        max_coefficient_difference=beta_error,
        reference_reproduction_passed=all(v < 1e-8 for v in comparisons.values()) and beta_error < 1e-5)
    save(output/'verification.json', report)
    save(output/'endpoints.json', endpoints)
    if not report['reference_reproduction_passed']:
        raise ValueError('Regenerated results differ from frozen evidence; inspect verification.json')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    gen = sub.add_parser('regenerate')
    gen.add_argument('--package', type=Path, required=True)
    gen.add_argument('--source', type=Path, required=True)
    gen.add_argument('--eco-config', type=Path, required=True)
    gen.add_argument('--output', type=Path, required=True)
    pred = sub.add_parser('predict')
    pred.add_argument('--model', type=Path, required=True)
    pred.add_argument('--eco-config', type=Path, required=True)
    pred.add_argument('ratios', type=float, nargs=2)
    args = parser.parse_args()
    if args.command == 'regenerate':
        result = regenerate(args.package, args.source, args.eco_config, args.output)
    else:
        result = predict_ratios(load_calibration(args.model), args.ratios, load_model(args.eco_config))
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
