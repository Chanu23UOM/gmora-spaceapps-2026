import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError

from api.index import handler


class VercelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def post(self,payload,origin):
        return urlopen(Request(self.base+'/api/scenarios',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':origin}))

    def test_public_capabilities_do_not_claim_live_cloud_connection(self):
        with urlopen(self.base+'/api/mirofish') as r:d=json.load(r)
        self.assertFalse(d['connected']);self.assertEqual(d['hosting_mode'],'public_archive')
        with urlopen(self.base+'/api/research') as r:d=json.load(r)
        self.assertIn('sensor_validation_audit',d['results'])

    def test_https_same_origin_can_prepare_without_provider_credentials(self):
        with self.post({'country':'Sri_Lanka','month':'2025-08'},self.base.replace('http:','https:')) as r:d=json.load(r)
        self.assertEqual(d['phase'],'prepared');self.assertFalse(d['busy'])
        self.assertEqual(d['capacity_baseline']['daily_capacity'],80)

    def test_cross_origin_and_invalid_input_are_rejected(self):
        with self.assertRaises(HTTPError) as ctx:self.post({'country':'Sri_Lanka','month':'2025-08'},'https://unrelated.example')
        self.assertEqual(ctx.exception.code,403)
        with self.assertRaises(HTTPError) as ctx:self.post({'country':'Sri_Lanka','month':'2026-01'},self.base)
        self.assertEqual(ctx.exception.code,400)
