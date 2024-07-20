use pyo3::exceptions::PyAttributeError;
use pyo3::exceptions::PyKeyError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyFrame;
use pyo3::types::PyTuple;
use pyo3::types::PyType;
use std::env::current_dir;
use std::path::Path;
use std::time::SystemTime;
use ulid::Ulid;

pub const STRING_KEY: &'static str = "a string is always a valid dict key";

/// A serialized frame is a sequence of msgpack-encoded bytes.
pub type SerializedFrame = Vec<u8>;

/// A unix timestamp for the current time.
pub fn timestamp() -> f64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .expect("System time is before unix epoch")
        .as_secs_f64()
}

/// Create a Kolo frame_id from a ulid.
pub fn frame_id() -> String {
    let frame_ulid = Ulid::new();
    format!("frm_{}", frame_ulid.to_string())
}

/// Read the filename and current line number from a Python frame object.
pub fn filename_with_lineno(
    frame: &Bound<'_, PyFrame>,
    py: Python,
) -> Result<(String, usize), PyErr> {
    let f_code = frame.getattr(intern!(py, "f_code"))?;
    let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
    let filename = co_filename.extract::<String>()?;
    let lineno = frame.getattr(intern!(py, "f_lineno"))?;
    let lineno = lineno.extract()?;
    Ok((filename, lineno))
}

/// Combine a filename and line number into Kolo's standard format.
fn format_frame_path(filename: &str, lineno: usize) -> String {
    let path = Path::new(filename);
    let dir = current_dir().expect("Current directory is invalid");
    let relative_path = match path.strip_prefix(&dir) {
        Ok(relative_path) => relative_path,
        Err(_) => path,
    };
    format!("{}:{}", relative_path.display(), lineno)
}

/// Get the frame path from a Python frame.
pub fn frame_path(frame: &Bound<'_, PyFrame>, py: Python) -> Result<String, PyErr> {
    let (filename, lineno) = filename_with_lineno(frame, py)?;
    Ok(format_frame_path(&filename, lineno))
}

