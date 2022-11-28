FROM python:slim
LABEL org.opencontainers.image.source=https://github.com/keithwissing/blueridge-exporter
LABEL description="Docker container to collect metrics from Blue Ridge internet"

RUN pip install --no-cache-dir pipenv

WORKDIR /app
COPY Pipfile* ./
RUN pipenv install --system --deploy

COPY src/. .

USER nobody:nogroup

ENTRYPOINT ["/usr/bin/env", "python", "exporter.py"]

HEALTHCHECK --timeout=10s CMD /usr/bin/env python healthcheck.py
