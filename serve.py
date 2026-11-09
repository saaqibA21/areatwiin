"""Tiny development server: python serve.py [port]

Like `python -m http.server`, but sends no-cache headers so edits show up on reload.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = partial(NoCacheHandler, directory=".")
    print(f"AreaTwin running at http://localhost:{port}/  (Ctrl+C to stop)")
    ThreadingHTTPServer(("", port), handler).serve_forever()
