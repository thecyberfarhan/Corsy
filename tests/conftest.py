import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


class _Handler(BaseHTTPRequestHandler):
    """A tiny target that models each CORS misconfiguration on its own path."""
    def log_message(self, *a):
        pass

    def do_GET(self):
        origin = self.headers.get('Origin', '')
        own = 'http://127.0.0.1:%d' % self.server.server_address[1]
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        p = self.path
        if p.startswith('/reflect'):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Credentials', 'true')
        elif p.startswith('/wildcard_cred'):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Credentials', 'true')
        elif p.startswith('/wildcard_plain'):
            self.send_header('Access-Control-Allow-Origin', '*')
        elif p.startswith('/null'):
            if origin in (own, 'null'):
                self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Access-Control-Allow-Credentials', 'true')
        elif p.startswith('/hang'):
            import time
            time.sleep(10)
        self.end_headers()
        self.wfile.write(b'ok')


@pytest.fixture(scope='session')
def server():
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield 'http://127.0.0.1:%d' % httpd.server_address[1]
    httpd.shutdown()
