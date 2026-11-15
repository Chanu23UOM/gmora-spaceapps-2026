import io
import json
import threading
import unittest
import types
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch, Mock

from pyrosync.vertex_bridge import GoogleTokens, handler_class


class Tokens:
    def __init__(self):
        self.calls = 0

    def headers(self,url):
        self.calls += 1
        return {'authorization':'Bearer google-test-only'}


class Response(io.BytesIO):
    status = 200
    headers = {'Content-Type':'application/json'}


class VertexTests(unittest.TestCase):
    def test_explicit_service_account_is_loaded_without_falling_back_to_another_account(self):
        credentials = Mock()
        credentials.before_request.side_effect = lambda request,method,url,headers: headers.update({'authorization':'Bearer test-only'})
        google = types.ModuleType('google')
        auth = types.ModuleType('google.auth')
        transport = types.ModuleType('google.auth.transport')
        requests = types.ModuleType('google.auth.transport.requests')
        google.auth = auth
        auth.load_credentials_from_file = Mock(return_value=(credentials,'test-project'))
        auth.default = Mock()
        requests.Request = Mock()
        modules = {'google':google,'google.auth':auth,'google.auth.transport':transport,'google.auth.transport.requests':requests}
        with patch.dict('sys.modules',modules):
            tokens = GoogleTokens('test-project','/private/service-account.json')
            self.assertEqual(tokens.headers('https://aiplatform.googleapis.com')['authorization'],'Bearer test-only')
            tokens.headers('https://aiplatform.googleapis.com')
        self.assertEqual(auth.load_credentials_from_file.call_count,1)
        auth.default.assert_not_called()
        self.assertEqual(credentials.before_request.call_count,2)

    def test_relay_replaces_local_key_with_google_credentials_on_each_request(self):
        tokens = Tokens()
        server = ThreadingHTTPServer(('127.0.0.1',0),handler_class('test-project','global','local-test-only',tokens))
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        real_open = urllib.request.urlopen
        observed = []
        def send(request,*args,**kwargs):
            if isinstance(request,urllib.request.Request) and request.full_url.startswith('https://aiplatform.googleapis.com/'):
                observed.append(request)
                return Response(b'{"choices":[]}')
            return real_open(request,*args,**kwargs)
        try:
            with patch('urllib.request.urlopen',side_effect=send):
                for _ in range(2):
                    request = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/v1/chat/completions',
                               json.dumps({'model':'google/test-model','messages':[]}).encode(),
                               {'Authorization':'Bearer local-test-only','Content-Type':'application/json'})
                    with real_open(request) as response:
                        self.assertEqual(json.load(response),{'choices':[]})
                request.remove_header('Authorization')
                with self.assertRaises(urllib.error.HTTPError) as error:
                    real_open(request)
                self.assertEqual(error.exception.code,401)
            self.assertEqual(tokens.calls,2)
            self.assertTrue(all(r.get_header('Authorization')=='Bearer google-test-only' for r in observed))
            self.assertTrue(all('/projects/test-project/locations/global/' in r.full_url for r in observed))
        finally:
            server.shutdown();server.server_close();thread.join()

    def test_reject_invalid_project_and_location(self):
        for project, location in [('test-project','../../evil'),('http://evil','global')]:
            with self.assertRaises(ValueError):
                handler_class(project,location,'test-only',Tokens())
