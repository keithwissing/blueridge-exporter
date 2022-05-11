import datetime
import logging
import os

from flask import Flask
from prometheus_client import Gauge, make_wsgi_app
from waitress import serve

from experiment import get_all_usage

app = Flask("Blueridge-Exporter")  # Create flask app

# Create Metrics
data_remaining = Gauge('blueridge_data_remaining', 'Remaining data available this month in GB')
data_used = Gauge('blueridge_data_used', 'Data used this month in GB')
limit = Gauge('blueridge_data_limit', 'Monthy data usage limit in GB')
used_down = Gauge('blueridge_data_used_down', 'Downstream data used this month in GB')
used_up = Gauge('blueridge_data_used_up', 'Upstream data used this month in GB')

# Cache metrics for how long (seconds)?
cache_seconds = int(os.environ.get('SPEEDTEST_CACHE_FOR', 0))
cache_until = datetime.datetime.fromtimestamp(0)

def runTest():
    usage = get_all_usage()
    return {x[0]: x[1] for x in usage}

@app.route("/metrics")
def updateResults():
    global cache_until

    if datetime.datetime.now() > cache_until:
        usage = runTest()
        data_remaining.set(usage['data_remaining'])
        data_used.set(usage['data_used'])
        limit.set(usage['limit'])
        used_down.set(usage['used_down'])
        used_up.set(usage['used_up'])
        cache_until = datetime.datetime.now() + datetime.timedelta(seconds=cache_seconds)

    return make_wsgi_app()

@app.route("/")
def mainPage():
    return ("<h1>Welcome to Blueridge-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.")

def setup_logging():
    # Setup logging values
    format_string = 'level=%(levelname)s datetime=%(asctime)s %(message)s'
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG, format=format_string)

    # Disable Waitress Logs
    log = logging.getLogger('waitress')
    log.disabled = True

def main():
    setup_logging()
    PORT = os.getenv('EXPORTER_PORT', 9798)
    logging.info(f'Starting Blueridge-Exporter on http://localhost:{PORT}')
    serve(app, host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
