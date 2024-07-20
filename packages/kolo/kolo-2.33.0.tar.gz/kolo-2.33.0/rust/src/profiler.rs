use bstr::Finder;
use hashbrown::HashMap;
use pyo3::ffi;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::sync::GILProtected;
use pyo3::types::PyBytes;
use pyo3::types::PyDict;
use pyo3::types::PyFrame;
use std::borrow::Cow;
use std::cell::RefCell;
use std::os::raw::c_int;
use thread_local::ThreadLocal;
use ulid::Ulid;

use super::config;
use super::filters;
use super::plugins::{load_plugins, PluginProcessor};
use super::utils;
use super::utils::SerializedFrame;

#[pyclass(module = "kolo._kolo")]
/// This struct holds data during profiling.
///
/// Several attributes are protected by `GILProtected` or `ThreadLocal` to support multi-threading.
/// Attributes guarded with `GILProtected` can only be mutated when we hold the GIL.
/// Attributes guarded with `ThreadLocal` store data that is only relevant to the current thread.
pub struct KoloProfiler {
    /// The location of the Kolo database on disk.
    db_path: String,
    /// Whether a trace should be saved every time a Python test exits.
    one_trace_per_test: bool,
    /// An identifier for the current trace. Can change if `one_trace_per_test` is `true`.
    trace_id: GILProtected<RefCell<String>>,
    /// The traced frames for the main thread or the only thread if `use_threading` is `false`.
    frames_of_interest: GILProtected<RefCell<Vec<SerializedFrame>>>,
    /// The traced frames for all other threads when `use_threading` is `true`.
    frames: GILProtected<RefCell<HashMap<usize, Vec<SerializedFrame>>>>,
    /// A list of `Finder`s to check a filepath fragment for inclusion in the trace.
    include_frames: Vec<Finder<'static>>,
    /// A list of `Finder`s to check a filepath fragment for exclusion from the trace.
    ignore_frames: Vec<Finder<'static>>,
    /// A dictionary mapping `co_name` to a list of associated `PluginProcessor` instances.
    default_include_frames: GILProtected<RefCell<HashMap<String, Vec<PluginProcessor>>>>,
    /// A list of `PyFrame` objects (as the opaque `PyObject` type) and their associated `frame_id`.
    call_frames: ThreadLocal<RefCell<Vec<(PyObject, String)>>>,
    /// The time tracing started.
    timestamp: f64,
    /// A dictionary mapping the Python `id` of a frame to the Kolo `frame_id`.
    _frame_ids: ThreadLocal<RefCell<HashMap<usize, String>>>,
    /// The `native_id` of the main thread. Can be `None` when threading is not supported, e.g. by
    /// pyodide.
    main_thread_id: Option<usize>,
    /// A tag for where the profiler was created. e.g. `kolo.enable` or
    /// `kolo.middleware.KoloMiddleware`.
    source: String,
    /// A timeout for saving the trace to sqlite.
    timeout: usize,
    /// Whether we're tracing multiple threads.
    use_threading: bool,
    /// Whether to use the lightweight repr format when serializing frame data.
    lightweight_repr: bool,
    /// Omit return locals
    omit_return_locals: bool,
}

#[pymethods]
impl KoloProfiler {
    /// This is called from Python code to trigger saving the trace. Used by
    /// `KoloProfiler.save_request_in_db`.
    fn save_request_in_db(&self) -> Result<(), PyErr> {
        Python::with_gil(|py| self.save_in_db(py))
    }

    /// This is called from Python code to build the trace. Used by
    /// `KoloProfiler.upload_trace_in_thread`.
    fn build_trace(&self) -> Result<Py<PyBytes>, PyErr> {
        Python::with_gil(|py| self.build_trace_inner(py))
    }

