import unittest
from ml.consolidate_field_review import consolidate

def row(key,scene=None,label='healthy',state='pending_capture_and_background_review'):
    return dict(id=key,scene_group=scene or key,label=label,source='s',sha256=key,path=key,source_url='url',license='CC BY 4.0',domain='natural_background',review_status=state,label_status='publisher_label_unverified')
def pair(a,b,status='same_leaf_or_scene'):
    return dict(first=a,second=b,first_sha256=a,second_sha256=b,status=status)

class ConsolidationTests(unittest.TestCase):
    def test_transitive_conflict_includes_old_duplicate_copies(self):
        staged=[row('a','old'),row('b','old',state='duplicate_copy'),row('c',label='septoria')]
        result=consolidate(staged,[staged[0],staged[2]],[pair('a','c')])
        self.assertEqual({r['review_status'] for r in result},{'quarantine_label_conflict'})
        self.assertEqual(len({r['review_capture_group'] for r in result}),1)

    def test_precautionary_groups_are_deterministic_and_unassigned(self):
        rows=[row('a'),row('b'),row('c')];pairs=[pair('b','c'),pair('a','b','possible_shared_capture_keep_together')]
        a=consolidate(rows,rows,pairs);b=consolidate(rows[::-1],rows[::-1],pairs[::-1])
        self.assertEqual(a,b)
        self.assertEqual(sum(r['review_status']=='pending_capture_provenance' for r in a),1)
        self.assertEqual({r['role'] for r in a},{'unassigned'})
        self.assertEqual({r['physical_capture_group'] for r in a},{'unresolved'})

    def test_prior_and_label_concerns_propagate(self):
        for state in ('excluded_prior_scene','requires_source_label_review'):
            a=row('a');b=row('b')
            if state=='excluded_prior_scene':b['review_status']=state;screened=[a]
            else:b['label_status']=state;screened=[a,b]
            out=consolidate([a,b],screened,[pair('a','b')])
            expected='excluded_prior_scene' if state=='excluded_prior_scene' else 'quarantine_source_label_review'
            self.assertEqual({r['review_status'] for r in out},{expected})

    def test_stale_or_incomplete_review_rejected(self):
        rows=[row('a'),row('b')]
        with self.assertRaises(ValueError):consolidate(rows,rows[:1],[])
        p=pair('a','b');p['first_sha256']='changed'
        with self.assertRaises(ValueError):consolidate(rows,rows,[p])
        p=pair('a','b','pending_full_size_review')
        with self.assertRaises(ValueError):consolidate(rows,rows,[p])
