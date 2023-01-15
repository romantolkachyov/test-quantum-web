# Quantum Web Test Assigment

Project layout:

* `src/` — ract app sources
* `quantum_web/` — django app
* `quantum_web/worker` — async worker (consume redis queue for jobs, produce results to redis stream)
* `quantum_web/webapp` — backend api (rest `/api/start` and `/ws/`)
* `build` — frontend build files (in order to exclude building on the server; it is not a good idea in general)
* `public` — react app static
* `sdk_mock` — embed package

## Demo server

http://192.248.176.29:8000/

* Single worker
* Single VPS (1vCPU, 1Gb)
* Max concurrent jobs for a single worker: 2

## Getting started

```shell
docker compose up -d
```

Server (use pre-built react-app from `/build` instead of devserver):

```shell
docker-compose -f docker-compose.yml -f docker-compose.server.yml up -d
```