    /// Register the profiler on the current thread. Called by `threading.setprofile`. See
    /// `register_profiler` in `lib.rs`.
    fn register_threading_profiler(
        slf: PyRef<'_, Self>,
        _frame: PyObject,
        _event: PyObject,
        _arg: PyObject,
    ) -> Result<(), PyErr> {
        // Safety:
        //
        // PyEval_SetProfile takes two arguments:
        //  * trace_func: Option<Py_tracefunc>
        //  * arg1:       *mut PyObject
        //
        // `profile_callback` matches the signature of a `Py_tracefunc`, so we only
        // need to wrap it in `Some`.
        // `slf.into_ptr()` is a pointer to our Rust profiler instance as a Python
        // object.
        //
        // We must also hold the GIL, which we do because we're called from python.
        //
        // https://docs.rs/pyo3-ffi/latest/pyo3_ffi/fn.PyEval_SetProfile.html
        // https://docs.python.org/3/c-api/init.html#c.PyEval_SetProfile
        unsafe {
            ffi::PyEval_SetProfile(Some(profile_callback), slf.into_ptr());
        }
        Ok(())
    }
}

impl KoloProfiler {
    /// Create a new `KoloProfiler` instance from the Python `KoloProfiler` class.
    ///
    /// Converts the Python objects into their corresponding Rust types.
    pub fn new_from_python(py: Python, py_profiler: &Bound<'_, PyAny>) -> Result<Self, PyErr> {
        let config = py_profiler.getattr(intern!(py, "config"))?;
        let config = config.downcast::<PyDict>()?;
        let filters = config
            .get_item("filters")
            .expect("config.get(\"filters\" should not raise.");

        Ok(Self {
            db_path: py_profiler
                .getattr(intern!(py, "db_path"))?
                .str()?
                .extract()?,
            one_trace_per_test: py_profiler
                .getattr(intern!(py, "one_trace_per_test"))?
                .extract()?,
            trace_id: GILProtected::new(
                py_profiler
                    .getattr(intern!(py, "trace_id"))?
                    .extract::<String>()?
                    .into(),
            ),
            source: py_profiler
                .getattr(intern!(py, "source"))?
                .extract::<String>()?,
            frames: GILProtected::new(HashMap::new().into()),
            frames_of_interest: GILProtected::new(Vec::new().into()),
            include_frames: filters::load_filters(&filters, "include_frames")?,
            ignore_frames: filters::load_filters(&filters, "ignore_frames")?,
            default_include_frames: GILProtected::new(load_plugins(py, config)?.into()),
            call_frames: ThreadLocal::new(),
            timestamp: utils::timestamp(),
            _frame_ids: ThreadLocal::new(),
            main_thread_id: utils::get_main_thread_id(py)?,
            timeout: config::get_sqlite_busy_timeout(config)?,
            use_threading: config::use_threading(config),
            lightweight_repr: config::lightweight_repr(config),
            omit_return_locals: config::omit_return_locals(config),
        })
    }

    /// Helper method for serializing the command line arguments of the Python program as msgpack.
    ///
    /// Must be called in the context of writing a msgpack map.
    /// The first value written is the `command_line_args` key. The other values are the command
    /// line argument list as the map value.
    fn write_argv(&self, buf: &mut Vec<u8>, argv: Vec<String>) {
        rmp::encode::write_str(buf, "command_line_args").expect("Writing to memory, not I/O");
        rmp::encode::write_array_len(buf, argv.len() as u32).expect("Writing to memory, not I/O");
        for arg in argv {
            rmp::encode::write_str(buf, &arg).expect("Writing to memory, not I/O");
        }
    }

    /// Helper method for serializing the `frames` of the trace as msgpack.
    ///
    /// Must be called in the context of writing a msgpack map.
    /// The first value written is the `frames` key. The other values are a map from `thread_id` to
    /// a list of frames.
    fn write_frames(&self, buf: &mut Vec<u8>, frames: HashMap<usize, Vec<SerializedFrame>>) {
        rmp::encode::write_str(buf, "frames").expect("Writing to memory, not I/O");
        rmp::encode::write_map_len(buf, frames.len() as u32).expect("Writing to memory, not I/O");
        for (thread_id, frames) in frames {
            rmp::encode::write_uint(buf, thread_id as u64).expect("Writing to memory, not I/O");
            utils::write_raw_frames(buf, frames);
        }
    }

