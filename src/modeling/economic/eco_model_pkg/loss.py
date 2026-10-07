"""Convert pre-plant M. incognita density to tomato yield loss."""

from __future__ import annotations

import math

from .config import Model


def relative_yield_fraction(density: float, model: Model) -> float:
    """Return relative yield from the literature-fitted Seinhorst equation.

    For the fixed demo model, density is J2/100 cm^3 soil. Values above the
    maximum density observed in the source experiment are rejected.
    """

    if not math.isfinite(density) or density < 0 or density > model.max_density:
        raise ValueError(f"密度必须是 0 至 {model.max_density:g} 之间的有限数")
    if density <= model.tolerance_density:
        return 1.0
    relative_yield = model.minimum_relative_yield + (
        1.0 - model.minimum_relative_yield
    ) * model.seinhorst_z ** (density / model.tolerance_density - 1.0)
    return min(1.0, max(model.minimum_relative_yield, relative_yield))


def yield_loss_fraction(density: float, model: Model) -> float:
    """Return the untreated yield-loss fraction (1 - relative yield)."""

    return 1.0 - relative_yield_fraction(density, model)
