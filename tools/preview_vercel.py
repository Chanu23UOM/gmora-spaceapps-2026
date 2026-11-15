"""Preview Vercel's API adapter and static files together, before deployment."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from api.index import handler


class Preview(handler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            return super().do_GET()
        return SimpleHTTPRequestHandler.do_GET(self)


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    server=ThreadingHTTPServer(('127.0.0.1',8767),partial(Preview,directory=str(root/'web_app')))
    print('Vercel-compatible preview: http://127.0.0.1:8767',flush=True)
    server.serve_forever()
