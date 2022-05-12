import http.cookiejar
import json
import logging
import re

import mechanize
from bs4 import BeautifulSoup
from get_docker_secret import get_docker_secret

def get_configuration() -> dict[str, str]:
    uname = get_docker_secret('blueridge_username')
    if not uname:
        return {}
    passwd = get_docker_secret('blueridge_password')
    influx_host = get_docker_secret('influx_host')
    influx_db = get_docker_secret('influx_db')
    return {'uname': uname, 'passwd': passwd, 'influx_host': influx_host, 'influx_db': influx_db}

def get_first_page(br, username: str, password: str):
    br.open("https://www.brctv.com/login")

    br.select_form(nr=0)
    br.form['username'] = username
    br.form['password'] = password
    br.submit()

    html = br.response().read()
    return html

def find_uid(html):
    soup = BeautifulSoup(html, 'html.parser')

    ajax_divs = soup.find_all('div', class_='mbr-ajax-loader')

    uid = None
    prefix = '/ajax/services/usage/brief/'
    for div in ajax_divs:
        link = div['data-ajax-content']
        if link.startswith(prefix):
            uid = link[len(prefix):]
    return uid

def get_usage_data(br, uid):
    usage = f'https://www.brctv.com/ajax/services/usage/full/{uid}'
    br.open(usage)
    json_data = br.response().read()
    return json_data

def find_usage_data(json_data):
    ct = json.loads(json_data)
    soup = BeautifulSoup(ct['content'], 'html.parser')
    labels = soup.find_all('div', class_='label')
    values = soup.find_all('div', class_='value')
    labels = [x.get_text().strip().strip(':').lower().replace(' ', '_') for x in labels]
    values = [x.get_text().strip() for x in values]
    things = list(zip(labels, values))
    logging.debug(f'Usage: {things}')
    return things

def get_internet_usage(br):
    url = 'https://www.brctv.com/my/services/internet-usage'
    br.open(url)
    html = br.response().read()
    return html

def parse_usage_string(usage_str):
    m = re.match(
        r'CABLE MODEM Up to (.+) Download/(.+) Upload MAC: (.+) You have used (.+): (.+) upload & (.+) download. Your limit is (.+). You have (.+) remaining.',
        usage_str)
    if not m:
        logging.error('Usage String did not match expected format:')
        logging.error(usage_str)
    labels = ['downstream', 'upstream', 'mac', 'used', 'used_up', 'used_down', 'limit', 'remaining']
    usage = list(zip(labels, m.groups()))
    logging.debug(f'Usage: {usage}')
    return usage

def find_another_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    intro = soup.find_all(id='data-usage-intro')
    intro = intro[0].get_text()
    intro = ' '.join(intro.split())
    return parse_usage_string(intro)

def to_gb(s):
    parts = s.split()
    if len(parts) == 2:
        if parts[1] == 'TB':
            return float(parts[0]) * 1000
        if parts[1] == 'GB':
            return float(parts[0])
        if parts[1] == 'MB':
            return float(parts[0]) / 1000
        if parts[1] == 'KB':
            return float(parts[0]) / 1000 / 1000
    return s

def experiment(username: str, password: str):
    cj = http.cookiejar.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)

    html = get_first_page(br, username, password)
    uid = find_uid(html)

    json_data = get_usage_data(br, uid)
    things = find_usage_data(json_data)

    html = get_internet_usage(br)
    usage = find_another_data(html)

    both = sorted(things + usage)
    return list(map(lambda x: (x[0], to_gb(x[1])), both))

def get_all_usage():
    config = get_configuration()
    things = experiment(config['uname'], config['passwd'])
    logging.info(f'All Usage: {things}')
    return things

def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    get_all_usage()

if __name__ == "__main__":
    main()
