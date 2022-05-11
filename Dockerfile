FROM python:3.10.4-slim
LABEL org.opencontainers.image.source=https://github.com/keithwissing/blueridge-exporter
LABEL description="Docker container to collect metrics from Blue Ridge internet"

# wget used for healthcheck
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
    && apt install -y wget \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pipenv

WORKDIR /app
COPY Pipfile* ./

# Install required modules
RUN pipenv install --system --deploy

COPY src/. .

USER nobody:nogroup

CMD ["/usr/bin/env", "python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${EXPORTER_PORT:=1987}/
