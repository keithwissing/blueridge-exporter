import argparse
import logging
import os
from tempfile import NamedTemporaryFile

from flask import Flask
from prometheus_client import make_wsgi_app, Gauge, Info, REGISTRY, write_to_textfile
from waitress import serve

from experiment import get_all_usage
from simplecache import timed_memory_cache

app = Flask('blueridge-exporter')

USE_DEBUG_SERVER = False

metrics = {
    'data_remaining': ('blueridge_data_remaining', 'Remaining data available this month in GB'),
    'data_used': ('blueridge_data_used', 'Data used this month in GB'),
    'limit': ('blueridge_data_limit', 'Monthly data usage limit in GB'),
    'used_down': ('blueridge_data_used_down', 'Downstream data used this month in GB'),
    'used_up': ('blueridge_data_used_up', 'Upstream data used this month in GB')
}

gauges = {}

def get_gauge(name, description):
    if name not in gauges:
        gauges[name] = Gauge(name, description)
    return gauges[name]

def get_info(name, description):
    if not get_info.info:
        get_info.info = Info(name, description)
    return get_info.info

get_info.info = None

@timed_memory_cache(seconds=int(os.getenv('EXPORTER_CACHE_TIMEOUT', '300')))
def get_metrics():
    return get_all_usage()

@app.route('/')
def hello_world():
    return '<h1>Blueridge-Exporter</h1><a href="metrics">Metrics</a>'

@app.route('/metrics')
def hello_metrics():
    usage = get_metrics()
    usage = {k: v for k, v in usage}

    for k in metrics.keys():
        name, description = metrics[k]
        g = get_gauge(name, description)
        g.set(float(usage[k]))

    g = get_gauge('blueridge_days_remaining', 'Days remaining in this cycle')
    g.set(int(usage['monthly_cycle'].split()[0]))

    i = get_info('blueridge_plan', 'Blueridge service information')
    i.info({k: v for k, v in usage.items() if k in ['mac', 'downstream', 'upstream']})

    return make_wsgi_app()

def write_metrics_to_stdout():
    with NamedTemporaryFile() as file:
        write_to_textfile(file.name, REGISTRY)
        with open(file.name, 'r') as f:
            print(f.read())
        print(file.name)

def main():
    parser = argparse.ArgumentParser(description='Blueridge Cable Usage Exporter')
    parser.add_argument('--test', action='store_true', dest='test', help='Pull data once, output to stdout, and exit')
    args = parser.parse_args()

    if args.test:
        hello_metrics()
        write_metrics_to_stdout()
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
        port = os.getenv('EXPORTER_PORT', 1987)
        if USE_DEBUG_SERVER:
            app.run(port=port)
        else:
            # https://stackoverflow.com/a/54381386/125170 - use Waitress, a production WSGI server
            serve(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
