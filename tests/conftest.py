from pathlib import Path
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Any, List, Tuple

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


AddedRows = List[Tuple[str, str]]


class MockTail:
    def __init__(self, rows: AddedRows, exit_code: str):
        self.rows = rows
        self.iter_changes = iter(rows)
        self.exit_code = exit_code
        self.tail_count = 0
        self.done = False

    def read_line(self, debounce_ms: int, step_ms: int, timeout_ms: int):
        try:
            line = next(self.iter_changes)
        except StopIteration:
            # TODO: implement proper stop logic
            if self.done:
                return self.rows[0]
            self.done = True
            return self.exit_code
        else:
            self.tail_count += 1
            return line

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        pass


if TYPE_CHECKING:
    from typing import Literal, Protocol

    class MockTailType(Protocol):
        def __call__(self, rows: AddedRows, *, exit_code: Literal['signal', 'timeout'] = 'timeout') -> Any:
            ...


@pytest.fixture
def mock_tail(mocker):
    def mock(rows: AddedRows, *, exit_code: str = 'timeout'):
        m = MockTail(rows, exit_code)
        mocker.patch('async_tail.main.Tail', return_value=m)
        return m

    return mock
