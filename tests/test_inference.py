"""Optional integration checks against the actual local pilot bundle."""
import unittest,base64,json,hashlib,importlib.util,io,csv
from pathlib import Path
from unittest.mock import patch
import server
AVAILABLE=all(importlib.util.find_spec(m) for m in ['numpy','PIL','onnxruntime']) and (server.BUNDLE/'classifier.onnx').exists()
@unittest.skipUnless(AVAILABLE,'Local trained model and inference dependencies required')
class InferenceTests(unittest.TestCase):
    def test_bundle_identity_and_real_prediction(self):
        r=server.infer(dict(image=base64.b64encode((server.WEB/'samples/early.jpg').read_bytes()).decode()))
        self.assertEqual(r['mode'],'model');self.assertAlmostEqual(sum(r['probabilities'].values()),1)
        self.assertIn(r['label'],r['probabilities']);self.assertIn(r['decision']['action'],{'expert','recapture'})
        self.assertFalse(r['unknown_check_available'])
    def test_quality_gate_precedes_classifier(self):
        from PIL import Image
        b=io.BytesIO();Image.new('RGB',(256,256),'black').save(b,format='PNG')
        r=server.infer(dict(image=base64.b64encode(b.getvalue()).decode()))
        self.assertFalse(r['quality_ok']);self.assertEqual(r['decision']['action'],'recapture')
        self.assertNotIn('confidence',r)
    def test_bad_image_is_not_a_prediction(self):
        with self.assertRaises(Exception):server.infer(dict(image=base64.b64encode(b'invalid').decode()))
    def test_model_profile_hash_mismatch_blocks_connection(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'classifier.onnx').write_bytes(b'invalid');(root/'profile.json').write_text(json.dumps(dict(model_sha256='wrong')))
            with patch.object(server,'BUNDLE',root):self.assertFalse(server.bundle_status()['model_connected'])
        server.load_runtime.cache_clear()
    def test_test_cohort_count_matches_published_report(self):
        report=json.loads((server.BUNDLE/'evaluation.json').read_text())
        with (server.ROOT/report.get('manifest_path','data/manifest.csv')).open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(report['controlled']['after']['count'],sum(r['role']=='test' for r in rows))
        self.assertFalse(report['guidance_enabled']);self.assertEqual(report['field']['model_sha256'],hashlib.sha256((server.BUNDLE/'classifier.onnx').read_bytes()).hexdigest())
