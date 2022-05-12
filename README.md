# blueridge-exporter

A Prometheus exporter for Blueridge Cable internet data usage

This exporter will log into https://www.brctv.com/login and pull your data usage information.

Blueridge does not update this information very often, so there is no reason to pull it more than every hour or two.
Less often is of course also an option.

This exporter works with the version of the Blueridge website as of May 2022.

---

Available environment variables:

| variable               | default | description                  |
|------------------------|---------|------------------------------|
| EXPORTER_PORT          | 1987    | listening port number        |
| EXPORTER_CACHE_TIMEOUT | 300     | time in seconds to keep data |

## To deploy via docker-compose:

* copy .env.example to .env
    * `cp .env.example .env`
* edit .env to set your username and password
    * `vim .env`
* deploy
    * `docker-compose up -d`

## Deploy to a swarm as a stack:

```commandline
$ printf "heather" | docker secret create blueridge_username -
$ printf "my_secure_password" | docker secret create blueridge_password -

$ docker stack deploy -c docker-stack.yml blueridge-exporter
```

## Sample prometheus configuration:

``` yaml
- job_name: 'blueridge-exporter'
  scrape_interval: 1h
  scrape_timeout: 1m
  static_configs:
  - targets: ['<YOUR_IP_ADDRESS>:<YOUR_EXPORTER_PORT>']
```
