#!/usr/bin/env python3
"""Run the retained sampler with the public BoundFunc namespace on this build.

The retained implementation refers to func.BoundFunc. PyRosetta 2026.29 exposes
the identical bounded function class under core.scoring.constraints. This alias
repairs that API lookup only; sampling, constraints and acceptance tests remain.
"""
from pyrosetta import rosetta as R
import sample_disulfide_lid


if __name__ == '__main__':
    if not hasattr(R.core.scoring.func, 'BoundFunc'):
        R.core.scoring.func.BoundFunc = R.core.scoring.constraints.BoundFunc
    sample_disulfide_lid.main()