    /// Helper method for serializing the `frames_of_interest` of the trace as msgpack.
    ///
    /// Must be called in the context of writing a msgpack map.
    /// The first value written is the `frames` key. The other value is a list of frames.
    fn write_frames_of_interest(
        &self,
        buf: &mut Vec<u8>,
        frames_of_interest: Vec<SerializedFrame>,
    ) {
        rmp::encode::write_str(buf, "frames_of_interest").expect("Writing to memory, not I/O");
        utils::write_raw_frames(buf, frames_of_interest);
    }

    /// Helper method for serializing the `meta` of the trace as msgpack.
    ///
    /// Must be called in the context of writing a msgpack map.
    /// The first value written is the `meta` key. The other value is a map containing `version`,
    /// `source` and `use_frame_boundaries`.
    fn write_meta(&self, buf: &mut Vec<u8>, version: &str, source: &str) {
        rmp::encode::write_str(buf, "meta").expect("Writing to memory, not I/O");
        rmp::encode::write_map_len(buf, 3).expect("Writing to memory, not I/O");

        utils::write_str_pair(buf, "version", Some(version));
        utils::write_str_pair(buf, "source", Some(source));
        utils::write_bool_pair(buf, "use_frame_boundaries", true);
    }

    /// Build the trace as msgpack ready to save to sqlite or upload to the dashboard.
    fn build_trace_inner(&self, py: Python) -> Result<Py<PyBytes>, PyErr> {
        let version = utils::kolo_version(py)?;
        let commit_sha = utils::git_commit_sha(py)?;
        let argv = utils::get_argv(py)?;
        let frames_of_interest = self.frames_of_interest.get(py).take();
        let frames = self.frames.get(py).take();

        let trace_id = self.trace_id.get(py).borrow().clone();
        let mut buf: Vec<u8> = vec![];

        // Start writing the top-level msgpack map. The following entries are key, value pairs.
        // It is important that the length written here matches the number of key, value pairs
        // exactly.
        rmp::encode::write_map_len(&mut buf, 8).expect("Writing to memory, not I/O");
        self.write_argv(&mut buf, argv);
        utils::write_str_pair(&mut buf, "current_commit_sha", commit_sha.as_deref());
        self.write_frames(&mut buf, frames);
        self.write_frames_of_interest(&mut buf, frames_of_interest);
        utils::write_int_pair(&mut buf, "main_thread_id", self.main_thread_id);
        self.write_meta(&mut buf, &version, &self.source);
        utils::write_f64_pair(&mut buf, "timestamp", self.timestamp);
        utils::write_str_pair(&mut buf, "trace_id", Some(&trace_id));

        Ok(PyBytes::new_bound(py, &buf).unbind())
    }

    /// Save the trace to sqlite.
    ///
    /// We delegate to the Python implementation because the time here is mostly spent in IO with
    /// the filesystem, so there's unlikely to be much of a performance win to justify a Rust
    /// implementation.
    fn save_in_db(&self, py: Python) -> Result<(), PyErr> {
        let kwargs = PyDict::new_bound(py);
        kwargs.set_item("timeout", self.timeout).unwrap();

        let data = self.build_trace_inner(py)?;
        kwargs.set_item("msgpack", data).unwrap();

        let trace_id = self.trace_id.get(py).borrow().clone();
        let db = PyModule::import_bound(py, "kolo.db")?;
        let save = db.getattr(intern!(py, "save_trace_in_sqlite"))?;
        save.call((&self.db_path, &trace_id), Some(&kwargs))?;
        Ok(())
    }

