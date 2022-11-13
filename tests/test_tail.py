from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from async_tail import atail, tail

if TYPE_CHECKING:
    from conftest import MockTailType


def test_tail_sync(tmp_file: Path, write_soon):
    write_soon(tmp_file)
    line = None
    for line in tail(tmp_file, debounce=50, step=10):
        break

    assert line == [('dummy', str(tmp_file))]


async def test_tail_async(tmp_file: Path, write_soon):
    write_soon(tmp_file)
    async for line in atail(tmp_file):
        assert line == ('dummy', str(tmp_file))
        break


def test_tail_timeout(mock_tail: 'MockTailType', caplog):
    mock = mock_tail([('dummy', 'dummy.log')], exit_code='timeout')

    caplog.set_level('DEBUG', 'async_tail')
    gen = iter(tail('.'))
    assert next(gen) == ('dummy', 'dummy.log')

    _ = next(gen)  # Will trigger exit_code timeout
    assert mock.tail_count == 1
    assert caplog.text == ("async_tail.main DEBUG: Rust notified timeout, continuing\n")  # noqa: Q000


def test_tail_yield_on_timeout(mock_tail: 'MockTailType'):
    mock = mock_tail([('dummy', 'dummy.log')], exit_code='timeout')

    row_list = []
    for lines in tail('.', yield_on_timeout=True):
        if lines == []:  # yields empty list
            break
        row_list.append(lines)

    assert row_list == [('dummy', 'dummy.log')]
    assert mock.tail_count == 1


def test_tail_raise_interrupt(mock_tail: 'MockTailType'):
    mock_tail([('dummy', 'dummy.log')], exit_code='signal')

    w = tail('.', raise_interrupt=True)
    assert next(w) == ('dummy', 'dummy.log')
    with pytest.raises(KeyboardInterrupt):
        next(w)


def test_tail_dont_raise_interrupt(mock_tail: 'MockTailType', caplog):
    caplog.set_level('WARNING', 'async_tail')
    mock_tail([('dummy', 'dummy.log')], exit_code='signal')

    w = tail('.', raise_interrupt=False)
    assert next(w) == ('dummy', 'dummy.log')
    with pytest.raises(StopIteration):
        next(w)

    assert caplog.text == 'async_tail.main WARNING: KeyboardInterrupt caught, stopping tail\n'