/// Get the qualname for the Python object represented by the frame.
///
/// Equivalent to `kolo.profiler.get_qualname`.
pub fn get_qualname(frame: &Bound<'_, PyFrame>, py: Python) -> Result<Option<String>, PyErr> {
    let f_code = frame.getattr(intern!(py, "f_code"))?;
    // Read `co_qualname` on modern Python versions.
    match f_code.getattr(intern!(py, "co_qualname")) {
        Ok(qualname) => {
            let globals = frame.getattr(intern!(py, "f_globals"))?;
            let module = globals.get_item("__name__")?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyAttributeError>(py) => {}
        Err(err) => return Err(err),
    }

    let co_name = f_code.getattr(intern!(py, "co_name"))?;
    let name = co_name.extract::<String>()?;
    // Special case for module objects
    if name.as_str() == "<module>" {
        let globals = frame.getattr(intern!(py, "f_globals"))?;
        let module = globals.get_item("__name__")?;
        return Ok(Some(format!("{}.<module>", module)));
    }

    // Fallback handling for legacy Python versions without `co_qualname`.
    match _get_qualname_inner(frame, py, &co_name) {
        Ok(qualname) => Ok(qualname),
        Err(_) => Ok(None),
    }
}

fn _get_qualname_inner(
    frame: &Bound<'_, PyFrame>,
    py: Python,
    co_name: &Bound<'_, PyAny>,
) -> Result<Option<String>, PyErr> {
    let outer_frame = frame.getattr(intern!(py, "f_back"))?;
    if outer_frame.is_none() {
        return Ok(None);
    }

    let outer_frame_locals = outer_frame.getattr(intern!(py, "f_locals"))?;
    match outer_frame_locals.get_item(co_name) {
        Ok(function) => {
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    }

    let locals = frame.getattr(intern!(py, "f_locals"))?;
    let inspect = PyModule::import_bound(py, "inspect")?;
    let getattr_static = inspect.getattr(intern!(py, "getattr_static"))?;
    match locals.get_item("self") {
        Ok(locals_self) => {
            let function = getattr_static.call1((locals_self, co_name))?;
            let builtins = py.import_bound("builtins")?;
            let property = builtins.getattr(intern!(py, "property"))?;
            let property = property.downcast()?;
            let function = match function.is_instance(property)? {
                true => function.getattr(intern!(py, "fget"))?,
                false => function,
            };
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    };

    match locals.get_item("cls") {
        Ok(cls) if cls.is_instance_of::<PyType>() => {
            let function = getattr_static.call1((cls, co_name))?;
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Ok(_) => {}
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    }
    let globals = frame.getattr(intern!(py, "f_globals"))?;
    match locals.get_item("__qualname__") {
        Ok(qualname) => {
            let module = globals.get_item("__name__")?;
            Ok(Some(format!("{}.{}", module, qualname)))
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {
            let function = globals.get_item(co_name)?;
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            Ok(Some(format!("{}.{}", module, qualname)))
        }
        Err(_) => Ok(None),
    }
}

/// Serialize an arbitrary Python object as msgpack by delegating to `kolo.serialize.dump_msgpack`
/// or `kolo.serialize.dump_msgpack_lightweight_repr`.
pub fn dump_msgpack(
    py: Python,
    data: &Bound<'_, PyAny>,
    lightweight_repr: bool,
) -> Result<Vec<u8>, PyErr> {
    let serialize = PyModule::import_bound(py, "kolo.serialize")?;
    let args = PyTuple::new_bound(py, [&data]);
    let data = match lightweight_repr {
        false => serialize.call_method1("dump_msgpack", args)?,
        true => serialize.call_method1("dump_msgpack_lightweight_repr", args)?,
    };
    data.extract::<Vec<u8>>()
}

/// Write a key, value pair of a msgpack map where the value is a string or None.
pub fn write_str_pair(buf: &mut Vec<u8>, key: &str, value: Option<&str>) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    match value {
        Some(value) => rmp::encode::write_str(buf, value).expect("Writing to memory, not I/O"),
        None => rmp::encode::write_nil(buf).expect("Writing to memory, not I/O"),
    };
}

/// Write a key, value pair of a msgpack map where the value is already valid msgpack bytes.
pub fn write_raw_pair(buf: &mut Vec<u8>, key: &str, value: &mut Vec<u8>) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    buf.append(value);
}

/// Write a key, value pair of a msgpack map where the value is an integer or None.
pub fn write_int_pair(buf: &mut Vec<u8>, key: &str, value: Option<usize>) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    match value {
        Some(value) => {
            rmp::encode::write_uint(buf, value as u64).expect("Writing to memory, not I/O");
        }
        None => {
            rmp::encode::write_nil(buf).expect("Writing to memory, not I/O");
        }
    }
}

/// Write a key, value pair of a msgpack map where the value is a float.
pub fn write_f64_pair(buf: &mut Vec<u8>, key: &str, value: f64) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    rmp::encode::write_f64(buf, value).expect("Writing to memory, not I/O");
}

/// Write a key, value pair of a msgpack map where the value is a boolean.
pub fn write_bool_pair(buf: &mut Vec<u8>, key: &str, value: bool) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    rmp::encode::write_bool(buf, value).expect("Writing to memory, not I/O");
}

/// Write a msgpack array from a vector of already valid msgpack frames.
pub fn write_raw_frames(buf: &mut Vec<u8>, frames: Vec<SerializedFrame>) {
    rmp::encode::write_array_len(buf, frames.len() as u32).expect("Writing to memory, not I/O");
    buf.append(&mut frames.into_iter().flatten().collect());
}

/// Get the thread name and native id of the current thread from Python.
///
/// We can't get these from Rust because the thread name is a Python concept and the native id is
/// an operating system concept not exposed by Rust.
pub fn current_thread(py: Python) -> Result<(String, Option<usize>), PyErr> {
    let threading = PyModule::import_bound(py, "threading")?;
    let thread = threading.call_method0("current_thread")?;
    let thread_name = thread.getattr(intern!(py, "name"))?;
    let thread_name = thread_name.extract()?;
    let native_id = match thread.getattr(intern!(py, "native_id")) {
        Ok(native_id) => native_id.extract()?,
        Err(err) if err.is_instance_of::<PyAttributeError>(py) => None,
        Err(err) => return Err(err),
    };
    Ok((thread_name, native_id))
}

