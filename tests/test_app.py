import logging
import multiprocessing
import time
from typing import Generator

import celery
import pytest
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="module")
def valkey_uri() -> Generator[str, None, None]:
    print("Starting Valkey container")
    valkey_container = DockerContainer("valkey/valkey:latest")
    valkey_container.with_exposed_ports(6379)
    valkey_container.start()

    valkey_port = valkey_container.get_exposed_port(6379)
    ip = valkey_container.get_container_host_ip()
    valkey_uri = f"valkey://{ip}:{valkey_port}/0"
    print(f"Valkey URI: {valkey_uri}")
    yield valkey_uri

    valkey_container.stop()


@pytest.fixture(scope="module")
def redis_uri() -> Generator[str, None, None]:
    print("Starting Redis container")
    redis_container = DockerContainer("redis:6.2.6")
    redis_container.with_exposed_ports(6379)
    redis_container.start()

    redis_port = redis_container.get_exposed_port(6379)
    ip = redis_container.get_container_host_ip()

    redis_uri = f"redis://{ip}:{redis_port}/0"
    print(f"Redis URI: {redis_uri}")
    yield redis_uri

    redis_container.stop()


def create_celery_app(redis_uri: str, valkey_uri: str) -> celery.Celery:
    """Create a Celery application with the given broker and backend URIs."""
    app = celery.Celery("test_app", broker=redis_uri, backend=valkey_uri)
    app.conf.broker_connection_retry = True

    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        task_always_eager=False,  # Important: Don't run tasks eagerly
        worker_prefetch_multiplier=1,
    )

    @app.task
    def add(x: int, y: int) -> int:
        return x + y

    @app.task
    def mul(x: int, y: int) -> int:
        return x * y

    return app


def run_worker(app) -> None:
    """Run the Celery worker process."""
    worker = app.Worker(loglevel="INFO", concurrency=1, pool="solo")
    worker.start()


@pytest.fixture(scope="module")
def celery_worker_and_app(
    redis_uri: str, valkey_uri: str
) -> Generator[celery.Celery, None, None]:
    """Start Celery worker in a separate process and return the Celery app."""
    # Create and configure the Celery app
    app = create_celery_app(redis_uri, valkey_uri)

    # Start the worker in a separate process
    worker_process = multiprocessing.Process(target=run_worker, args=(app,))
    worker_process.start()

    # Wait for worker to initialize
    time.sleep(5)  # Give worker time to start

    yield app

    # Cleanup
    worker_process.terminate()
    worker_process.join(timeout=5)
    if worker_process.is_alive():
        worker_process.kill()


def test_add(celery_worker_and_app: celery.Celery) -> None:
    """Test the add task."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Send task
    logger.info("Sending add task")
    result = celery_worker_and_app.send_task("tests.test_app.add", args=[1, 100])

    # Wait for result
    task_result = result.get(timeout=10)
    logger.info(f"Got result: {task_result}")

    # Assert result
    assert task_result == 101


def test_mul(celery_worker_and_app: celery.Celery) -> None:
    """Test the mul task."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Send task
    logger.info("Sending mul task")
    result = celery_worker_and_app.send_task("tests.test_app.mul", args=[2, 3])

    # Wait for result
    task_result = result.get(timeout=10)
    logger.info(f"Got result: {task_result}")

    # Assert result
    assert task_result == 6
