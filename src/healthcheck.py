import os
import urllib
import urllib.request

def main():
    port = os.getenv('EXPORTER_PORT', 9798)
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/') as f:
        body = f.read(100).decode('utf-8')
    assert 'Blueridge-Exporter' in body
    assert 'Metrics' in body

if __name__ == "__main__":
    main()
