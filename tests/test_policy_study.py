import json
import tempfile
import unittest
from pathlib import Path

from pyrosync.policy_study import freeze_inputs,cases


class PolicyStudyTests(unittest.TestCase):
    def test_dashboard_rebuild_cannot_change_frozen_study_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'web_app/data';source.mkdir(parents=True)
            (source/'Sri_Lanka.json').write_text('{"version":1}')
            plan={'countries':['Sri_Lanka']}
            snapshot=freeze_inputs(plan,root)
            (source/'Sri_Lanka.json').write_text('{"version":2}')
            self.assertEqual(json.loads((freeze_inputs(plan,root)/'Sri_Lanka.json').read_text()),{'version':1})
            (snapshot/'Sri_Lanka.json').write_text('{"version":3}')
            with self.assertRaises(ValueError):freeze_inputs(plan,root)

    def test_policy_pairs_share_country_replicate_and_bounded_plan(self):
        plan=json.loads((Path(__file__).resolve().parents[1]/'experiments/mirofish-policies-v1.json').read_text())
        values=cases(plan)
        self.assertEqual(len(values),8)
        self.assertEqual(len(set(values)),8)
        self.assertEqual(plan['max_rounds'],1)
        for country in plan['countries']:
            for replicate in plan['replicates']:
                self.assertEqual({p for c,p,r in values if c==country and r==replicate},{'independent','coordinated'})
