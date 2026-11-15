import copy
import unittest
from datetime import date,timedelta

from pyrosync.validation import audit_country,transition_audit


class ValidationTests(unittest.TestCase):
    def test_transition_preserves_reference_change_and_exposes_instrument_offset(self):
        start=date(2024,1,1)
        days=[{'date':(start+timedelta(days=i)).isoformat(),'viirs_active_cells':10+i} for i in range(70)]
        truth=[d['viirs_active_cells'] for d in days]
        perfect=transition_audit(days,truth)
        biased=transition_audit(days,[v-5 for v in truth])
        self.assertEqual(perfect['simulated_boundaries'],2)
        self.assertEqual(perfect['mean_absolute_reference_relative_jump'],0)
        self.assertEqual(biased['mean_absolute_reference_relative_jump'],5)

    def test_transition_rejects_a_missing_calendar_day(self):
        start=date(2024,1,1)
        days=[{'date':(start+timedelta(days=i)).isoformat(),'viirs_active_cells':10} for i in range(70) if i!=30]
        with self.assertRaises(ValueError):transition_audit(days,[10]*len(days))

    def test_mapping_choice_does_not_change_when_test_reference_changes(self):
        start=date(2020,1,1)
        daily=[{'date':(start+timedelta(days=i)).isoformat(),'complete_source_inputs':True,
                'source_cells':{'modis':i%5},'viirs_active_cells':2*(i%5)} for i in range(1096)]
        plan={'outer_folds':[{'selection_years':[2020],'calibration_year':2021,'test_year':2022}],
              'calibration_candidates':['identity','monthly_ratio']}
        payload={'country':'fixture','daily':daily};before=audit_country(payload,plan)
        changed=copy.deepcopy(payload)
        for d in changed['daily']:
            if d['date'].startswith('2022'):d['viirs_active_cells']+=1000
        after=audit_country(changed,plan)
        self.assertEqual(before['outer_folds'][0]['selected_mapping'],after['outer_folds'][0]['selected_mapping'])
        self.assertEqual(before['outer_folds'][0]['selected_mapping'],'monthly_ratio')
        changed['daily'][0]['complete_source_inputs']=False
        with self.assertRaises(ValueError):audit_country(changed,plan)
