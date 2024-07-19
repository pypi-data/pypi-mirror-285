from .htmls import forwarder_html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from _thread import start_new_thread
from time import sleep
from myHttp import http
from myBasics import strToBase64
from typing import NoReturn
import socket


__all__ = ['start_forward_server']


def addr_valid(addr: str) -> bool:
    addr = addr.replace(' ', '')
    ip = addr
    if (addr.find(':') != -1):
        if (len(addr.split(':')) != 2):
            return False
        port = addr.split(':')[1]
        try:
            port_int = int(port)
        except:
            return False
        if (str(port_int) != port):
            return False
        if (port_int <= 0 or port_int > 65535):
            return False
        ip = addr.split(':')[0]
    ip_parts = ip.split('.')
    if (len(ip_parts) != 4):
        return False
    for part in ip_parts:
        try:
            part_int = int(part)
        except:
            return False
        if (str(part_int) != part):
            return False
        if (part_int < 0 or part_int > 255):
            return False
    return True


class Request(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        if (path in ('/', '/index.html')):
            self.process_main()
            return
        path = path[1:]
        if (path.find('/') == -1):
            addr = path
        else:
            addr = path[:path.find('/')]
        if (not addr_valid(addr)):
            self.process_addr_invalid(addr)
            return
        url = 'http://' + path
        response = http(url, Decode=False, Timeout=1000, Retry=False)
        if (response['status'] != 0):
            self.process_cannot_open(url)
            return
        status = response['code']
        self.send_response(status)
        self.send_cache_header()
        self.send_cors_header()
        self.send_header('Connection', 'keep-alive')
        content = response['text']
        try:
            content = content.decode('utf-8')
        except:
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            return
        self.send_header('Content-Type', 'text/html')
        replacer = 'class="$jtc.phg.proxy-replacer$" href="'
        replaced = 'href="/' + addr
        html = content.replace(replacer, replaced)
        replacer2 = '$$$jtc.py-html-graph.data-server-loc$$$'
        replacer3 = '$$jtc.py-html-graph.data-server-loc$'
        replacer4 = '$jtc.py-html-graph.data-server-loc$$'
        replacer2 = strToBase64(replacer2)
        replacer3 = strToBase64(replacer3)
        replacer4 = strToBase64(replacer4)
        target = 'http://' + addr
        if (len(target) % 3 == 2):
            target += '$'
        elif (len(target) % 3 == 1):
            target += '$$'
        target = strToBase64(target)
        html = html.replace(replacer2, target)
        html = html.replace(replacer3, target)
        html = html.replace(replacer4, target)
        html = html.encode('utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)
        return

    def process_main(self):
        self.send_response(200)
        self.send_header('Connection', 'keep-alive')
        self.send_cache_header()
        self.send_header('Content-Type', 'text/html')
        self.send_cors_header()
        html = forwarder_html.encode('utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)

    def process_addr_invalid(self, addr):
        self.send_response(200)
        self.send_header('Connection', 'keep-alive')
        self.send_cache_header()
        self.send_header('Content-Type', 'text/html')
        self.send_cors_header()
        html = forwarder_html.replace('$jtc.phg.lfs.error$', f'Error: Server address {addr} is not valid!')
        html = html.encode('utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)

    def process_cannot_open(self, url):
        self.send_response(200)
        self.send_header('Connection', 'keep-alive')
        self.send_cache_header()
        self.send_header('Content-Type', 'text/html')
        self.send_cors_header()
        html = forwarder_html.replace('$jtc.phg.lfs.error$', f'Error: URL {url} can\'t be opened!')
        html = html.encode('utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)

    def send_cache_header(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT')

    def send_cors_header(self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Access-Control-Allow-Origin', '*')

    def log_message(self, *args) -> None:
        pass


class MyHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置套接字选项
        super().server_bind()


def start_forward_server(port: int) -> NoReturn:
    '''
    Start the local forward server to access a non-127.0.0.1 server in HTTP mode.
    
    For details, see https://github.com/jtc1246/py-html-graph   # TODO
    '''
    if (port <= 0 or port > 65535):
        raise ValueError('Invalid port number' + str(port))
    server = MyHTTPServer(('127.0.0.1', port), Request)
    start_new_thread(server.serve_forever, ())
    print(f'Server started,\nLink: https://127.0.0.1:{port}/')
    while True:
        sleep(10)

if (__name__ == '__main__'):
    start_forward_server(9011)
