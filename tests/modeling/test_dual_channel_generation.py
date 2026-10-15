"""Check regeneration independently of the saved signal CSV inputs."""
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np

from src.modeling.dual_channel.generate_inputs import generate
from src.modeling.dual_channel.replay import run

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT/'experiments/dual-channel/ode-linked'
CORE_AVAILABLE = importlib.util.find_spec('src.modeling.ode.literature_core') is not None


@unittest.skipUnless(CORE_AVAILABLE, 'Combined PR #19 + #20 checkout required for ODE regeneration')
class GenerationTests(unittest.TestCase):
    def test_frozen_parameters_reproduce_inputs_and_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs = root/'parameters'
            inputs.mkdir()
            # No saved output CSV is accessible to the generator here.
            for name in ('scenario.json', 'generation-design.json', 'channel3.json', 'channel18.json'):
                shutil.copy2(FIXTURES/'inputs'/name, inputs/name)
            output = root/'generated'
            source = ROOT/'experiments/ode-model/configs/literature_core_source.json'
            record = generate(inputs, output, source)
            self.assertEqual({n:v['rows'] for n,v in record['outputs'].items()},
                             {'ode-endpoints.csv':18, 'calibration.csv':9, 'evaluation.csv':36})
            for name in record['outputs']:
                with (FIXTURES/'inputs'/name).open() as f: expected = list(csv.DictReader(f))
                with (output/name).open() as f: actual = list(csv.DictReader(f))
                self.assertEqual(len(actual), len(expected))
                for left, right in zip(actual, expected):
                    self.assertEqual(left.keys(), right.keys())
                    for key in right:
                        try: value = float(right[key])
                        except ValueError: self.assertEqual(left[key], right[key])
                        else:
                            np.testing.assert_allclose(float(left[key]), value, rtol=1e-7, atol=1e-9,
                                                       err_msg=f'{name}: {right["sample_id"]}: {key}')
            before = {p.name:p.read_bytes() for p in output.iterdir()}
            with self.assertRaises(FileExistsError): generate(inputs, output, source)
            self.assertEqual(before, {p.name:p.read_bytes() for p in output.iterdir()})
            summary = run(output, root/'replay', ROOT/'experiments/economic/configs/eco_model_example_model.json',
                          'SIM_V4_MI1TO10_CE10TO1_Q1_8H_A480')
            expected = json.loads((FIXTURES/'results/summary.json').read_text())
            np.testing.assert_allclose(summary['coefficients'], expected['coefficients'], rtol=1e-7, atol=1e-7)
            for ratio in summary['scenario_metrics']:
                for model in ('channel3', 'channel18', 'dual'):
                    for metric, value in summary['scenario_metrics'][ratio][model].items():
                        np.testing.assert_allclose(value, expected['scenario_metrics'][ratio][model][metric],
                                                   rtol=1e-7, atol=1e-7)
