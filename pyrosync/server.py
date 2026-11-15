"""Local dashboard plus a narrow MiroFish scenario API. No credentials in browser."""
import argparse
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from .mirofish import ROOT, MiroFishError, ScenarioStore, doctor


def handler_class(store):
    class Handler(SimpleHTTPRequestHandler):
        def reply(self, code, value):
            body = json.dumps(value, allow_nan=False).encode()
            self.send_response(code)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            try:
                if path == '/api/mirofish':
                    return self.reply(200,doctor(store.root, store.client))
                match = re.fullmatch(r'/api/scenarios/([0-9a-f]{20})(/report)?',path)
                if match:
                    run_id, report = match.groups()
                    state = store.get(run_id)
                    if report:
                        if state['phase'] != 'completed':
                            return self.reply(409,{'error':'Report is not complete'})
                        return self.reply(200,{'markdown':(store.path(run_id)/'report.md').read_text(),
                                               'release_status':'synthetic_research_only'})
                    return self.reply(200,state)
                if path.startswith('/api/'):
                    return self.reply(404,{'error':'Unknown API route'})
                super().do_GET()
            except FileNotFoundError:
                self.reply(404,{'error':'Scenario not found'})
            except (ValueError, MiroFishError):
                self.reply(502,{'error':'MiroFish is unavailable or returned an incompatible response'})

        def do_POST(self):
            # Same-origin JSON requests only; the server binds to loopback.
            expected = {'http://'+self.headers.get('Host','')}
            origin = self.headers.get('Origin')
            if origin and origin not in expected:
                return self.reply(403,{'error':'Cross-origin mutation denied'})
            if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
                return self.reply(415,{'error':'Use application/json'})
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 8192:
                    return self.reply(413,{'error':'Invalid request size'})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data,dict):
                    raise ValueError('JSON object required')
                path = urlsplit(self.path).path
                if path == '/api/scenarios':
                    allowed = {'country','month','policy','reviewers','reviews_per_day','max_rounds','replicate'}
                    if not {'country','month'} <= data.keys() or data.keys()-allowed:
                        raise ValueError('Expected country, month and supported scenario settings')
                    return self.reply(200,store.prepare(**data))
                match = re.fullmatch(r'/api/scenarios/([0-9a-f]{20})/advance',path)
                if match:
                    store.start(match[1])
                    return self.reply(202,store.get(match[1]))
                self.reply(404,{'error':'Unknown API route'})
            except FileNotFoundError:
                self.reply(404,{'error':'Build the country archive first or use an existing scenario ID'})
            except (ValueError,TypeError) as exc:
                self.reply(400,{'error':str(exc)})
            except MiroFishError as exc:
                self.reply(502,{'error':str(exc)})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    args = parser.parse_args()
    store = ScenarioStore()
    handler = partial(handler_class(store),directory=str(ROOT/'web_app'))
    with ThreadingHTTPServer(('127.0.0.1',args.port),handler) as server:
        print(f'PyroSync: http://127.0.0.1:{args.port}',flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
