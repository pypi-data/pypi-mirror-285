import numpy as np
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from _thread import start_new_thread
from time import sleep
from mySecrets import hexToStr, toHex
import json
from math import floor
from myBasics import binToBase64
import ssl
from mySecrets import hexToStr, toHex
from myBasics import strToBase64, base64ToStr
from html import escape as html_escape
from typing import Literal, Union, NoReturn
from .colors import generate_colors, STD_COLORS
from .htmls import html_404, dashboard_html
from time import time
import os


__all__ = ['GraphServer']

_base_path = os.path.abspath(__file__)
_base_path = os.path.dirname(_base_path)


def escape_html(s: str) -> str:
    s = html_escape(s)
    return s.replace('\n', ' ').replace(' ', '&nbsp;')


BASE64_HEADER = 'data:application/javascript;base64,'


def generate_html(base_path: str,
                  graph_title: str = 'The title of graph',
                  x_title: str = 'The description of X',
                  y_title: str = 'The description of Y',
                  x_start_ms: int = 0,
                  x_step_ms: int = 1000,
                  data_point_num: int = None,  # required
                  variable_num: int = None,  # required
                  variable_names: list[str] = None,  # generate automatically if it's None
                  label_colors: list[str] = None,  # generate automatically if it's None
                  data_server_url: str = None,  # required
                  max_whole_level_cache_size: int = 0,
                  http_port: int = None) -> str:
    if (not base_path.endswith('/')):
        base_path += '/'
    with open(base_path + 'main.html', 'r') as f:
        html = f.read()
        html = html.replace("$jtc.py-html-graph.graph-title$", escape_html(graph_title)) \
                   .replace("$jtc.py-html-graph.x-title$", escape_html(x_title)) \
                   .replace("$jtc.py-html-graph.y-title$", escape_html(y_title))
    with open(base_path + 'chart.js', 'r') as f:
        chartjs = f.read()
    variable_names_tmp = list(variable_names)
    for i in range(0, len(variable_names)):
        variable_names_tmp[i] = escape_html(variable_names[i])
    with open(base_path + 'main.js', 'r') as f:
        js = f.read()
        js = js.replace("'$jtc.py-html-graph.data-point-num$'", str(data_point_num)) \
               .replace("'$jtc.py-html-graph.variable-num$'", str(variable_num)) \
               .replace("'$jtc.py-html-graph.variable-names$'", str(variable_names_tmp)) \
               .replace("'$jtc.py-html-graph.label-colors$'", str(label_colors)) \
               .replace("'$jtc.py-html-graph.data-server-base-url$'", f'"{data_server_url}"')
        if(http_port != None):
            js = js.replace("'$jtc.py-html-graph.http-port-in-https$'", f"'{str(http_port)}'")
    with open(base_path + 'reset.css', 'r') as f:
        reset = f.read()
    with open(base_path + 'main.css', 'r') as f:
        css = f.read()
    with open(base_path + 'style.js', 'r') as f:
        stylejs = f.read()
    with open(base_path + 'axis.js', 'r') as f:
        axisjs = f.read()
        axisjs = axisjs.replace("'$jtc.py-html-graph.x-start-ms$'", str(x_start_ms)) \
                       .replace("'$jtc.py-html-graph.x-step-ms$'", str(x_step_ms))
    with open(base_path + 'cache_worker.js', 'r') as f:
        worker = f.read()
        worker = worker.replace("'$jtc.py-html-graph.max-whole-level-cache-size$'", str(max_whole_level_cache_size))
    with open(base_path + 'http.js', 'r') as f:
        httpjs = f.read()
    httpjs = strToBase64(httpjs)
    worker = worker.replace("'$jtc.py-html-graph.inside.httpjs$'", f"'{httpjs}'")
    worker = strToBase64(worker)
    js = js.replace("'$jtc.py-html-graph.inside.cacheworkerbase64$'", f"'{worker}'")
    html = html.replace('<script src="chart.js"></script>', f'<script>{chartjs}</script>')
    html = html.replace('<script src="main.js"></script>', f'<script src="{BASE64_HEADER+strToBase64(js)}"></script>')
    html = html.replace('<link rel="stylesheet" href="reset.css">', f'<style>{reset}</style>')
    html = html.replace('<link rel="stylesheet" href="main.css">', f'<style>{css}</style>')
    html = html.replace('<script src="style.js"></script>', f'<script src="{BASE64_HEADER+strToBase64(stylejs)}"></script>')
    html = html.replace('<script src="axis.js"></script>', f'<script src="{BASE64_HEADER+strToBase64(axisjs)}"></script>')
    return html


