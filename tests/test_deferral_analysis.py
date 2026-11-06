import unittest
from ml.deferral_analysis import analyze, risk_coverage, export_rows


class DeferralTests(unittest.TestCase):
    def test_ties_are_threshold_blocks_and_order_invariant(self):
        a = risk_coverage([True, False, True], [1, 1, 0])
        b = risk_coverage([False, True, True], [1, 1, 0])
        self.assertEqual(a, b)
        self.assertEqual(a['points'][0]['accepted'], 2)
        self.assertAlmostEqual(a['aurc'], 4/9)

    def test_empty_curve_and_invalid_scores(self):
        self.assertIsNone(risk_coverage([], [])['aurc'])
        with self.assertRaises(ValueError):
            risk_coverage([True], [float('nan')])

    def test_replay_defers_and_empty_set_ranks_last(self):
        profile = dict(classes=['healthy', 'blight'], temperature=1,
                       method='LAC', qhat=.1, guidance_enabled=False)
        rows = export_rows([
            dict(id='a', label='healthy', logits=[0, 0]),
            dict(id='b', label='healthy', logits=[5, 0]),
        ], 'field', profile)
        result = analyze(rows, 2)
        self.assertEqual(result['accepted_coverage'], 0)
        self.assertIsNone(result['accepted_accuracy']['value'])
        self.assertEqual(result['curves']['set_size_empty_last']['points'][0]['risk'], 0)
        self.assertEqual(result['singleton_top1_accuracy']['denominator'], 1)

    def test_unknown_action_and_duplicates_rejected(self):
        row = dict(image_id='a', true_label='healthy', pred_label='healthy',
                   confidence=.9, raw_confidence=.9, conformal_set='healthy', triage_action='monitor')
        with self.assertRaises(ValueError):
            analyze([row], 2)
        row['triage_action'] = 'expert'
        with self.assertRaises(ValueError):
            analyze([row, row], 2)

    def test_unknown_rows_not_mixed_with_known_coverage(self):
        self.assertEqual(export_rows([dict(label='unknown')], 'field', {'classes':['healthy']}), [])
