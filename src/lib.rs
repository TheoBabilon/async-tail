use pyo3::prelude::*;

mod r#async;
mod sync;

///
/// A Python module implemented in Rust.
#[pymodule]
fn _async_tail(_py: Python, m: &PyModule) -> PyResult<()> {
    let mut version = env!("CARGO_PKG_VERSION").to_string();
    // cargo uses "1.0-alpha1" etc. while python uses "1.0.0a1", this is not full compatibility,
    // but it's good enough for now
    // see https://docs.rs/semver/1.0.9/semver/struct.Version.html#method.parse for rust spec
    // see https://peps.python.org/pep-0440/ for python spec
    // it seems the dot after "alpha/beta" e.g. "-alpha.1" is not necessary, hence why this works
    version = version.replace("-alpha", "a").replace("-beta", "b");
    m.add("__version__", version)?;
    m.add_class::<self::r#async::AIOTail>()?;
    m.add_class::<self::sync::Tail>()?;
    Ok(())
}
