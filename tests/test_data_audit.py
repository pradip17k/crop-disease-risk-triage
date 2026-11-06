import unittest,tempfile,hashlib
from pathlib import Path
from ml.audit_manifest import audit
from ml.calibrate import run
class DataAuditTests(unittest.TestCase):
    def test_exact_duplicate_cross_role_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'a.jpg').write_bytes(b'image')
            common=dict(path='a.jpg',label='healthy',domain='controlled',sha256=hashlib.sha256(b'image').hexdigest(),source_url='https://example.org/image',license='test')
            rows=[dict(common,id='a',group='leaf1',role='train'),dict(common,id='b',group='leaf2',role='test')]
            self.assertFalse(audit(rows,root)['passes'])
    def test_checksum_and_unsafe_path(self):
        with tempfile.TemporaryDirectory() as folder:
            row=dict(id='a',path='../escape.jpg',label='healthy',domain='field',role='test',group='leaf',sha256='bad',source_url='source',license='test')
            self.assertFalse(audit([row],Path(folder))['passes'])
    def test_valid_manifest_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'a.jpg').write_bytes(b'image')
            row=dict(id='a',path='a.jpg',label='healthy',domain='field',role='test',group='leaf',sha256=hashlib.sha256(b'image').hexdigest(),source_url='source',license='test')
            r=audit([row],root);self.assertTrue(r['passes']);self.assertEqual(r['shared_labels'],['healthy'])
    def test_calibration_id_overlap_with_different_groups_is_rejected(self):
        rows={role:[dict(id='same',group=role,label='a',logits=[2,0])] for role in ['temperature_rows','conformal_rows','test_rows']}
        with self.assertRaisesRegex(ValueError,'ID leakage'):run(dict(classes=['a','b'],model_sha256='hash',**rows))
    def test_domain_and_class_results_and_no_auto_guidance(self):
        rows={role:[dict(id=role+str(i),group=role+str(i),label='a' if i%2==0 else 'b',logits=[2,0],domain='field' if i%2==0 else 'controlled') for i in range(12)] for role in ['temperature_rows','conformal_rows','test_rows']}
        profile,report=run(dict(classes=['a','b'],model_sha256='hash',**rows))
        self.assertFalse(profile['guidance_enabled']);self.assertEqual(report['by_class']['a']['count'],6)
        self.assertEqual(set(report['by_domain']),{'field','controlled'})
if __name__=='__main__':unittest.main()

from ml.prepare_manifest import assign
class SplitTests(unittest.TestCase):
    def test_group_assignment_is_order_independent(self):
        rows=[dict(id=str(i),group='leaf'+str(i//2)) for i in range(30)]
        first={r['id']:r['role'] for r in assign(rows)}
        second={r['id']:r['role'] for r in assign(list(reversed(rows)))}
        self.assertEqual(first,second)
        for i in range(0,30,2):self.assertEqual(first[str(i)],first[str(i+1)])
