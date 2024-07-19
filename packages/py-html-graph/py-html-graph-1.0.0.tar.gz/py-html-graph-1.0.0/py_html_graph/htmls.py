import os

base_path = os.path.abspath(__file__)
base_path = os.path.dirname(base_path)

with open(base_path+'/html/404.html') as f:
    html_404 = f.read()

with open(base_path+'/html/dash.html') as f:
    dashboard_html = f.read()

with open(base_path+'/html/forward.html') as f:
    forwarder_html = f.read()
