"""Replay regression and Eco diagnostics from frozen synthetic ODE pairs."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from .calibration import fit, predict, eco_scenarios
from src.modeling.economic.eco_model_pkg.config import load_model


def read_pairs(path):
    with path.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows or len({r['sample_id'] for r in rows}) != len(rows):
        raise ValueError('nonempty unique paired samples required')
    for row in rows:
        if row['data_origin'] != 'synthetic_ODE':
            raise ValueError('replay accepts synthetic ODE fixtures only')
        for key in ('target', 'background', 'x3', 'x18'):
            row[key] = float(row[key])
            if not np.isfinite(row[key]):
                raise ValueError('nonfinite paired value')
        if min(row['target'], row['background']) < 0:
            raise ValueError('reference densities must be nonnegative')
    return rows


def error_metrics(rows, estimates):
    residual = np.asarray(estimates)-np.array([r['target'] for r in rows])
    return dict(n=len(rows), rmse=float(np.sqrt(np.mean(residual**2))),
                mae=float(np.abs(residual).mean()), max_absolute_error=float(np.abs(residual).max()))


def run(input_dir, output, eco_config, protocol_id):
    training = read_pairs(input_dir/'calibration.csv')
    evaluation = read_pairs(input_dir/'evaluation.csv')
    if {r['sample_id'] for r in training} & {r['sample_id'] for r in evaluation}:
        raise ValueError('calibration/evaluation sample overlap')
    if {(r['target'], r['background']) for r in training} & {(r['target'], r['background']) for r in evaluation}:
        raise ValueError('evaluation combinations must differ from calibration')
    x = np.array([[r['x3'], r['x18']] for r in training])
    y = np.array([r['target'] for r in training])
    model = fit(x, y, sample_ids=[r['sample_id'] for r in training], protocol_id=protocol_id,
                evidence_status='simulated', reference_basis='spike_count')
    eco = load_model(eco_config)
    variants = [('channel3', [0]), ('channel18', [1]), ('dual', [0, 1])]
    betas = {name: np.linalg.lstsq(np.column_stack((np.ones(len(x)), x[:, cols])), y, rcond=None)[0]
             for name, cols in variants}
    results = []
    for row in evaluation:
        signal = np.array([row['x3'], row['x18']])
        prediction = predict(model, signal, protocol_id=protocol_id)
        estimates = {name: float(np.r_[1., signal[cols]] @ betas[name]) for name, cols in variants}
        results.append(dict(sample_id=row['sample_id'], ratio=row['mi_ascr3_to_ascr18'],
                            reference_density=row['target'], background=row['background'],
                            estimates=estimates, prediction=prediction, eco=eco_scenarios(prediction, eco)))
    metrics = {}
    for ratio in sorted({r['mi_ascr3_to_ascr18'] for r in evaluation}):
        indices = [i for i, r in enumerate(evaluation) if r['mi_ascr3_to_ascr18'] == ratio]
        metrics[ratio] = {name: error_metrics([evaluation[i] for i in indices],
                                             [results[i]['estimates'][name] for i in indices]) for name, _ in variants}
    output.mkdir(parents=True, exist_ok=False)
    summary = dict(evidence_status='simulated', coefficients=model.coefficients.tolist(),
                   condition_number=model.condition_number, density_unit=eco.density_unit,
                   calibration_metrics=error_metrics(training, np.c_[np.ones(len(x)), x] @ model.coefficients),
                   scenario_metrics=metrics, interval_scope='formal OLS diagnostic; no empirical coverage',
                   input_files=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                for p in [input_dir/'calibration.csv', input_dir/'evaluation.csv', eco_config]],
                   scope='regression replay of saved ODE signals, not new ODE fitting or wet-lab validation')
    for filename, data in [('summary.json', summary), ('predictions.json', results)]:
        (output/filename).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    plot(results, output/'dual-channel-check.png')
    return summary


def plot(results, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
    baseline = [r for r in results if r['ratio'] == '1:10']
    for name in ('channel3', 'channel18', 'dual'):
        axes[0].scatter([r['reference_density'] for r in baseline],
                        [r['estimates'][name] for r in baseline], label=name)
    axes[0].plot([-10, 100], [-10, 100], '--', color='grey')
    axes[0].set(xlabel='Assumed Mi density (J2/100 cm3)', ylabel='Estimated density', title='New combinations: Mi 1:10')
    for ratio in sorted({r['ratio'] for r in results}):
        rows = [r for r in results if r['ratio'] == ratio]
        axes[1].scatter([r['reference_density'] for r in rows],
                        [r['estimates']['dual']-r['reference_density'] for r in rows], label=ratio)
    axes[1].axhline(0, linestyle='--', color='grey')
    axes[1].set(xlabel='Assumed Mi density (J2/100 cm3)', ylabel='Estimate minus reference', title='Fixed coefficients; changed Mi ratio')
    for ax in axes:
        ax.legend()
        ax.grid(alpha=.2)
    fig.suptitle('Synthetic ODE fixtures: no measurement noise or empirical validation')
    fig.savefig(path, dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--eco-config', type=Path, required=True)
    parser.add_argument('--protocol-id', required=True)
    args = parser.parse_args()
    run(args.input_dir, args.output, args.eco_config, args.protocol_id)
