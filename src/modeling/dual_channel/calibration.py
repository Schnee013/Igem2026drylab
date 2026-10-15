"""Exploratory three-coefficient calibration and conditional Eco scenarios."""
from dataclasses import dataclass
import math
import numpy as np
from scipy.spatial import ConvexHull
from scipy.stats import t
from src.modeling.economic.eco_model_pkg.economics import evaluate

UNIT = 'J2/100 cm^3 soil'


@dataclass
class Calibration:
    coefficients: np.ndarray
    covariance: np.ndarray
    residual_variance: float
    df: int
    hull_equations: np.ndarray
    density_range: tuple[float, float]
    protocol_id: str
    evidence_status: str
    reference_basis: str
    condition_number: float


def fit(x, density, *, sample_ids, protocol_id, evidence_status, reference_basis):
    """Fit independent paired rows; x is raw minus matched blank, in fixed units.

    reference_basis: spike_count or independent_field_count.
    Protocol identity binds stage, matrix, volumes, dilution, constructs and timing.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(density, dtype=float)
    if x.ndim != 2 or x.shape[1] != 2 or y.shape != (len(x),) or len(x) <= 3:
        raise ValueError('need >3 independent rows, two channels and one density per row')
    if len(sample_ids) != len(x) or len(set(sample_ids)) != len(x):
        raise ValueError('aggregate technical repeats; sample IDs must be unique')
    if not np.isfinite(x).all() or not np.isfinite(y).all() or (y < 0).any():
        raise ValueError('finite signals and nonnegative reference densities required')
    if not protocol_id or evidence_status not in {'simulated', 'measured_unvalidated'}:
        raise ValueError('explicit protocol and exploratory evidence status required')
    if reference_basis not in {'spike_count', 'independent_field_count'}:
        raise ValueError('unknown reference basis')
    design = np.column_stack((np.ones(len(x)), x))
    beta, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank != 3 or np.ptp(y) == 0:
        raise ValueError('calibration lacks independent channel information or target variation')
    # Condition number is diagnostic; operational cutoff awaits preregistration.
    standardized = (x - x.mean(axis=0)) / x.std(axis=0)
    condition = float(np.linalg.cond(np.column_stack((np.ones(len(x)), standardized))))
    variance = float(np.sum((y - design @ beta)**2) / (len(x)-3))
    pinv = np.linalg.pinv(design)
    return Calibration(beta, variance * (pinv @ pinv.T), variance, len(x)-3,
                       ConvexHull(x).equations, (float(y.min()), float(y.max())),
                       protocol_id, evidence_status, reference_basis, condition)


def predict(model, x, *, protocol_id, saturated=False, qc_pass=True):
    """Return an untruncated OLS point and 95% individual prediction interval.

    The interval assumes independent homoscedastic normal errors and fixed x;
    it excludes counting error, blank uncertainty and unobserved batch shifts.
    """
    x = np.asarray(x, dtype=float)
    out = dict(density=None, density_unit=UNIT, prediction_interval_95=None,
               calibration_density_range=list(model.density_range),
               within_calibration_range=False, reasons=[],
               evidence_status=model.evidence_status, reference_basis=model.reference_basis,
               protocol_id=model.protocol_id)
    if x.shape != (2,) or not np.isfinite(x).all():
        out['reasons'].append('invalid_signal')
        return out
    a = np.r_[1., x]
    point = float(a @ model.coefficients)
    radius = float(t.ppf(.975, model.df) * np.sqrt(model.residual_variance + a @ model.covariance @ a))
    out.update(density=point, prediction_interval_95=[point-radius, point+radius])
    reasons = out['reasons']
    if protocol_id != model.protocol_id:
        reasons.append('protocol_mismatch')
    if saturated:
        reasons.append('saturated')
    if not qc_pass:
        reasons.append('qc_failed')
    if np.any(model.hull_equations[:, :2] @ x + model.hull_equations[:, 2] > 1e-9):
        reasons.append('outside_joint_signal_hull')
    if not model.density_range[0] <= point <= model.density_range[1]:
        reasons.append('outside_density_calibration')
    if point < 0:
        reasons.append('negative_density')
    out['within_calibration_range'] = not reasons
    return out


def eco_scenarios(prediction, eco_model):
    """Return conditional examples, never a field recommendation or ROI interval.

    Both calibration and Eco domains must cover the physical prediction interval.
    Include both sides of every crossed threshold, since costs are discontinuous.
    """
    blocked = dict(status='blocked', reasons=list(prediction['reasons']), scenarios=[])
    if not prediction['within_calibration_range']:
        return blocked
    if prediction['density_unit'] != eco_model.density_unit:
        blocked['reasons'].append('unit_mismatch')
        return blocked
    low, high = prediction['prediction_interval_95']
    physical_low = max(0., low)
    cal_low, cal_high = prediction['calibration_density_range']
    if physical_low < cal_low or high > min(cal_high, eco_model.max_density):
        blocked['reasons'].append('interval_outside_supported_density_range')
        return blocked
    values = {physical_low, high, prediction['density']}
    for boundary in (eco_model.middle_from_density, eco_model.high_from_density):
        if physical_low < boundary <= high:
            values.update((math.nextafter(boundary, -math.inf), boundary))
    rows = []
    for density in sorted(values):
        result = evaluate(density, eco_model)
        rows.append(dict(density=density, density_unit=UNIT, band=result.band,
                         detection_net_benefit_vs_uniform=result.detection_net_benefit_vs_uniform))
    return dict(status='conditional_demo_only', evidence_status=prediction['evidence_status'],
                reference_basis=prediction['reference_basis'],
                grade_uncertain=len({r['band'] for r in rows}) > 1,
                physical_interval=[physical_low, high],
                interval_truncated_at_zero=low < 0, scenarios=rows)
