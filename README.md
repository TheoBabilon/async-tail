# async-tail

Asynchronous tailing library written in Rust.

---

Python wrapper around Rust [linemux](https://github.com/jmagnuson/linemux) library, which uses the [notify](https://crates.io/crates/notify) cross-platform filesystem notification library.

Uses [PyO3](https://github.com/PyO3/pyo3) Rust bindings and [PyO3-asyncio](https://github.com/awestlake87/pyo3-asyncio) to manage Rust/Python event loops lifecycles.

## Usage

Here are some examples of what **async-tail** can do:

### `tail` Usage

```py
from async_tail import tail

for line in tail('./path/to/file.log'):
    print(line)
```

### `atail` Usage

```py
import asyncio
from async_tail import atail

async def main():
    async for line in atail('/path/to/file.txt'):
        print(line)

asyncio.run(main())
```

## Notes

**async-tail** is a way for me to learn Rust and experiment Rust bindings from Python. It is inspired from the great [Samuel COLVIN](https://github.com/samuelcolvin)'s work on [watchfiles](https://github.com/samuelcolvin/watchfiles), which provides a Python wrapper around Rust [notify](https://crates.io/crates/notify) crate. This is still under development and needs several things to be adressed before a first release:

- [x] Write tests
- [ ] Setup proper CI
- [ ] Implement step/debounce_ms/timeout logic for async handler (AIOTail)
