"""Checks actual prepared experiment boundaries when local data exists."""
import unittest,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
@unittest.skipUnless((ROOT/'data/source-v2-training.csv').exists(),'Expanded local cohort not prepared')
class ExperimentBoundaryTests(unittest.TestCase):
    def test_previous_evaluation_groups_are_not_reused(self):
        with (ROOT/'data/manifest.csv').open(newline='') as f:old=list(csv.DictReader(f))
        with (ROOT/'data/source-v2-training.csv').open(newline='') as f:new=list(csv.DictReader(f))
        reserved={r['group'] for r in old if r['role']!='train'}
        self.assertFalse(reserved & {r['group'] for r in new})
        old_train={r['group'] for r in old if r['role']=='train'}
        self.assertTrue(all(r['role']=='train' for r in new if r['group'] in old_train))
    def test_public_check_group_remains_outside_candidate(self):
        source=json.loads((ROOT/'outputs/tomato-leaf-check-source.json').read_text())
        with (ROOT/'data/source-v2-training.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertNotIn(source['recorded_leaf_group'],{r['group'] for r in rows})
        self.assertNotIn(source['sha256'],{r['sha256'] for r in rows})
