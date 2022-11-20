from typing import Any, Awaitable, List, Literal, Tuple, Union

__all__ = ('AIOTail', 'Tail')

__version__: str
"""The package version as defined in `Cargo.toml`, modified to match python's versioning semantics."""

class Tail:

    """
    Interface to the Rust [linemux](https://crates.io/crates/linemux) crate which does
    the heavy lifting of monitoring for file changes using the underlying [notify](https://crates.io/crates/notify)
    """

    def __init__(self, watch_files: List[str]) -> None:
        """
        Create a new `MuxedLines` instance and start a thread to watch for changes.

        Args:
            watch_files: file paths to watch for changes
        """
    def read_line(
        self,
        debounce_ms: int,
        step_ms: int,
        timeout_ms: int,
    ) -> Union[List[Tuple[str, str]], Literal['signal', 'timeout']]:
        """
        Monitor files for changes.

        This method will wait `timeout_ms` milliseconds for changes, but once a change is detected,
        it will group changes and return in no more than `debounce_ms` milliseconds.

        The GIL is released during a `step_ms` sleep on each iteration to avoid
        blocking python.

        Args:
            debounce_ms: maximum time in milliseconds to group changes over before returning.
            step: time to wait for new changes in milliseconds, if no changes are detected in this time,
                give it a try until `timeout_ms` or until a change is detected, then try grouping changes
                over `debounce_ms` ms and yield them (or raise timeout)
            timeout_ms: maximum time in milliseconds to wait for changes before returning,
                `0` means wait indefinitely, `debounce_ms` takes precedence over `timeout_ms` once
                a change is detected.

        Returns:
            See below.

        Return values have the following meanings:

        * Change details as a `list` of `(new_line, path)` tuples, `new_line` is the raw added line in file as string
          `path` is a string representing the path of the file that changed
        * `'signal'` string, if a signal was received
        * `'timeout'` string, if `timeout_ms` was exceeded
        """
    def __enter__(self) -> 'Tail':
        """
        Does nothing, but allows `Tail` to be used as a context manager.

            !!! note

            The monitoring thead is created when an instance is initiated, not on `__enter__`.
        """
    def __exit__(self, *args: Any) -> None:
        """
        Calls [`close`][async_tail._async_tail.Tail.close].
        """
    def close(self) -> None:
        """
        Does nothing for now but will be used to deregister files from being monitored once
        https://github.com/jmagnuson/linemux/issues/12 is resolved
        """

class AIOTail:

    """
    Interface to the Rust [linemux](https://crates.io/crates/linemux) crate which does
    the heavy lifting of monitoring for file changes using the underlying [notify](https://crates.io/crates/notify)
    Async-compliant version leveraging pyo3-asyncio to provide Rust/Python event loop interoperability
    """

    def __init__(self) -> None:
        """
        Create a new `MuxedLines` instance
        """
    def add_file(self, path: str) -> Awaitable[str]:
        """
        Add a file to the list of monitored files

        Args:
            path: file path to be added the list of monitored files

        Returns:
            Rust Future made available thanks to `pyo3-asyncio` `future_into_py`, can be awaited from Python
            Returns the resolved absolute path of the provided file path
        """
    def read_line(self) -> Awaitable[Tuple[str, str]]:
        """
        Awaits for any change in the list of monitored files and yields it

        Returns:
            Rust Future made available thanks to `pyo3-asyncio` `future_into_py`, can be awaited from Python
            Returns added line as a `tuple` of `(new_line, path)`, `new_line` is the raw added line in file as string
                `path` is a string representing the path of the file that changed
        """
