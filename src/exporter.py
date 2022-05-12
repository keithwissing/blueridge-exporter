import logging
import os

from flask import Flask
from prometheus_client import make_wsgi_app, Gauge, Info
from waitress import serve

from experiment import get_all_usage
from src.simplecache import timed_memory_cache

app = Flask('blueridge-exporter')

USE_DEBUG_SERVER = False

metrics = {
    'data_remaining': ('blueridge_data_remaining', 'Remaining data available this month in GB'),
    'data_used': ('blueridge_data_used', 'Data used this month in GB'),
    'limit': ('blueridge_data_limit', 'Monthly data usage limit in GB'),
    'used_down': ('blueridge_data_used_down', 'Downstream data used this month in GB'),
    'used_up': ('blueridge_data_used_up', 'Upstream data used this month in GB')
}

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
        g = Gauge(name, description)
        g.set(float(usage[k]))

    g = Gauge('blueridge_days_remaining', 'Days remiaing in this cycle')
    g.set(int(usage['monthly_cycle'].split()[0]))

    i = Info('blueridge_plan', 'Blueridge service information')
    i.info({k: v for k, v in usage.items() if k in ['mac', 'downstream', 'upstream']})

    return make_wsgi_app()

def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    port = os.getenv('EXPORTER_PORT', 9798)
    if USE_DEBUG_SERVER:
        app.run(port=port)
    else:
        # https://stackoverflow.com/a/54381386/125170 - use Waitress, a production WSGI server
        serve(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
