import unittest
from pathlib import Path
from dataclasses import replace
import numpy as np
from src.modeling.dual_channel.calibration import fit, predict, eco_scenarios
from src.modeling.economic.eco_model_pkg.config import load_model

ROOT = Path(__file__).resolve().parents[2]


class DualChannelTests(unittest.TestCase):
    def setUp(self):
        self.x = np.array([[a,b] for a in (0.,1.,2.) for b in (0.,1.,2.)])
        self.y = 10+40*self.x[:,0]-2*self.x[:,1]
        self.kw = dict(sample_ids=list(range(9)), protocol_id='test', evidence_status='simulated', reference_basis='spike_count')
        self.model = fit(self.x,self.y,**self.kw)
        self.eco = load_model(ROOT/'experiments/economic/configs/eco_model_example_model.json')

    def test_recovers_three_coefficients_including_negative(self):
        np.testing.assert_allclose(self.model.coefficients,[10,40,-2],atol=1e-10)

    def test_rank_and_duplicate_guard(self):
        with self.assertRaises(ValueError):
            fit(np.column_stack((self.x[:,0], self.x[:,0])),self.y,**self.kw)
        with self.assertRaises(ValueError):
            fit(self.x,self.y,**dict(self.kw,sample_ids=[1]*9))

    def test_joint_hull_not_just_rectangle(self):
        x = np.array([[0,0],[2,0],[0,2],[.2,.2],[.5,.5]])
        m = fit(x,10+x[:,0],**dict(self.kw,sample_ids=list(range(5))))
        self.assertIn('outside_joint_signal_hull', predict(m,[1.5,1.5],protocol_id='test')['reasons'])

    def test_qc_saturation_protocol_nonfinite_block_eco(self):
        for kwargs in ({'saturated':True}, {'qc_pass':False}, {'protocol_id':'different'}):
            p = predict(self.model,[1,1],**dict(protocol_id='test',**{}) | kwargs)
            self.assertEqual(eco_scenarios(p,self.eco)['status'],'blocked')
        self.assertIn('invalid_signal',predict(self.model,[float('nan'),1],protocol_id='test')['reasons'])

    def test_negative_prediction_preserved_and_blocked(self):
        m = replace(self.model,coefficients=np.array([-100.,1.,1.]))
        p = predict(m,[1,1],protocol_id='test')
        self.assertLess(p['density'],0)
        self.assertIn('negative_density',p['reasons'])

    def test_crossed_thresholds_include_middle_and_both_sides(self):
        p = predict(self.model,[1,1],protocol_id='test')
        p.update(prediction_interval_95=[8.,82.],calibration_density_range=[0.,100.])
        result = eco_scenarios(p,self.eco)
        self.assertTrue(result['grade_uncertain'])
        self.assertEqual({r['band'] for r in result['scenarios']},{'低','中','高'})
        altered = replace(self.eco,middle_from_density=20.,high_from_density=70.)
        result = eco_scenarios(p,altered)
        self.assertTrue({20.,70.}.issubset({r['density'] for r in result['scenarios']}))

    def test_interval_and_eco_domain_guard(self):
        p = predict(self.model,[1,1],protocol_id='test')
        p['prediction_interval_95']=[5.,1000.]
        self.assertEqual(eco_scenarios(p,self.eco)['status'],'blocked')

    def test_interval_is_for_individual_prediction(self):
        m=replace(self.model,residual_variance=4.,covariance=np.zeros((3,3)))
        p=predict(m,[1,1],protocol_id='test')
        self.assertGreater(p['prediction_interval_95'][1]-p['density'],3.92)


if __name__=='__main__':
    unittest.main()
