import copy
import json
import unittest
from pathlib import Path

import numpy as np

from pyrosync.data import parse_row, load_country
from pyrosync.pipeline import analyze, occupancy
from pyrosync.forecast import benchmark, predict, interval_radius
from pyrosync.evidence import evidence_packet, verify_claims, render_brief

ROOT = Path(__file__).resolve().parents[1]


def row(**changes):
    value = dict(latitude='7.2', longitude='80.2', scan='1', track='1', frp='4',
                 acq_date='2025-01-01', acq_time='30', satellite='Terra', confidence='80',
                 daynight='N', type='0')
    value.update(changes)
    return value


class DataTests(unittest.TestCase):
    def test_utc_padding_and_provenance(self):
        r = parse_row(row(), 'modis', 42)
        self.assertEqual(r.utc, '2025-01-01T00:30:00+00:00')
        self.assertEqual(r.row, 42)

    def test_reject_invalid_numeric_time_confidence(self):
        for change in [dict(latitude='nan'), dict(frp='inf'), dict(scan='0'), dict(longitude='181'),
                       dict(acq_time='2460'), dict(confidence='101'), dict(type='8')]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                parse_row(row(**change), 'modis', 2)

    def test_union_idempotence_across_satellite_and_daynight(self):
        records = [parse_row(row(), 'modis', 2),
                   parse_row(row(confidence='n', satellite='N', acq_time='1400', daynight='D'), 'viirs-snpp', 2),
                   parse_row(row(acq_date='2025-01-02'), 'modis', 3)]
        payload = analyze(records, 'fixture')
        self.assertEqual(payload['summary']['active_cell_days'], 2)
        self.assertEqual(payload['summary']['multi_sensor_cell_days'], 1)
        self.assertEqual(occupancy(records), occupancy(records * 2))
        self.assertEqual(sum(d['active_cells'] for d in payload['daily']), 2)
        self.assertEqual(sum(c['cell_days'] for c in payload['map_cells']), 2)

    def test_static_and_low_confidence_do_not_enter_default_target(self):
        records = [parse_row(row(type='2'), 'modis', 2),
                   parse_row(row(confidence='29'), 'modis', 3),
                   parse_row(row(confidence='l'), 'viirs-snpp', 2)]
        payload = analyze(records, 'fixture')
        self.assertEqual(payload['summary']['active_cell_days'], 0)
        self.assertEqual(len(occupancy(records, quality=False)), 1)
        self.assertEqual(payload['daily'][0]['industrial_raw'], 1)


class ForecastTests(unittest.TestCase):
    def test_weekly_baseline_and_finite_nonnegative_predictions(self):
        values = np.arange(84, dtype=float) % 17
        np.testing.assert_equal(predict(values, 'last_week'), values[-7:])
        for model in ('last_week', 'trailing_28', 'weekday_8w', 'ridge_ar'):
            result = predict(values, model)
            self.assertEqual(len(result), 7)
            self.assertTrue(np.isfinite(result).all() and (result >= 0).all())
        self.assertEqual(predict(np.zeros(84), 'ridge_ar').sum(), 0)

    def test_calibration_order_statistic(self):
        residuals = np.tile(np.arange(1, 14)[:,None], (1,7))
        np.testing.assert_equal(interval_radius(residuals), np.repeat(12, 7))

    def test_holdout_cannot_influence_selection_calibration_or_prior_predictions(self):
        y = 8+np.arange(365)%7+np.sin(np.arange(365)/15)*4
        before = benchmark(y)
        altered = y.copy()
        altered[273:] += 1000
        after = benchmark(altered)
        self.assertEqual(before['selected_model'], after['selected_model'])
        pre_a = [p for p in before['predictions'] if p['split'] != 'holdout']
        pre_b = [p for p in after['predictions'] if p['split'] != 'holdout']
        self.assertEqual(pre_a, pre_b)
        for fold in before['predictions']:
            self.assertLess(fold['train_end'], fold['origin'])
            if fold['split'] == 'selection':
                self.assertLessEqual(fold['origin'], '2025-06-24')
            if fold['split'] == 'holdout':
                self.assertGreaterEqual(fold['origin'], '2025-10-01')
        first_a = next(p for p in before['predictions'] if p['split']=='holdout')
        first_b = next(p for p in after['predictions'] if p['split']=='holdout')
        self.assertEqual(first_a['predicted'], first_b['predicted'])


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'country':'fixture', 'summary':{'raw_rows':10, 'active_cell_days':4,
                        'multi_sensor_cell_days':2}, 'benchmark':{'selected_model':'last_week',
                        'promotion_passed':False}, 'limitations':['No coverage masks.']}

    def test_brief_and_claim_tampering(self):
        packet = evidence_packet(self.payload)
        self.assertIn('10', render_brief(self.payload, packet))
        bad = copy.deepcopy(packet['claims'])
        bad[0]['value'] = 11
        with self.assertRaises(ValueError):
            verify_claims(self.payload, bad)
        bad[0]['value'] = 10
        bad[0]['evidence'] = '/invented'
        with self.assertRaises(ValueError):
            verify_claims(self.payload, bad)
        with self.assertRaises(ValueError):
            verify_claims(self.payload, [{'name':'wildfire_probability','value':.9}])
        with self.assertRaises(ValueError):
            verify_claims(self.payload, [])
        packet['country'] = 'another country'
        with self.assertRaises(ValueError):
            render_brief(self.payload, packet)


class ArtifactTests(unittest.TestCase):
    def test_real_data_invariants_and_provenance(self):
        expected = {'Sri_Lanka':11654, 'Argentina':389118}
        for country, n in expected.items():
            payload = json.loads((ROOT/'web_app'/'data'/f'{country}.json').read_text())
            self.assertEqual(payload['summary']['raw_rows'], n)
            self.assertEqual(sum(d['raw'] for d in payload['daily']), n)
            self.assertEqual(sum(d['active_cells'] for d in payload['daily']), payload['summary']['active_cell_days'])
            self.assertTrue(all(d['multi_sensor_cells'] <= d['active_cells'] <= d['filtered_raw'] <= d['raw']
                                for d in payload['daily']))
            self.assertEqual(len(payload['daily']), 365)
            self.assertEqual(len(payload['benchmark']['results']), 4)
            self.assertTrue(all(0 <= d['retained_fraction'] <= 1 for d in payload['sensor_dropout']))
            for month, entry in payload['map_months'].items():
                cells = json.loads((ROOT/'web_app'/entry['path']).read_text())
                total = sum(c['cell_days'] for c in cells if c['type'] == 0)
                self.assertEqual(total, sum(d['active_cells'] for d in payload['daily'] if d['date'].startswith(month)))


if __name__ == '__main__':
    unittest.main()
