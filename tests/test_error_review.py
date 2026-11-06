import unittest,math
from ml.report_errors import wilson,describe
class ErrorReviewTests(unittest.TestCase):
    def test_intervals_do_not_claim_certainty_for_small_perfect_samples(self):
        low,high=wilson(1,1);self.assertLess(low,.5);self.assertAlmostEqual(high,1)
        low,high=wilson(0,1);self.assertAlmostEqual(low,0);self.assertGreater(high,.5)
        self.assertIsNone(wilson(0,0))
    def test_confident_errors_and_absent_classes_remain_visible(self):
        rows=[dict(label='healthy',logits=[10,0]),dict(label='blight',logits=[10,0])]
        r=describe(rows,['healthy','blight','other'],1)
        self.assertEqual(r['accuracy'],.5);self.assertEqual(r['wrong_with_score_at_least_08'],1)
        self.assertEqual(r['per_class'][1]['confusions']['healthy'],1)
        self.assertIsNone(r['per_class'][2]['recall'])