class GraphServer:
    '''
    The server to show graphs in the browser.
    
    Methods:
    
    1. add_graph: add a graph to the server.
    2. start: start the server asynchronizely.
    3. wait_forever: block the main thread.
    
    Example:
    
    ```
    server = GraphServer(8080, 4443)
    server.start()
    
    array_1 = np.zeros((10, 1000000), dtype=np.float32)
    server.add_graph('my_graph_1', array_1, 'column')
    
    array_2 = np.zeros((1000000, 10), dtype=np.float32)
    server.add_graph('my_graph_2', array_2, 'row')
    
    server.wait_forever()
    
    ```
    Then open the link in the browser, you can see the graphs.
    '''
    def __init__(this, http_port:int = None, https_port:int = None):
        '''
        Create a server to show graphs in the browser.
        
        Serve HTTP in http_port, serve HTTPS in https_port.
        
        You must provide at least one of them.
        '''
        if(http_port == None and https_port == None):
            raise TypeError("You must provide at least one of http_port and https_port.")
        if(http_port != None and type(http_port) != int):
            raise TypeError("http_port must be int.")
        if(https_port != None and type(https_port) != int):
            raise TypeError("https_port must be int.")
        if(http_port == https_port):
            raise ValueError("http_port and https_port can't be the same.")
        this.http_port = http_port
        this.https_port = https_port
        this.configs = {}

        class Request(BaseHTTPRequestHandler):
            def do_GET(self):
                path_segments = self.path.split('/')[1:]
                if (path_segments[-1] == ''):
                    path_segments = path_segments[:-1]
                if(len(path_segments) == 0 or (path_segments[0] in ('index.html', 'dashboard.html', 'dashboard') and len(path_segments) == 1)):
                    # print('dashboard')
                    self.process_dashboard()
                    return
                graph_name = path_segments[0]
                if(graph_name not in this.configs):
                    # print(404)
                    self.process_404()
                    return
                if (len(path_segments) == 1):
                    # print('html')
                    self.process_html(graph_name)
                    return
                if (len(path_segments) == 2 and path_segments[1] == 'minmax'):
                    # print('minmax')
                    self.process_minmax(graph_name)
                    return
                if (len(path_segments) == 2):
                    self.process_one_request(path_segments[1], graph_name)
                    return
                if (len(path_segments) == 3 and path_segments[1] == 'batch'):
                    # print('batch request')
                    self.process_batch(path_segments[2], graph_name)
                    return
                # print(404)
                # print(self.path)
                self.process_404()
                return
            
            def process_dashboard(self):
                format = '<p>$jtc.phg.dash-id$. <a class="$jtc.phg.proxy-replacer$" href="/$jtc.phg.dash-name$">$jtc.phg.dash-name$</a>: $jtc.phg.dash-desc$</p>\n'
                content = ''
                if(len(this.configs) == 0):
                    content = '<p style="color:red;">No graphs added now.</p>'
                cnt = 1
                for name in this.configs:
                    title = this.configs[name]['title']
                    content += format.replace('$jtc.phg.dash-id$', str(cnt)) \
                                     .replace('$jtc.phg.dash-name$', escape_html(name)) \
                                     .replace('$jtc.phg.dash-desc$', escape_html(title))
                    cnt += 1
                html = dashboard_html.replace('<p>0. <a href="/example" class="$jtc.py-html-graph.dashboard-items-replacer$">example</a>: this is an example</p>', content)
                html = html.encode('utf-8')
                self.send_response(200)
                self.send_cache_header()
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Connection', 'keep-alive')
                self.send_cors_header()
                self.send_header('Content-Length', len(html))
                self.end_headers()
                self.wfile.write(html)
                return

            def process_html(self, name):
                self.send_response(200)
                self.send_cache_header()
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Connection', 'keep-alive')
                self.send_cors_header()
                domain = self.headers['Host']
                data_server_url = f'/{name}'
                html = generate_html(_base_path+'/html',
                                    data_point_num=this.configs[name]['data_point_num'],
                                    variable_num=this.configs[name]['variable_num'],
                                    variable_names=this.configs[name]['names'],
                                    label_colors=this.configs[name]['colors'],
                                    data_server_url=data_server_url,
                                    graph_title=this.configs[name]['title'],
                                    x_title=this.configs[name]['x_title'],
                                    y_title=this.configs[name]['y_title'],
                                    x_start_ms=this.configs[name]['x_start_ms'],
                                    x_step_ms=this.configs[name]['x_step_ms'],
                                    max_whole_level_cache_size=this.configs[name]['max_whole_level_cache_size'],
                                    http_port=this.http_port)
                html = html.encode('utf-8')
                self.send_header('Content-Length', len(html))
                self.end_headers()
                self.wfile.write(html)

            def process_minmax(self, name):
                a = this.configs[name]['array_min'].byteswap().tobytes()
                b = this.configs[name]['array_max'].byteswap().tobytes()
                data = binToBase64(a + b)
                self.send_response(200)
                self.send_header('Content-Length', len(data))
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
                return

            def process_one_request(self, data: str, name):
                array = this.configs[name]['array']
                data_point_num = this.configs[name]['data_point_num']
                json_data = json.loads(hexToStr(data))
                # print('single-request: ', end='')
                # print(json_data)
                start = json_data['start']
                end = json_data['end']
                step = json_data['step']
                transpose = 'tr' in json_data
                selected = []
                for i in range(start, end, step):
                    selected.append(i)
                if (selected[0] < 0):
                    selected[0] = 0
                if (selected[-1] > data_point_num - 1):
                    selected[-1] = data_point_num - 1
                array_ = array[:, selected]
                if (transpose):
                    array_ = array_.T
                data = array_.byteswap().tobytes()
                # data = binToBase64(data)
                self.send_response(200)
                self.send_header('Content-Length', len(data))
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
                return
            
            def process_batch(self, data: str, name):
                array = this.configs[name]['array']
                data_point_num = this.configs[name]['data_point_num']
                json_data = json.loads(hexToStr(data))
                results = []
                lengths = []
                total_length = 0
                for a in json_data:
                    current_request = json.loads(hexToStr(a))
                    start = current_request['start']
                    end = current_request['end']
                    step = current_request['step']
                    selected = []
                    for i in range(start, end, step):
                        selected.append(i)
                    if (selected[0] < 0):
                        selected[0] = 0
                    if (selected[-1] > data_point_num - 1):
                        selected[-1] = data_point_num - 1
                    array_ = array[:, selected]
                    data = array_.T.byteswap().tobytes()
                    results.append(data)
                    lengths.append(len(data))
                    total_length += len(data)
                data = b''.join(results)
                length_header = toHex(json.dumps(lengths))
                self.send_response(200)
                self.send_header('Content-Length', total_length)
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Parts-Length', length_header)
                self.send_header('Access-Control-Expose-Headers', 'Parts-Length')
                self.end_headers()
                self.wfile.write(data)
                return

            def send_cache_header(self):
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT')

            def send_cors_header(self):
                self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                self.send_header('Access-Control-Allow-Origin', '*')

            def process_404(self):
                self.send_response(404)
                self.send_cache_header()
                self.send_header('Content-Length', len(html_404.encode('utf-8')))
                self.send_header('Connection', 'keep-alive')
                self.send_cors_header()
                self.end_headers()
                self.wfile.write(html_404.encode('utf-8'))
                return

            def do_POST(self):
                # print('POST 404')
                self.process_404()
                return

            def log_message(self, *args) -> None:
                pass
            
        this.RequestClass = Request
    
    def add_graph(this, 
                  name: str, array: np.ndarray, direction: Literal['row', 'column'] = 'row',
                  title: str = 'The title of graph',
                  x_start_ms: int = 0,
                  x_step_ms: int = 1000,
                  x_title: str = 'The description of X',
                  y_title: str = 'The description of Y',
                  label_colors: Union[list[str], Literal['STD', 'GENRERATE']] = 'STD',
                  label_names: list[str] = None) -> None:
        '''
        Add a graph to the server.
        
        Parameters:
        
        1. name: the name displayed in the dashboard, two graphs can't have the same name. Can only contain characters in 0-9,a-z,A-Z and !*'();:@&=+$,/[]-_=~.
        2. array: the data of the graph, in numpy, must in np.float32.
        3. direction: 'row' or 'column'. 'row' means each row is the data at one time point, 'column' means each column is the data at one time point. <br>
        For example, I have 10 variables and 50000 data points, if the shape is (50000, 10), it's 'row', if the shape is (10, 50000), it's 'column'.
        4. title: the title of the graph.
        5. x_start_ms: the time of the first data point, in milliseconds.
        6. x_step_ms: the time interval between two data points, in milliseconds.
        7. x_title: the description of X.
        8. y_title: the description of Y.
        9. label_colors: the colors of the lines, can be 'STD', 'GENRERATE' or a list of colors (str, in #rrggbb).<br>
        If 'STD', it will use the pre-generated colors. If 'GENRERATE', it will generate colors automatically. <br>
        10. label_names: the names of the variables, if not provided, it will be generated automatically.
        '''
        if(array.dtype != np.float32):
            raise TypeError("Array must in np.float32.")
        if(name in this.configs):
            raise ValueError(f"Graph {name} already exists.")
        if(name == ''):
            raise TypeError("Graph name can't be empty.")
        allowed_characters = "!*'();:@&=+$,/[]-_=~."
        allowed_characters += '0123456789'
        allowed_characters += 'abcdefghijklmnopqrstuvwxyz'
        allowed_characters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for c in name:
            if(c not in allowed_characters):
                raise ValueError(f"Invalid character '{c}' in graph name. Graph name can only contain characters in 0-9,a-z,A-Z and !*'();:@&=+$,/[]-_=~.")
        config = {}
        config['array_min'] = np.min(array)
        config['array_max'] = np.max(array)
        if(direction not in ('row', 'column')):
            raise TypeError("direction can only be 'row' or 'column'.")
        if(direction == 'row'):
            config['variable_num'] = array.shape[1]
            config['data_point_num'] = array.shape[0]
            config['array'] = array.T
        else:
            config['variable_num'] = array.shape[0]
            config['data_point_num'] = array.shape[1]
            config['array'] = array
        if(label_names == None):
            label_names = [f'Name {i}' for i in range(1, config['variable_num'] + 1)]
        if(len(label_names) != config['variable_num']):
            raise ValueError(f"There are {config['variable_num']} variables, but {len(label_names)} label names provided.")
        if (label_colors not in ('STD', 'GENRERATE') and type(label_colors) != list):
            raise TypeError("label_colors can only be 'STD', 'GENRERATE' or a list of colors (str, #rrggbb).")
        if(label_colors == 'STD' and config['variable_num'] > len(STD_COLORS)):
            label_colors = 'GENRERATE'
        if(label_colors == 'STD'):
            label_colors = STD_COLORS[config['variable_num']]
        if(label_colors == 'GENRERATE'):
            label_colors = generate_colors(config['variable_num'], 3)
        if(len(label_colors) != config['variable_num']):
            raise ValueError(f"There are {config['variable_num']} variables, but {len(label_colors)} colors provided.")
        config['names'] = label_names
        config['colors'] = label_colors
        config['title'] = title
        config['x_title'] = x_title
        config['y_title'] = y_title
        config['x_start_ms'] = x_start_ms
        config['x_step_ms'] = x_step_ms
        config['max_whole_level_cache_size'] = 0
        this.configs[name] = config
    
    
    def start(this) -> None:
        '''
        Start the server asynchronizely.
        '''
        this.http_server = None
        this.https_server = None
        if (this.http_port != None):
            this.http_server = ThreadingHTTPServer(('0.0.0.0', this.http_port), this.RequestClass)
            start_new_thread(this.http_server.serve_forever, ())
        if (this.https_port != None):
            this.https_server = ThreadingHTTPServer(('0.0.0.0', this.https_port), this.RequestClass)
            this.https_server.socket = ssl.wrap_socket(this.https_server.socket, certfile=_base_path+'/ssl/certificate.crt', keyfile=_base_path+'/ssl/private.key', server_side=True)
            start_new_thread(this.https_server.serve_forever, ())
        print('Server started, ')
        print(f'HTTP link:  http://127.0.0.1:{this.http_port}')
        print(f'HTTPS link: https://<ip>:{this.https_port}')
    
    def wait_forever(this) -> NoReturn:
        '''
        Just to block the main thread.
        '''
        while True:
            sleep(10)

if __name__ == '__main__':
    with open('../data/10_50m.bin', 'rb') as f:
        data_10_50m = f.read()
    array_10_50m = np.frombuffer(data_10_50m, dtype=np.float32).reshape((10, 50000000)).byteswap()
    del data_10_50m

    server = GraphServer(9010, 9012)
    server.start()
    server.add_graph('jtc', array_10_50m, 'column', 
                     x_start_ms=int(time()*1000), x_step_ms=200, 
                     x_title='Time', y_title='Price', title='Price comparison',
                     label_colors='STD', label_names=['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'DOT', 'UNI', 'SOL', 'LTC'])
    server.add_graph('mygraph', array_10_50m[0:6,0:20000000], 'column')
    server.add_graph('tmp', array_10_50m[0:6,0:20000000].T, 'row')
    server.add_graph('test4', np.zeros((100,10000), dtype=np.float32), 'column')
    server.wait_forever()