    /// Create a trace frame in msgpack format from a profiling event.
    ///
    /// Analogous to the `KoloProfiler.process_frame` method in Python.
    fn process_frame(
        &self,
        pyframe: &Bound<'_, PyFrame>,
        event: &str,
        arg: PyObject,
        name: &str,
        frame_types: &mut Vec<String>,
        frames: &mut Vec<SerializedFrame>,
    ) -> Result<(), PyErr> {
        let py = pyframe.py();
        let pyframe_id = pyframe.as_ptr() as usize;

        let frame_id = self.get_and_set_frame_id(event, pyframe_id);
        let user_code_call_site = self.get_user_code_call_site(pyframe, event, &frame_id)?;

        // Gather frame data and convert to Rust types
        let (thread_name, native_id) = utils::current_thread(py)?;
        let arg = arg.downcast_bound::<PyAny>(py)?;
        let path = utils::frame_path(pyframe, py)?;
        let qualname = utils::get_qualname(pyframe, py)?;
        let locals = utils::get_locals(pyframe, event, self.omit_return_locals)?;

        // Serialize frame data as msgpack
        let mut arg = utils::dump_msgpack(py, arg, self.lightweight_repr)?;
        let mut locals = utils::dump_msgpack(py, &locals, self.lightweight_repr)?;

        let mut buf: Vec<u8> = vec![];

        // The map length must match the number of key, value pairs written next exactly.
        rmp::encode::write_map_len(&mut buf, 12).expect("Writing to memory, not I/O");

        utils::write_str_pair(&mut buf, "path", Some(&path));
        utils::write_str_pair(&mut buf, "co_name", Some(name));
        utils::write_str_pair(&mut buf, "qualname", qualname.as_deref());
        utils::write_str_pair(&mut buf, "event", Some(event));
        utils::write_str_pair(&mut buf, "frame_id", Some(&frame_id));
        utils::write_raw_pair(&mut buf, "arg", &mut arg);
        utils::write_raw_pair(&mut buf, "locals", &mut locals);
        utils::write_str_pair(&mut buf, "thread", Some(&thread_name));
        utils::write_int_pair(&mut buf, "thread_native_id", native_id);
        utils::write_f64_pair(&mut buf, "timestamp", utils::timestamp());
        utils::write_str_pair(&mut buf, "type", Some("frame"));
        self.write_user_code_call_site(&mut buf, user_code_call_site);

        // Push the new SerializedFrame and any other related SerializedFrames into
        // `self.frames_of_interest` or `self.frames`.
        frames.push(buf);
        frame_types.push("frame".to_string());
        self.push_frames(py, event, frame_types, frames)
    }

    /// Helper method for process_frame. Returns the Kolo `frame_id` for the current frame.
    ///
    /// Adds entries to `self._frame_ids` for `call` events.
    /// Reads entries from `self._frame_ids` for `return` events.
    fn get_and_set_frame_id(&self, event: &str, pyframe_id: usize) -> String {
        match event {
            "call" => {
                let frame_id = utils::frame_id();
                self._frame_ids
                    .get_or_default()
                    .borrow_mut()
                    .insert(pyframe_id, frame_id.clone());
                frame_id
            }
            "return" => match self
                ._frame_ids
                .get_or_default()
                .borrow()
                .get(&pyframe_id)
                .cloned()
            {
                Some(frame_id) => frame_id,
                None => utils::frame_id(),
            },
            _ => unreachable!(),
        }
    }

    /// Helper method for process_frame to obtain the user_code_call_site data.
    ///
    /// `self.call_frames` needs to be passed to `utils::user_code_call_site` before
    /// `self.update_call_frames` is called.
    fn get_user_code_call_site(
        &self,
        pyframe: &Bound<'_, PyFrame>,
        event: &str,
        frame_id: &str,
    ) -> Result<Option<utils::UserCodeCallSite>, PyErr> {
        let py = pyframe.py();
        let call_frames = self
            .call_frames
            .get_or_default()
            .borrow()
            .iter()
            .map(|(frame, frame_id)| (frame.bind(py).clone(), frame_id.clone()))
            .collect();
        let user_code_call_site = utils::user_code_call_site(call_frames, frame_id)?;
        self.update_call_frames(event, pyframe, frame_id);
        Ok(user_code_call_site)
    }

