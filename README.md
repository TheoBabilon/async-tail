# async-tail

[![CI](https://github.com/TheoBabilon/async-tail/workflows/ci/badge.svg?event=push)](https://github.com/TheoBabilon/async-tail/actions?query=event%3Apush+branch%3Amain+workflow%3Aci)
[![Coverage](https://codecov.io/gh/TheoBabilon/async-tail/branch/main/graph/badge.svg)](https://codecov.io/gh/TheoBabilon/async-tail)

Asynchronous tailing library written in Rust.

---

Python wrapper around Rust [linemux](https://github.com/jmagnuson/linemux) library, which uses the [notify](https://crates.io/crates/notify) cross-platform filesystem notification library.

Uses [PyO3](https://github.com/PyO3/pyo3) Rust bindings and [PyO3-asyncio](https://github.com/awestlake87/pyo3-asyncio) to manage Rust/Python event loops lifecycles.

## Installation

**async-tail** requires Python 3.7 - 3.11.

```bash
pip install async-tail
```

Binaries are available for:

* **Linux**: `x86_64`, `aarch64`, `i686`, `armv7l`, `musl-x86_64`, `musl-aarch64`, `ppc64le` & `s390x`
* **MacOS**: `x86_64` & `arm64` (except python 3.7)
* **Windows**: To be done

Otherwise, you can install from source which requires Rust stable to be installed.

## Usage

Here are some examples of what **async-tail** can do:

### `tail` Usage

```py
from async_tail import tail

for line in tail('./path/to/file.log', './path/to/file_2.log'):
    print(line)
```

### `atail` Usage

```py
import asyncio
from async_tail import atail

async def main():
    async for line in atail('/path/to/file.txt', '/path/to/file_2.txt'):
        print(line)

asyncio.run(main())
```

## Notes

**async-tail** is a way for me to learn Rust and experiment Rust bindings from Python. It is inspired from the great [Samuel COLVIN](https://github.com/samuelcolvin)'s work on [watchfiles](https://github.com/samuelcolvin/watchfiles), which provides a Python wrapper around Rust [notify](https://crates.io/crates/notify) crate. This is still under development. More things will come:

- [x] Write tests
- [x] Setup proper CI
- [ ] Build wheels for Windows
- [ ] Build and expose docs
- [ ] Provide benchmarks
