import logging
import time

import celery
import pytest

from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="module")
def valkey_uri():
    print("Starting Valkey container")
    with DockerContainer('valkey/valkey:8.0.1') as valkey_container:
        valkey_container.with_exposed_ports(6379)
        valkey_port = valkey_container.get_exposed_port(6379)
        ip = valkey_container.get_container_host_ip()
        valkey_uri = f"valkey://{ip}:{valkey_port}/0"
        print(valkey_uri)
        yield valkey_uri


@pytest.fixture(scope="module")
def redis_uri():
    # Start a redis container
    print("Starting Redis container")
    with DockerContainer("redis:6.2.6") as redis_container:
        redis_container.with_exposed_ports(6379)
        redis_port = redis_container.get_exposed_port(6379)
        ip = redis_container.get_container_host_ip()

        redis_uri = "redis://{}:{}/0".format(ip, redis_port)
        print(redis_uri)

        yield redis_uri


@pytest.fixture(scope="module")
def celery_app(redis_uri, valkey_uri):
    app = celery.Celery('main', broker=redis_uri, backend=valkey_uri)
    app.conf.broker_connection_retry_on_startup = True
    app.conf.timezone = "UTC"
    app.conf.task_always_eager = True

    @app.task
    def add(x, y):
        return x + y


    @app.task
    def mul(x, y):
        return x * y

    yield app


def test_add(celery_app):
    logging.basicConfig(level=logging.DEBUG)
    s = celery_app.send_task("main.add", args=[1, 100])
    time.sleep(10)
    assert s.get(timeout=10) == 101
