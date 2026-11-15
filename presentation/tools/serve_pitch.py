"""Serve pitch-only cards; research.json reads the live backend, with no credentials."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path.split('?')[0]=='/research.json':
   try:
    with urllib.request.urlopen('http://127.0.0.1:8765/api/research',timeout=5) as r:data=r.read()
    self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
   except OSError:self.send_error(503,'Live research backend unavailable')
  else:super().do_GET()
if __name__=='__main__':
 with ThreadingHTTPServer(('127.0.0.1',8766),partial(Handler,directory=str(ROOT/'stage'))) as server:
  print('Pitch stage http://127.0.0.1:8766',flush=True);server.serve_forever()