    /// Update `self.call_frames` for future tracing events.
    ///
    /// Adds entries to `self.call_frames` for `call` events.
    /// Removes entries from `self.call_frames` for `return` events.
    fn update_call_frames(&self, event: &str, frame: &Bound<'_, PyFrame>, frame_id: &str) {
        match (event, frame_id) {
            ("call", frame_id) => {
                self.call_frames
                    .get_or_default()
                    .borrow_mut()
                    .push((frame.clone().into(), frame_id.to_string()));
            }
            ("return", _) => {
                if let Some(e) = self.call_frames.get() {
                    e.borrow_mut().pop();
                }
            }
            _ => {}
        }
    }

    /// Helper method for serializing the `user_code_call_site` of the trace as msgpack.
    ///
    /// Must be called in the context of writing a msgpack map.
    fn write_user_code_call_site(
        &self,
        buf: &mut Vec<u8>,
        user_code_call_site: Option<utils::UserCodeCallSite>,
    ) {
        let user_code_call_site = match user_code_call_site {
            Some(user_code_call_site) => user_code_call_site.into_msgpack_value(),
            None => rmpv::Value::Nil,
        };
        rmp::encode::write_str(buf, "user_code_call_site").expect("Writing to memory, not I/O");
        rmpv::encode::write_value(buf, &user_code_call_site).unwrap();
    }

    /// Helper method to manage pushing frames into self.frames_of_interest and self.frames.
    ///
    /// Also handles marking the start of a test and saving a trace at the end of a test when
    /// `self.one_trace_per_test` is `true`.
    fn push_frames(
        &self,
        py: Python,
        event: &str,
        frame_types: &mut [String],
        frames: &mut Vec<SerializedFrame>,
    ) -> Result<(), PyErr> {
        // Optimise the common case of no frames to push.
        if frame_types.is_empty() {
            return Ok(());
        }

        // Reverse the order of return frames so call and return frames can be paired up properly.
        if event == "return" {
            frames.reverse();
            frame_types.reverse();
        }

        let (_, native_id) = utils::current_thread(py)?;

        if self.one_trace_per_test {
            for (index, frame_type) in frame_types.iter().enumerate() {
                match frame_type.as_str() {
                    "start_test" => {
                        frames.drain(..index);
                        self.start_test(py)
                    }
                    "end_test" => {
                        let mut before: Vec<SerializedFrame> = frames.drain(..index + 1).collect();
                        self.push_frame_data(py, native_id, &mut before);
                        self.save_in_db(py)?;
                    }
                    _ => {}
                }
            }
        }
        self.push_frame_data(py, native_id, frames);
        Ok(())
    }

    /// Helper method to push frames into `self.frames_of_interest` and `self.frames`.
    fn push_frame_data(
        &self,
        py: Python,
        native_id: Option<usize>,
        frames: &mut Vec<SerializedFrame>,
    ) {
        match native_id {
            None => self.frames_of_interest.get(py).borrow_mut().append(frames),
            Some(native_id) => {
                if !self.use_threading || Some(native_id) == self.main_thread_id {
                    self.frames_of_interest.get(py).borrow_mut().append(frames);
                } else {
                    self.frames
                        .get(py)
                        .borrow_mut()
                        .entry(native_id)
                        .or_default()
                        .append(frames);
                };
            }
        }
    }

    /// Start a new trace because a new test has started.
    fn start_test(&self, py: Python) {
        // Set a new `self.trace_id`.
        let trace_id = Ulid::new();
        let trace_id = format!("trc_{}", trace_id.to_string());
        let mut self_trace_id = self.trace_id.get(py).borrow_mut();
        *self_trace_id = trace_id;

        // Clear `self.frames_of_interest` and `self.frames` of earlier frames.
        let mut frames_of_interest = self.frames_of_interest.get(py).borrow_mut();
        *frames_of_interest = vec![];
        let mut frames = self.frames.get(py).borrow_mut();
        *frames = HashMap::new();
    }

    /// Check if we should include the current frame in the trace because a user defined include
    /// matched.
    fn process_include_frames(&self, filename: &str) -> bool {
        self.include_frames
            .iter()
            .any(|finder| finder.find(filename).is_some())
    }

