import http.server
import socketserver
import requests
import os.path


PORT = 11234
REDIRECT_HOST = 'https://mhcadminproxy-ci.aws.wgen.net'
STATIC_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lantern-inst-config')

SERVED_STATIC_FILES_MAP = {
    '/config.js': os.path.join(STATIC_FILES_DIR, 'config.js'),
    '/index.html': os.path.join(STATIC_FILES_DIR, 'index.html'),
    '/scripts.js': os.path.join(STATIC_FILES_DIR, 'scripts.js'),
    '/styles.css': os.path.join(STATIC_FILES_DIR, 'styles.css'),
    '/': os.path.join(STATIC_FILES_DIR, 'index.html'),
}
STATIC_SCRIPT_PATHS = [
    '/config.js',
    '/scripts.js',
]

SERVER_PATHS = list(SERVED_STATIC_FILES_MAP.keys())


class Proxy(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        print(f'Requested: {self.path}')
        headers = {}

        if self.path in SERVER_PATHS:
            print('processing static file for path: ', self.path)
            response_content = open(SERVED_STATIC_FILES_MAP[self.path]).read().encode()
            if self.path in STATIC_SCRIPT_PATHS:
                # add content type so that browser knew these are scripts
                headers['content-type'] = 'application/javascript'
        else:
            response = requests.get(REDIRECT_HOST + self.path)
            response_content = response.content

        self.send_response(200)
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(response_content)


class ReusableAddressServer(socketserver.ForkingTCPServer):
    # avoid Socket in Use error
    allow_reuse_address = True


httpd = ReusableAddressServer(('', PORT), Proxy)

print("serving at port", PORT)
httpd.serve_forever()
