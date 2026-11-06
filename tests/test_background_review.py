import copy
import unittest
from ml.review_field_backgrounds import apply_review

class BackgroundReviewTests(unittest.TestCase):
    def setUp(self):
        self.row=dict(id='a',sha256='abc',sheet='s',tile=1,source='source',label='healthy',role='unassigned')
        self.index=dict(rows=[self.row])
        self.decisions=dict(rows=[dict(self.row,domain='natural_background',label_status='publisher_label_unverified',review_level='contact_sheet_screen')])

    def test_screening_never_establishes_readiness(self):
        self.index['rows'][0]['role']='test'
        rows,summary=apply_review(self.index,self.decisions)
        self.assertEqual(rows[0]['role'],'unassigned')
        self.assertEqual(rows[0]['physical_capture_group'],'unresolved')
        self.assertFalse(summary['training_ready'])

    def test_missing_duplicate_and_stale_reviews_rejected(self):
        for mutation in ('missing','duplicate','hash','tile','domain'):
            d=copy.deepcopy(self.decisions)
            if mutation=='missing':d['rows']=[]
            elif mutation=='duplicate':d['rows']*=2
            elif mutation=='hash':d['rows'][0]['sha256']='changed'
            elif mutation=='tile':d['rows'][0]['tile']=2
            else:d['rows'][0]['domain']='invented'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):apply_review(self.index,d)

    def test_conflicts_and_composites_quarantined(self):
        d=copy.deepcopy(self.decisions);d['rows'][0]['label_status']='conflicting_scene_labels'
        self.assertEqual(apply_review(self.index,d)[0][0]['review_status'],'quarantine_label_conflict')
        d=copy.deepcopy(self.decisions);d['rows'][0]['domain']='composite_or_illustration'
        self.assertEqual(apply_review(self.index,d)[0][0]['review_status'],'quarantine_composite')
