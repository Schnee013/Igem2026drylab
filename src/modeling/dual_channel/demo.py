"""Seeded synthetic wiring example; no wet-lab observations."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from src.modeling.dual_channel.calibration import fit, predict, eco_scenarios
from src.modeling.economic.eco_model_pkg.config import load_model


def run(output, eco_config):
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261010)
    rows = []
    for batch in range(3):
        for target in (0., 40., 120.):
            for background in (0., 80., 200.):
                x = np.array([.008*target+.004*background, .014*target+.001*background])
                x += rng.normal(0, .008, 2) + batch * np.array([.001, -.001])
                rows.append(dict(sample_id=f'SIM-{batch}-{int(target)}-{int(background)}',
                                 batch=batch, target=target, background=background,
                                 x3=x[0], x18=x[1], evidence_status='simulated'))
    with (output/'simulated_pairs.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    train, validation = rows[:18], rows[18:]
    x = np.array([[r['x3'], r['x18']] for r in train])
    y = np.array([r['target'] for r in train])
    xv = np.array([[r['x3'], r['x18']] for r in validation])
    yv = np.array([r['target'] for r in validation])
    model = fit(x, y, sample_ids=[r['sample_id'] for r in train], protocol_id='SIM_ONLY_v1',
                evidence_status='simulated', reference_basis='spike_count')
    eco = load_model(eco_config)
    metrics = {}
    for name, columns in [('channel3', [0]), ('channel18', [1]), ('dual', [0, 1])]:
        design = np.column_stack((np.ones(len(x)), x[:, columns]))
        beta = np.linalg.lstsq(design, y, rcond=None)[0]
        estimates = np.column_stack((np.ones(len(xv)), xv[:, columns])) @ beta
        err = estimates-yv
        metrics[name] = dict(mae=float(np.abs(err).mean()), rmse=float(np.sqrt((err**2).mean())),
                             background_only_false_positive_at_middle=int(np.sum((yv == 0) & (estimates >= eco.middle_from_density))),
                             background_only_n=int(np.sum(yv == 0)),
                             per_background_mae={str(b): float(np.abs(err[[r['background']==b for r in validation]]).mean()) for b in (0.,80.,200.)})
    predictions = [predict(model, v, protocol_id='SIM_ONLY_v1') for v in xv]
    cases = {}
    for target in (10., 60., 80.):
        signal = [.008*target+.004*80, .014*target+.001*80]
        p = predict(model, signal, protocol_id='SIM_ONLY_v1')
        cases[str(target)] = dict(prediction=p, eco=eco_scenarios(p, eco))
    result = dict(evidence_status='simulated', seed=20261010,
                  generating_equations=['x3=0.008*target+0.004*background+noise+batch_shift',
                                        'x18=0.014*target+0.001*background+noise+batch_shift'],
                  noise_sd=.008, batch_shift_per_index=[.001,-.001],
                  density_unit=eco.density_unit, training_batches=[0,1], validation_batches=[2],
                  coefficients=model.coefficients.tolist(), condition_number=model.condition_number,
                  validation_metrics=metrics, validation_predictions=predictions,
                  usable_validation_n=sum(p['within_calibration_range'] for p in predictions),
                  conditional_cases=cases, eco_config=str(eco_config),
                  eco_config_sha256=hashlib.sha256(eco_config.read_bytes()).hexdigest())
    (output/'simulation.json').write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--eco-config', type=Path, required=True)
    args = parser.parse_args()
    run(args.output, args.eco_config)
