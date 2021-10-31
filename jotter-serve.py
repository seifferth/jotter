#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from jotter import find_jotter_root, survey
from jotter_html import produce_html

index_md = """
# Jotter Index

- [citekeys](/citekeys)
"""

class JotterServer(BaseHTTPRequestHandler):
    def do_GET(self):
        jotter_root = find_jotter_root()
        filename_map, citekey_map, keyword_map = survey(jotter_root)
        payload = None
        if self.path == "/":
            doc = {
                "_content": index_md,
                "title": "Jotter Index",
            }
            payload = produce_html(
                doc,
                css_root=jotter_root + "/.jotter/css",
                internal_links=True,
                resolve_citekeys=False,
            )
        elif self.path == "/citekeys":
            doc = {
                "_content": "# Citekeys\n\n" + \
                            "\n".join(map(
                                lambda x: f"- [{x}](/{x})",
                                citekey_map.keys(),
                            )) + \
                            "\n",
                "title": "Jotter Citekeys",
            }
            payload = produce_html(
                doc,
                css_root = jotter_root + "/.jotter/css",
                internal_links = True,
                resolve_citekeys = False,
            )
        elif self.path[1:] in citekey_map.keys():
            payload = produce_html(
                citekey_map[self.path[1:]],
                citekey_map = citekey_map,
                css_root = jotter_root + "/.jotter/css",
                internal_links = False,
                resolve_citekeys = False,
            )
        if payload == None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404: File not found")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(payload.encode("utf-8"))

if __name__ == "__main__":
    hostName, serverPort = "localhost", 8080
    webServer = HTTPServer((hostName, serverPort), JotterServer)
    print(f"Dynamic jotter server started on http://{hostName}:{serverPort}")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