    /// Check if we should exclude the current frame from the trace because a user defined ignore
    /// matched.
    fn process_ignore_frames(&self, filename: &str) -> bool {
        self.ignore_frames
            .iter()
            .any(|finder| finder.find(filename).is_some())
    }

    /// Check if we should exclude the current frame from the trace using Kolo's builtin filters.
    fn process_default_ignore_frames(
        &self,
        pyframe: &Bound<'_, PyFrame>,
        co_filename: &str,
    ) -> bool {
        filters::library_filter(co_filename)
            | filters::frozen_filter(co_filename)
            | filters::kolo_filter(co_filename)
            | filters::exec_filter(co_filename)
            | filters::pytest_generated_filter(co_filename)
            | filters::attrs_filter(co_filename, pyframe)
    }

    /// Check if we should include the current frame in the trace.
    fn include_frame(&self, pyframe: &Bound<'_, PyFrame>, filename: &str) -> bool {
        self.process_include_frames(filename) | !self.ignore_frame(pyframe, filename)
    }

    /// Check if we should exclude the current frame from the trace.
    fn ignore_frame(&self, pyframe: &Bound<'_, PyFrame>, filename: &str) -> bool {
        self.process_default_ignore_frames(pyframe, filename) | self.process_ignore_frames(filename)
    }

    /// Run a frame processor (from `default_include_frames`) to build a Kolo frame.
    ///
    /// Analogous to the `default_include_frames` handling in `KoloProfiler.__call__`.
    fn run_frame_processor(
        &self,
        py: Python,
        processor: &PluginProcessor,
        pyframe: &Bound<'_, PyFrame>,
        event: &str,
        arg: &PyObject,
        filename: &str,
    ) -> Result<Option<(String, Vec<u8>)>, PyErr> {
        if !processor.matches(py, pyframe, event, arg, filename)? {
            return Ok(None);
        }
        let call_frames = self
            .call_frames
            .get_or_default()
            .borrow()
            .iter()
            .map(|(frame, frame_id)| (frame.bind(py).clone(), frame_id.clone()))
            .collect();
        let data = match processor.process(py, pyframe, event, arg, call_frames)? {
            Some(data) => data,
            None => return Ok(None),
        };
        let frame_type = data
            .bind(py)
            .get_item("type")
            .expect("data[\"type\"] should not raise.")
            .expect("data[\"type\"] should not be missing.")
            .extract()?;

        let data = utils::dump_msgpack(py, data.bind(py), self.lightweight_repr)?;

        Ok(Some((frame_type, data)))
    }

    /// Run the Kolo profiling logic.
    ///
    /// Analagous to `KoloProfiler.__call__`.
    fn profile(&self, frame: &PyObject, arg: PyObject, event: &str, py: Python) {
        let pyframe = frame.bind(py);
        let pyframe = pyframe
            .downcast::<PyFrame>()
            .expect("Python gives us a PyFrame");
        let f_code = pyframe
            .getattr(intern!(py, "f_code"))
            .expect("A frame always has an `f_code`");
        let co_filename = f_code
            .getattr(intern!(py, "co_filename"))
            .expect("`f_code` always has `co_filename`");
        let co_name = f_code
            .getattr(intern!(py, "co_name"))
            .expect("`f_code` always has `co_name`");
        let filename = co_filename
            .extract::<Cow<str>>()
            .expect("`co_filename` is always a string");
        let name = co_name
            .extract::<Cow<str>>()
            .expect("`co_name` is always a string");

        let mut frames = vec![];
        let mut frame_types = vec![];
        let default_include_frames = self.default_include_frames.get(py).borrow();
        if let Some(processors) = default_include_frames.get(&name.to_string()) {
            for processor in processors.iter() {
                match self.run_frame_processor(py, processor, pyframe, event, &arg, &filename) {
                    Ok(Some((frame_type, data))) => {
                        frames.push(data);
                        frame_types.push(frame_type);
                    }
                    Ok(None) => {}
                    Err(err) => self.log_error(py, err, pyframe, event, &co_filename, &co_name),
                }
            }
        };

        let result = match self.include_frame(pyframe, &filename) {
            true => self.process_frame(pyframe, event, arg, &name, &mut frame_types, &mut frames),
            false => self.push_frames(py, event, &mut frame_types, &mut frames),
        };
        if let Err(err) = result {
            self.log_error(py, err, pyframe, event, &co_filename, &co_name);
        }
    }

