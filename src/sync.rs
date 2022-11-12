use linemux::MuxedLines;
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use std::thread;
use std::thread::sleep;
use std::time::{Duration, SystemTime};
use tokio::runtime::Runtime;

#[pyclass]
pub struct Tail {
    changes: Arc<Mutex<Vec<(String, String)>>>,
}

#[pymethods]
impl Tail {
    #[new]
    fn py_new(watch_files: Vec<String>) -> PyResult<Self> {
        let changes: Arc<Mutex<Vec<(String, String)>>> = Arc::new(Mutex::new(Vec::new()));
        let changes_clone = changes.clone();
        let mut lines = MuxedLines::new()?;

        let _handle = thread::spawn(move || {
            let rt = Runtime::new().unwrap();
            rt.block_on(async move {
                for path in watch_files {
                    lines.add_file(path).await.unwrap();
                }
                while let Ok(Some(line)) = lines.next_line().await {
                    changes_clone
                        .lock()
                        .unwrap()
                        .push((line.line().to_string(), line.source().display().to_string()));
                }
            });
        });
        Ok(Tail { changes })
    }

    pub fn read_line(&self, py: Python, debounce_ms: u64, step_ms: u64, timeout_ms: u64) -> PyResult<PyObject> {
        let mut max_debounce_time: Option<SystemTime> = None;
        let step_time = Duration::from_millis(step_ms);
        let mut last_size: usize = 0;
        let max_timeout_time: Option<SystemTime> = match timeout_ms {
            0 => None,
            _ => Some(SystemTime::now() + Duration::from_millis(timeout_ms)),
        };
        loop {
            py.allow_threads(|| sleep(step_time));
            match py.check_signals() {
                Ok(_) => (),
                Err(_) => {
                    self.clear();
                    return Ok("signal".to_object(py));
                }
            };
            let size = self.changes.lock().unwrap().len();
            if size > 0 {
                if size == last_size {
                    break;
                }
                last_size = size;

                let now = SystemTime::now();
                if let Some(max_time) = max_debounce_time {
                    if now > max_time {
                        break;
                    }
                } else {
                    max_debounce_time = Some(now + Duration::from_millis(debounce_ms));
                }
            } else if let Some(max_time) = max_timeout_time {
                if SystemTime::now() > max_time {
                    self.clear();
                    return Ok("timeout".to_object(py));
                }
            }
        }
        let py_changes = self.changes.lock().unwrap().to_object(py);
        self.clear();
        Ok(py_changes)
    }

    fn clear(&self) {
        self.changes.lock().unwrap().clear();
    }

    // https://github.com/PyO3/pyo3/issues/1205#issuecomment-1164096251 for advice on `__enter__`
    pub fn __enter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    // Awaiting https://github.com/jmagnuson/linemux/issues/12
    pub fn close(&mut self) {}

    pub fn __exit__(&mut self, _exc_type: PyObject, _exc_value: PyObject, _traceback: PyObject) {
        self.close();
    }
}
