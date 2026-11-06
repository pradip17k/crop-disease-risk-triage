import unittest
from ml.stage_field_review import stage


def row(key,label='healthy',status='quarantine'):
    return dict(id=key,label=label,status=status,source='test',source_url='test',license='CC BY 4.0')


class StagingTests(unittest.TestCase):
    def test_prior_exclusion_propagates_through_duplicate_chain(self):
        result=stage([row('a'),row('b'),row('c')],[('a','b'),('b','c')],{'a'})
        self.assertTrue(all(r['review_status']=='excluded_prior_scene' for r in result))
        self.assertTrue(all(r['role']=='unassigned' for r in result))

    def test_label_conflict_excludes_whole_group(self):
        result=stage([row('a'),row('b','septoria')],[('a','b')],set())
        self.assertTrue(all(r['review_status']=='excluded_label_conflict' for r in result))

    def test_representative_is_deterministic_but_not_training_ready(self):
        rows=[row('b'),row('a')]
        result=stage(rows,[('a','b')],set())
        self.assertEqual(result,stage(rows[::-1],[('b','a')],set()))
        self.assertEqual(result[0]['review_status'],'pending_capture_and_background_review')
        self.assertEqual(result[1]['review_status'],'duplicate_copy')
        self.assertEqual(result[0]['physical_capture_group'],'unresolved')

    def test_missing_review_identity_rejected(self):
        with self.assertRaises(ValueError): stage([row('a')],[('a','missing')],set())
