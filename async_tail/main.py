import logging
from pathlib import Path
from typing import AsyncGenerator, Generator, List, Tuple, Union

from ._async_tail import AIOTail, Tail

__all__ = 'tail', 'atail', 'AddedLine'
logger = logging.getLogger('async_tail.main')


AddedLine = Tuple[str, str]
"""
A tuple representing a line added to monitored files, first element is a the newly-added line, second is the path
of the file that changed.
"""


def tail(
    *paths: Union[Path, str],
    debounce: int = 1_600,
    step: int = 50,
    rust_timeout: int = 5_000,
    yield_on_timeout: bool = False,
    raise_interrupt: bool = True,
) -> Generator[List[AddedLine], None, None]:
    """
    Monitor one or more files and yield a list of added lines whenever files change (tail -f behavior)

    Args:
        *paths: file paths to be monitored.
        debounce: maximum time in milliseconds to group changes over before yielding them (while changes are detected)
        step: time to wait for new changes in milliseconds, if no changes are detected in this time, give it
            a try until `rust_timeout` or until a change is detected, then try grouping changes over `debounce` ms
            and yield them (or raise timeout)
        rust_timeout: maximum time in milliseconds to wait in the rust code for changes, `0` means no timeout.
        yield_on_timeout: if `True`, the generator will yield upon timeout in rust even if no changes are detected.
        raise_interrupt: whether to re-raise `KeyboardInterrupt`s, or suppress the error and just stop iterating.

    Yields:
        The generator yields a list of [`AddedLine`][async_tail.main.AddedLine]s.

    ```py title="Example of tail usage"
    from async_tail import tail
    for line in tail('./first/file.log', './second/file.log', raise_interrupt=False):
        print(line)
    ```
    """
    with Tail([str(p) for p in paths]) as tail:
        while True:
            raw_changes = tail.read_line(debounce, step, rust_timeout)
            if raw_changes == 'timeout':
                if yield_on_timeout:
                    yield []
                else:
                    logger.debug('Rust notified timeout, continuing')
            elif raw_changes == 'signal':
                if raise_interrupt:
                    raise KeyboardInterrupt
                else:
                    logger.warning('KeyboardInterrupt caught, stopping tail')
                    return
            else:
                yield raw_changes


async def atail(*paths: Union[Path, str]) -> AsyncGenerator[AddedLine, None]:
    """
    Asynchronous equivalent of [`tail`][async_tail.tail] using pyo3-asyncio
    to handle Rust/Python event loops interoperability

    Args:
        *paths: file paths to be monitored.

    Yields:
        The generator yields [`AddedLine`][async_tail.main.AddedLine]s on-the-go as it is detected

    ```py title="Example of atail usage"
    import asyncio
    from async_tail import atail
    async def main():
        async for line in atail('./first/file.log', './second/file.log'):
            print(line)
    if __name__ == '__main__':
        asyncio.run(main())
    ```
    """
    aio_tail: AIOTail = AIOTail()
    for path in paths:
        await aio_tail.add_file(str(path))
    while True:
        line = await aio_tail.read_line()
        yield line
