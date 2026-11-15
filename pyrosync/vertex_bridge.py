"""Loopback OpenAI-compatible relay with refreshed Google ADC credentials.

All MiroFish processes use this relay so long simulations do not retain an
expired Google bearer token. Google credentials never enter MiroFish's .env.
"""
import argparse
import hmac
import json
import os
import re
import threading
import time
from datetime import datetime, timezone
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .mirofish import ROOT


def local_settings():
    path = ROOT/'.integrations/mirofish/.env'
    settings = {}
    if path.exists():
        for line in path.read_text().splitlines():
            key, separator, value = line.partition('=')
            if separator and not key.lstrip().startswith('#'):
                settings[key.strip()] = value.strip().strip('"\'')
    return {**settings, **os.environ}


class GoogleTokens:
    def __init__(self, project, credentials_file=None):
        self.project = project
        self.credentials_file = credentials_file
        self.credentials = None
        self.lock = threading.Lock()

    def headers(self, url):
        import google.auth
        from google.auth.transport.requests import Request
        with self.lock:
            if self.credentials is None:
                options = {'scopes':['https://www.googleapis.com/auth/cloud-platform'],
                           'quota_project_id':self.project}
                if self.credentials_file:
                    self.credentials, _ = google.auth.load_credentials_from_file(self.credentials_file, **options)
                else:
                    self.credentials, _ = google.auth.default(**options)
            headers = {}
            self.credentials.before_request(Request(), 'POST', url, headers)
            return headers


def handler_class(project, location, local_key, tokens, usage_path=None):
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]', project):
        raise ValueError('Invalid Vertex project ID')
    if not re.fullmatch(r'[a-z0-9-]+', location):
        raise ValueError('Invalid Vertex location')
    host = 'aiplatform.googleapis.com' if location == 'global' else location+'-aiplatform.googleapis.com'
    url = f'https://{host}/v1/projects/{project}/locations/{location}/endpoints/openapi/chat/completions'
    usage_lock=threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not log prompts, authorization headers or model responses.

        def reply(self, status, value):
            body = json.dumps(value).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path != '/health':
                return self.reply(404,{'error':{'message':'Unknown route'}})
            return self.reply(200,{'service':'PyroSync Vertex Bridge','project':project,'location':location,
                                   'authentication':'Google Application Default Credentials; verified on model request'})

        def do_POST(self):
            if self.path != '/v1/chat/completions':
                return self.reply(404,{'error':{'message':'Unknown route'}})
            if not hmac.compare_digest(self.headers.get('Authorization',''), 'Bearer '+local_key):
                return self.reply(401,{'error':{'message':'Local bridge authentication required'}})
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 2_000_000:
                    return self.reply(413,{'error':{'message':'Invalid request size'}})
                body = self.rfile.read(length)
                data = json.loads(body)
                if not isinstance(data,dict) or not isinstance(data.get('messages'),list):
                    return self.reply(400,{'error':{'message':'Expected a chat-completions request'}})
                headers = {'Content-Type':'application/json'}
                try:
                    headers.update(tokens.headers(url))
                except Exception:
                    return self.reply(503,{'error':{'message':'Google authentication unavailable. Check the configured service-account credential or Application Default Credentials.'}})
                request = urllib.request.Request(url,body,headers)
                started=time.monotonic()
                try:
                    response = urllib.request.urlopen(request,timeout=180)
                except urllib.error.HTTPError as exc:
                    return self.reply(exc.code,{'error':{'message':f'Vertex AI returned HTTP {exc.code}; verify project access, API, billing and model availability.'}})
                except (urllib.error.URLError,TimeoutError,OSError):
                    return self.reply(502,{'error':{'message':'Vertex AI connection failed'}})
                with response:
                    if 'application/json' in response.headers.get('Content-Type',''):
                        content=response.read()
                        if usage_path is not None:
                            try:
                                result=json.loads(content)
                                entry={'timestamp':datetime.now(timezone.utc).isoformat(),'model':result.get('model',data.get('model')),
                                       'usage':result.get('usage'),'elapsed_seconds':round(time.monotonic()-started,3)}
                                with usage_lock:
                                    with usage_path.open('a') as log:log.write(json.dumps(entry)+'\n')
                            except (ValueError,OSError):pass
                        self.send_response(response.status)
                        self.send_header('Content-Type','application/json')
                        self.send_header('Content-Length',str(len(content)))
                        self.end_headers();self.wfile.write(content)
                        return
                    self.send_response(response.status)
                    self.send_header('Content-Type',response.headers.get('Content-Type','application/json'))
                    self.send_header('Cache-Control','no-store')
                    self.end_headers()
                    while chunk := response.read1(65536):
                        self.wfile.write(chunk)
                        self.wfile.flush()
            except (ValueError,TypeError):
                self.reply(400,{'error':{'message':'Invalid chat-completions JSON'}})
            except (BrokenPipeError,ConnectionResetError):
                pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=5002)
    args = parser.parse_args()
    settings = local_settings()
    project = settings.get('VERTEX_PROJECT','')
    location = settings.get('VERTEX_LOCATION','global')
    key = settings.get('LLM_API_KEY','')
    if not project or not key:
        raise SystemExit('Configure VERTEX_PROJECT and the local bridge LLM_API_KEY in MiroFish .env')
    handler = handler_class(project,location,key,GoogleTokens(project,settings.get('GOOGLE_APPLICATION_CREDENTIALS')),ROOT/'.integrations/vertex-usage.jsonl')
    with ThreadingHTTPServer(('127.0.0.1',args.port),handler) as server:
        print(f'Vertex bridge: http://127.0.0.1:{args.port} · {project}/{location}',flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
