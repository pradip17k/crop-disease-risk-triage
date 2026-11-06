import unittest,math
from ml.reliability import *
from ml.calibrate import run
class ReliabilityTests(unittest.TestCase):
    def test_probabilities(self):
        self.assertEqual(probabilities([1000,1000]),[.5,.5])
        with self.assertRaises(ValueError):probabilities([float('nan')])
    def test_rank(self):
        self.assertEqual(quantile([.1,.2,.3,.4],.4),.3)
        self.assertIsNone(quantile([.1,.2],.1))
    def test_sets(self):
        self.assertEqual(prediction_set([.9,.1],['a','b'],dict(method='LAC',qhat=.1)),['a'])
        self.assertEqual(prediction_set([.5,.5],['a','b'],dict(method='APS',qhat=.9)),[])
    def test_metrics(self):
        r=metrics([dict(label='a',logits=[math.log(.8),math.log(.2)]),dict(label='b',logits=[math.log(.8),math.log(.2)])],['a','b'])
        self.assertAlmostEqual(r['ece'],.3);self.assertAlmostEqual(r['brier'],.68)
        self.assertEqual(len(r['risk_coverage']),1)
    def test_actions(self):
        self.assertEqual(decide('a',1,['a'],{})['action'],'expert')
        self.assertEqual(decide('a',1,['a'],{},quality_ok=False)['action'],'recapture')
        self.assertEqual(decide('a',.6,['a','b'],{})['action'],'recapture')
        self.assertEqual(decide('a',1,['a'],dict(independently_evaluated=True,guidance_enabled=True,min_confidence=.8))['action'],'guidance')
    def test_partition_leakage(self):
        row=dict(id='a',group='same-leaf',label='a',logits=[2,0])
        with self.assertRaisesRegex(ValueError,'leakage'):
            run(dict(classes=['a','b'],model_sha256='hash',temperature_rows=[row],conformal_rows=[row],test_rows=[row]))
if __name__=='__main__':unittest.main()
