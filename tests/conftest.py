from pathlib import Path
from threading import Thread
from time import sleep

import pytest


@pytest.fixture(autouse=True)
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    """
    Create a temporary file
    """
    return tmp_path / 'dummy.txt'


def sleep_write(path: Path):
    sleep(0.1)
    path.write_text('dummy')


@pytest.fixture
def write_soon():
    threads = []

    def start(path: Path):
        thread = Thread(target=sleep_write, args=(path,))
        thread.start()
        threads.append(thread)

    yield start

    for t in threads:
        t.join()
