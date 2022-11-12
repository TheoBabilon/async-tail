use linemux::MuxedLines;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug)]
struct AIOTailCore {
    lines: MuxedLines,
}

#[pyclass]
pub struct AIOTail(Arc<Mutex<AIOTailCore>>);

#[pymethods]
impl AIOTail {
    #[new]
    pub fn py_new() -> Self {
        AIOTail(Arc::new(Mutex::new(AIOTailCore {
            lines: MuxedLines::new().unwrap(),
        })))
    }

    fn add_file<'a>(&self, py: Python<'a>, path: String) -> PyResult<&'a PyAny> {
        let inner = self.0.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let res = inner.lock().await.lines.add_file(path).await?;
            Ok(res)
        })
    }

    fn read_line<'a>(&self, py: Python<'a>) -> PyResult<&'a PyAny> {
        let inner = self.0.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let line = inner.lock().await.lines.next_line().await?;
            match line {
                Some(val) => Ok((val.line().to_string(), val.source().display().to_string())),
                None => Err(PyException::new_err("An error occured while reading line")),
            }
        })
    }
}