    /// Log an unexpected error using Python's logging.
    fn log_error(
        &self,
        py: Python,
        err: PyErr,
        pyframe: &Bound<'_, PyFrame>,
        event: &str,
        co_filename: &Bound<'_, PyAny>,
        co_name: &Bound<'_, PyAny>,
    ) {
        let logging = PyModule::import_bound(py, "logging").unwrap();
        let logger = logging.call_method1("getLogger", ("kolo",)).unwrap();
        let locals = pyframe.getattr(intern!(py, "f_locals")).unwrap();

        let kwargs = PyDict::new_bound(py);
        kwargs.set_item("exc_info", err).unwrap();

        logger
            .call_method(
                "warning",
                (
                    PYTHON_EXCEPTION_WARNING,
                    co_filename,
                    co_name,
                    event,
                    locals,
                ),
                Some(&kwargs),
            )
            .unwrap();
    }
}

const PYTHON_EXCEPTION_WARNING: &str = "Unexpected exception in Rust.
    co_filename: %s
    co_name: %s
    event: %s
    frame locals: %s
";

// Safety:
//
// We match the type signature of `Py_tracefunc`.
//
// https://docs.rs/pyo3-ffi/latest/pyo3_ffi/type.Py_tracefunc.html
/// The low-level callback function that `PyEval_SetProfile` calls into for each event.
///
/// We convert the raw ffi types into nicely behaved safe PyO3 types and then delegate to
/// `KoloProfiler.process` for the main work.
pub extern "C" fn profile_callback(
    _obj: *mut ffi::PyObject,
    _frame: *mut ffi::PyFrameObject,
    what: c_int,
    _arg: *mut ffi::PyObject,
) -> c_int {
    // Exit early if we're not handling a Python `call` or `return` event.
    let event = match what {
        ffi::PyTrace_CALL => "call",
        ffi::PyTrace_RETURN => "return",
        _ => return 0,
    };
    let _frame = _frame as *mut ffi::PyObject;
    Python::with_gil(|py| {
        // Safety:
        //
        // `from_borrowed_ptr_or_err` must be called in an unsafe block.
        //
        // `_obj` is a reference to our `KoloProfiler` wrapped up in a Python object, so
        // we can safely convert it from an `ffi::PyObject` to a `PyObject`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_err
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let obj = match unsafe { PyObject::from_borrowed_ptr_or_err(py, _obj) } {
            Ok(obj) => obj,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };
        let profiler = match obj.extract::<PyRef<KoloProfiler>>(py) {
            Ok(profiler) => profiler,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };

        // Safety:
        //
        // `from_borrowed_ptr_or_err` must be called in an unsafe block.
        //
        // `_frame` is an `ffi::PyFrameObject` which can be converted safely
        // to a `PyObject`. We can later convert it into a `pyo3::types::PyFrame`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_err
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let frame = match unsafe { PyObject::from_borrowed_ptr_or_err(py, _frame) } {
            Ok(frame) => frame,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };

        // Safety:
        //
        // `from_borrowed_ptr_or_opt` must be called in an unsafe block.
        //
        // `_arg` is either a `Py_None` (PyTrace_CALL) or any PyObject (PyTrace_RETURN) or
        // NULL (PyTrace_RETURN). The first two can be unwrapped as a PyObject. `NULL` we
        // convert to a `py.None()`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_opt
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let arg = match unsafe { PyObject::from_borrowed_ptr_or_opt(py, _arg) } {
            Some(arg) => arg,
            // TODO: Perhaps better exception handling here?
            None => py.None(),
        };

        profiler.profile(&frame, arg, event, py);
        0
    })
}