/// Get the Python thread id for the main thread.
pub fn get_main_thread_id(py: Python) -> Result<Option<usize>, PyErr> {
    let threading = PyModule::import_bound(py, "threading")?;
    let main_thread = threading.call_method0(intern!(py, "main_thread"))?;
    let main_thread_id = match main_thread.getattr(intern!(py, "native_id")) {
        Ok(main_thread_id) => main_thread_id.extract()?,
        Err(err) if err.is_instance_of::<PyAttributeError>(py) => None,
        Err(err) => return Err(err),
    };
    Ok(main_thread_id)
}

pub struct UserCodeCallSite {
    pub call_frame_id: String,
    pub line_number: i32,
}

impl UserCodeCallSite {
    pub fn into_msgpack_value(self) -> rmpv::Value {
        rmpv::Value::Map(vec![
            ("call_frame_id".into(), self.call_frame_id.into()),
            ("line_number".into(), self.line_number.into()),
        ])
    }

    pub fn into_pydict(self, py: Python) -> Bound<'_, PyDict> {
        let call_site = PyDict::new_bound(py);
        call_site
            .set_item("call_frame_id", self.call_frame_id)
            .expect(STRING_KEY);
        call_site
            .set_item("line_number", self.line_number)
            .expect(STRING_KEY);
        call_site
    }
}

/// Find the frame_id and line number of the user code that called the active function.
///
/// Analagous to `kolo.serialize.user_code_call_site`.
pub fn user_code_call_site(
    call_frames: Vec<(Bound<'_, PyAny>, String)>,
    frame_id: &str,
) -> Result<Option<UserCodeCallSite>, PyErr> {
    let (call_frame, call_frame_id) = match call_frames
        .iter()
        .rev()
        .take(2)
        .find(|(_f, f_id)| f_id != frame_id)
    {
        Some(frame_data) => frame_data,
        None => {
            return Ok(None);
        }
    };

    let pyframe = call_frame.downcast::<PyFrame>()?;
    let py = pyframe.py();
    Ok(Some(UserCodeCallSite {
        call_frame_id: call_frame_id.to_string(),
        line_number: pyframe.getattr(intern!(py, "f_lineno"))?.extract()?,
    }))
}

/// Load Kolo's version from Python.
pub fn kolo_version(py: Python) -> Result<String, PyErr> {
    PyModule::import_bound(py, "kolo.version")?
        .getattr(intern!(py, "__version__"))?
        .extract::<String>()
}

/// Get the current git commit sha from Python.
pub fn git_commit_sha(py: Python) -> Result<Option<String>, PyErr> {
    PyModule::import_bound(py, "kolo.git")?
        .getattr(intern!(py, "COMMIT_SHA"))?
        .extract::<Option<String>>()
}

/// Get the command line arguments of the traced program from Python.
pub fn get_argv(py: Python) -> Result<Vec<String>, PyErr> {
    PyModule::import_bound(py, "sys")?
        .getattr(intern!(py, "argv"))?
        .extract::<Vec<String>>()
}

/// Load the local variables from a Python frame.
///
/// Omit the `__builtins__` entry from the trace because it is large and rarely interesting.
pub fn get_locals<'py>(
    frame: &Bound<'py, PyFrame>,
    event: &str,
    omit_return_locals: bool,
) -> Result<Bound<'py, PyAny>, PyErr> {
    let py = frame.py();

    if event == "return" && omit_return_locals {
        return Ok(py.None().into_bound(py));
    }

    let locals = frame.getattr(intern!(py, "f_locals"))?;
    let locals = locals.downcast_into::<PyDict>().unwrap();
    let result = match locals
        .get_item("__builtins__")
        .expect("locals.get(\"__builtins__\") should not raise.")
    {
        Some(_) => {
            let locals = locals.copy().unwrap();
            locals.del_item("__builtins__").unwrap();
            locals
        }
        None => locals,
    };

    Ok(result.into_any())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_frame_path_invalid_path() {
        let frame_path = format_frame_path("<module>", 23);

        assert_eq!(frame_path, "<module>:23");
    }
}
