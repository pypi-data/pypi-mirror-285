use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Extract the sqlite_busy_timeout from a config dictionary
pub fn get_sqlite_busy_timeout(config: &Bound<'_, PyDict>) -> Result<usize, PyErr> {
    match config
        .get_item("sqlite_busy_timeout")
        .expect("config.get(\"sqlite_busy_timeout\" should not raise.")
    {
        Some(timeout) => timeout.extract(),
        None => Ok(60),
    }
}

/// Extract whether to use threading from a config dictionary
pub fn use_threading(config: &Bound<'_, PyDict>) -> bool {
    match config
        .get_item("threading")
        .expect("config.get(\"threading\" should not raise.")
    {
        Some(threading) => threading.extract::<bool>().unwrap_or(false),
        None => false,
    }
}

/// Extract whether to use lightweight reprs from a config dictionary
pub fn lightweight_repr(config: &Bound<'_, PyDict>) -> bool {
    match config
        .get_item("lightweight_repr")
        .expect("config.get(\"lightweight_repr\" should not raise.")
    {
        Some(lightweight_repr) => lightweight_repr.extract::<bool>().unwrap_or(false),
        None => false,
    }
}

/// Extract whether to use omit_return_locals  from a config dictionary
pub fn omit_return_locals(config: &Bound<'_, PyDict>) -> bool {
    match config
        .get_item("omit_return_locals")
        .expect("config.get(\"omit_return_locals\" should not raise.")
    {
        Some(omit_return_locals) => omit_return_locals.extract::<bool>().unwrap_or(false),
        None => false,
    }
}
