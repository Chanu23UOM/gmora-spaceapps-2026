import copy
import csv
import json
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path

import numpy as np

from pyrosync.data import SOURCES,load_country
from pyrosync.pipeline import analyze
from pyrosync.research import candidate,evaluate_country,mapping


class HistoryTests(unittest.TestCase):
    def test_missing_inputs_are_unknown_and_leap_day_is_present(self):
        with tempfile.TemporaryDirectory() as root:
            records,inputs=load_country(Path(root),'Sri_Lanka',2024,allow_missing=True)
        result=analyze(records,'Sri_Lanka',2024,inputs,include_map=False,diagnostics=False)
        self.assertEqual(len(result['daily']),366)
        day=next(d for d in result['daily'] if d['date']=='2024-02-29')
        self.assertIsNone(day['active_cells'])
        self.assertEqual(day['observed_active_cells'],0)
        self.assertEqual(day['activity_status'],'unknown_missing_input')
        self.assertEqual(day['observation_coverage'],'unknown')

    def test_invalid_archive_rows_are_audited_without_modifying_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'modis/2024/modis_2024_Sri_Lanka.csv';p.parent.mkdir(parents=True)
            fields=['latitude','longitude','scan','track','frp','acq_date','acq_time','satellite','confidence','daynight','type']
            row=['7','80','1','1','4','2024-02-29','0001','Terra','80','N','0']
            with p.open('w') as f:
                w=csv.writer(f);w.writerow(fields);w.writerow(row);bad=row.copy();bad[4]='-0.18';w.writerow(bad)
            original=p.read_bytes()
            records,inputs=load_country(root,'Sri_Lanka',2024,allow_missing=True,invalid_rows='quarantine')
            self.assertEqual(len(records),1)
            self.assertEqual(inputs[0]['rows'],2)
            self.assertEqual(inputs[0]['accepted_rows'],1)
            self.assertEqual(inputs[0]['quarantined_rows'][0]['line'],3)
            self.assertEqual(p.read_bytes(),original)
            with self.assertRaises(ValueError):load_country(root,'Sri_Lanka',2024,allow_missing=True)


class ResearchTests(unittest.TestCase):
    def test_new_candidate_is_nonnegative_and_handles_zero_activity(self):
        np.testing.assert_equal(candidate(np.zeros(84),'ewma_14'),np.zeros(7))
        self.assertTrue((candidate(np.arange(84),'ewma_14')>=0).all())

    def test_frozen_outer_selection_cannot_see_test_targets(self):
        daily=[];start=date(2020,1,1)
        for i in range((date(2023,1,1)-start).days):
            daily.append({'date':(start+timedelta(days=i)).isoformat(),'active_cells':10+i%7,
                          'complete_source_inputs':True,'source_cells':{'modis':2},'viirs_active_cells':3})
        plan={'models':['last_week','trailing_28','ewma_14'],'initial_history_days':84,
              'outer_folds':[{'selection_years':[2020],'calibration_year':2021,'test_year':2022}]}
        payload={'country':'fixture','daily':daily}
        before,pred_before=evaluate_country(payload,plan)
        after_payload=copy.deepcopy(payload)
        for d in after_payload['daily']:
            if d['date'].startswith('2022'):d['active_cells']+=1000
        after,pred_after=evaluate_country(after_payload,plan)
        self.assertEqual(before['outer_folds'][0]['selected_model'],after['outer_folds'][0]['selected_model'])
        self.assertEqual([f for f in pred_before if f['year']<2022],[f for f in pred_after if f['year']<2022])
        self.assertTrue(all(f['train_end']<f['origin'] for f in pred_before))

    def test_missing_source_prevents_scoring_instead_of_becoming_zero(self):
        result,_=evaluate_country({'country':'fixture','daily':[{'date':'2020-01-01','active_cells':None,'complete_source_inputs':False}]},{})
        self.assertEqual(result['status'],'insufficient_inputs')

    def test_mapping_fits_only_training_data_and_identity_is_identity(self):
        train=[{'date':f'2020-01-{i:02d}','source_cells':{'modis':i},'viirs_active_cells':i*2} for i in range(1,25)]
        test=[{'date':'2021-01-01','source_cells':{'modis':10},'viirs_active_cells':999}]
        self.assertEqual(mapping(train,test,'identity'),[10])
        self.assertEqual(mapping(train,test,'monthly_ratio'),[20])
        first=mapping(train,test,'monthly_quantile_mapping')
        test[0]['viirs_active_cells']=0
        self.assertEqual(first,mapping(train,test,'monthly_quantile_mapping'))
