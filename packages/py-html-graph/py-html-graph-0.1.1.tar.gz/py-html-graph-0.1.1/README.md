# py-html-graph

## Introduction

This is a high-performance interactive numpy graph viewer, which is a good supplement for the awful and annoying matplotlib. Currently it supports multi-variable line chart. It can:

- Dynamically zoom and pan the graph, without the need to regenerate the image. With a much faster speed and higher resolution than matplotlib.

- Optimize for large amount of data. Have a good performance even with GBs of data.

- Smart cache and pre-fetching algorithm. Try best to avoid network latency.

- View directly in browser, low cost to learn and use.

## Usage

To use this tool, you need to have a python server and a browser.

#### Requirement

- Server: python>=3.9
- Browser: Chrome, Edge, Opera (can't use Safari or Firefox) (recommend Chrome and Opera)
- Device: have touchpad or mouse, can't work with touch screen (recommend touchpad)

#### Installation

```bash
pip install py-html-graph
```

#### Actual Usage

First you need to add your graph (numpy array) in the python code. You can refer to [example.py](example.py). Generally there are following steps:

1. Import: `from py_html_graph import GraphServer`
2. Create the server: `server = GraphServer(http_port, https_port)`
3. Start the server: `server.start()`
4. Add graph: `server.add_graph('mygraph', data, 'row')` (data is a numpy array)
5. Block the main thread: `server.wait_forever()`

Then you can open the link in the browser. And you will be able to see the dashboard and view the graph.

But there are some notes you need to pay attention to:

1. Don't use Safari or Firefox.
2. If you use non-local IP (other than 127.0.0.1, localhost) or HTTPS, please see the next section.

## About non-local IP and HTTPS

If using HTTP, this website can only be opened on the same device (127.0.0.1 or localhost) as the server. This is because I need to use sharedArrayBuffer, which requires Cross-Origin-Opener-Policy header (or the browser will not recognize sharedArrayBuffer). But if you open through http and not from 127.0.0.1 or localhost, the browser will disallow the header of Cross-Origin-Opener-Policy, so this website can't be opened. And in HTTPS page, we can't send HTTP requests.

So if you want to visit on different device, you must use HTTPS. But there is a problem in HTTPS, it needs to handle the encryption of data, which will affecting the speed of requests (because this website will send a lot of data). To solve this, you have following options:

1. Use on the same device (127.0.0.1 or localhost). (Disadvantage: can't use on different device)
2. Just use HTTPS. (Disadvantage: slow speed)
3. Use a forwarding server on the same device with browser, so that the brower will "think" it is communicating with 127.0.0.1. (Disadvantage: complex to set up) (`start_forward_server` function)
4. Add `--allow-running-insecure-content` in the browser start command, so that can send http requests in https page. (Disadvantage: complex to set up, limited to desktop) (see last section)

## Python functions

#### `class GraphServer`: the class of the server. A server can contain several graphs.
```python
def __init__(this, http_port:int = None, https_port:int = None):
    '''
    Create a server to show graphs in the browser.
    Serve HTTP in http_port, serve HTTPS in https_port.
    You must provide at least one of them.
    '''
```

```python
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
```

```python
def start(this) -> None:
    '''
    Start the server asynchronizely.
    '''
```

```python
def wait_forever(this) -> NoReturn:
    '''
    Just to block the main thread.
    '''
```

#### Other functions

1. Start the forwarding server: 
```python
def start_forward_server(port: int) -> NoReturn:
    '''
    Start the local forward server to access a non-127.0.0.1 server in HTTP mode.
    For details, see https://github.com/jtc1246/py-html-graph   # TODO
    '''
```

2. Color tools: `generate_colors`, `plot_colors`
```python
def generate_colors(num: int, trial: int = 10, fixed=False) -> list[str]:
    '''
    Generate the colors of num variables, each of them as different as possible
    Colors are put in RGB 3D space, will try to make the straight-line distance between each two of them as large as possible
    Will return a list of str, each str is a color in hex format (#rrggbb), can be passed in to add_graph directly
    
    Parameters:
    
    1. num: the number of variables
    2. trail: will try to generate trail times, and find the best one
    3. fixed: if True, the result will become deterministic
    '''
```

```python
def plot_colors(hex_colors:list[str]) -> None:
    """
    Plot the generated colors. hex_colors is a list of hex str, in #rrggbb format
    """
```

## Start the browser with `--allow-running-insecure-content`

This part will only talk about Chrome and Opera, beacuse Edge can't bypass the invalid SSL certificate problem.

|   | Chrome | Opera |
| --- | --- | --- |
| macOS | `open -n -a "Google Chrome" --args --allow-running-insecure-content --user-data-dir="/tmp/chrome_dev_session"` | `open -n -a "Opera" --args --allow-running-insecure-content --user-data-dir="/tmp/opera_dev_session"` |
| Windows | `"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --allow-running-insecure-content --user-data-dir="%TEMP%\chrome_dev_session"` | `"C:\Program Files\Opera\launcher.exe" --allow-running-insecure-content --user-data-dir="%TEMP%\opera_dev_session"` |
| Linux | `google-chrome --allow-running-insecure-content --user-data-dir="/tmp/chrome_dev_session"` | `opera --allow-running-insecure-content --user-data-dir="/tmp/opera_dev_session"` |

## Performance

Environment: macOS, M1, Chrome, launch with --allow-running-insecure-content, use HTTP in data requests. Browser and server on different devices, in LAN, one side WiFi, one side Ethernet. Use [example.py](example.py).

#### 1. Test directly

<img src="resources/demo.gif" width="100%">

#### 2. Manually 30 ms delay to the above environment

Add `sleep(0.03)` in the server code for handling data HTTP requests.

<img src="resources/demo_30ms.gif" width="100%">
