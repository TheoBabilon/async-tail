from pathlib import Path

from async_tail import atail, tail


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
