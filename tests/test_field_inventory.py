import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from ml import inventory_field
from ml.review_field_duplicates import duplicate_review


class FieldInventoryTests(unittest.TestCase):
    def test_duplicates_and_conflicts_are_queued_not_split(self):
        rows = [dict(id='a', label='healthy', pixel_sha256='same', dhash='0'),
                dict(id='b', label='blight', pixel_sha256='same', dhash='0'),
                dict(id='c', label='healthy', pixel_sha256='other', dhash='1')]
        result = duplicate_review(rows)
        self.assertTrue(result['exact_pixel_duplicate_groups'][0]['conflicting_labels'])
        self.assertEqual(len(result['near_duplicate_candidates']), 2)
        self.assertTrue(all(r['decision'] == 'pending_visual_review' for r in result['near_duplicate_candidates']))

    def test_prior_image_excluded_and_no_role_assigned(self):
        with tempfile.TemporaryDirectory(dir=inventory_field.ROOT/'data') as d:
            base = Path(d); img = base/'test.png'; Image.new('RGB', (20, 20), 'green').save(img)
            raw = img.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
            row = dict(id='test', source_url='unused', expected_sha256=sha)
            with patch.object(inventory_field, 'BASE', base), patch.object(inventory_field, 'fetch', return_value=raw):
                # The fetch mock must also make the file available for decoding.
                target=base/'images'/hashlib.sha256(b'test').hexdigest()
                target.parent.mkdir(); target.write_bytes(raw)
                out = inventory_field.inspect_image(row, {sha})
            self.assertEqual(out['status'], 'excluded_prior_image')
            self.assertEqual(out['role'], 'unassigned')
            self.assertEqual(out['grouping'], 'unresolved')

    def test_checksum_failure_is_quarantined(self):
        with patch.object(inventory_field, 'fetch', return_value=b'wrong file'):
            out = inventory_field.inspect_image(dict(id='test', source_url='unused', expected_sha256='bad'), set())
        self.assertEqual(out['status'], 'download_or_decode_failure')
        self.assertNotIn('pixel_sha256', out)
