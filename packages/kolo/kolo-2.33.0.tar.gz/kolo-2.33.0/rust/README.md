# The Rust extension

In Kolo we have a parallel implementation of `KoloProfiler` in Rust to reduce the overhead of the CPython interpreter.

The Rust codebase is split into several files:

* `lib.rs` - This is where we define the `kolo._kolo` module that can be imported by Python. This contains two functions, `register_profiler` and `register_noop_profiler` which can be called directly by Python code.
* `profiler.rs` - This is where the core profiling logic lives. The `KoloProfiler` struct is analogous to the `KoloProfiler` class in `src/kolo/profiler.py`. The `profile_callback` function is a thin layer to convert CPython types into Rust-friendly types.
* `plugins.rs` - This module contains the implementation of the plugin architecture for `default_include_frames`. The `PluginProcessor` struct is analogous to the `PluginProcessor` class in `src/kolo/plugins.py`.
* `filters.rs` - This module contains the implementation of the filtering logic for `default_ignore_frames`.
* `utils.rs` - This module contains various helper functions.
