from __future__ import annotations

import inspect
import logging
import platform
import sys
import threading
import time
import types
from collections import defaultdict
from collections.abc import Mapping
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Protocol, TypeVar, overload

import httpx
import msgpack
import ulid

from .config import load_config
from .db import save_trace_in_sqlite, setup_db
from .filters.attrs import attrs_filter
from .filters.core import (
    FrameFilter,
    FrameProcessor,
    exec_filter,
    frozen_filter,
    get_ignore_frames,
    get_include_frames,
    library_filter,
)
from .filters.kolo import kolo_filter
from .filters.pypy import pypy_filter
from .filters.pytest import pytest_generated_filter
from .git import COMMIT_SHA
from .plugins import PluginProcessor, load_plugin_data
from .serialize import (
    UserCodeCallSite,
    dump_msgpack,
    dump_msgpack_lightweight_repr,
    frame_path,
    monkeypatch_queryset_repr,
    user_code_call_site,
)
from .upload import upload_to_dashboard
from .version import __version__

logger = logging.getLogger("kolo")


class KoloLocals(threading.local):
    def __init__(self):
        self.call_frames = []
        self._frame_ids = {}


INCLUDE_FRAMES_WARNING = """\
Unexpected exception in include_frames: %s
    co_filename: %s
    co_name: %s
    event: %s
    frame locals: %s
"""
IGNORE_FRAMES_WARNING = """\
Unexpected exception in ignore_frames: %s
    co_filename: %s
    co_name: %s
    event: %s
    frame locals: %s
"""
DEFAULT_INCLUDE_FRAMES_WARNING = """\
Unexpected exception in default_include_frames: %s
    co_filename: %s
    co_name: %s
    event: %s
    frame locals: %s
"""
DEFAULT_IGNORE_FRAMES_WARNING = """\
Unexpected exception in default_ignore_frames: %s
    co_filename: %s
    co_name: %s
    event: %s
    frame locals: %s
"""
PROCESS_FRAME_WARNING = """\
Unexpected exception in KoloProfiler.process_frame
    co_filename: %s
    co_name: %s
    event: %s
    frame locals: %s
"""


class KoloProfiler:
    """
    Collect runtime information about code to view in VSCode.

    include_frames can be passed to enable profiling of standard library
    or third party code.

    ignore_frames can also be passed to disable profiling of a user's
    own code.

    The list should contain fragments of the path to the relevant files.
    For example, to include profiling for the json module the include_frames
    could look like ["/json/"].

    The list may also contain frame filters. A frame filter is a function
    (or other callable) that takes the same arguments as the profilefunc
    passed to sys.setprofile and returns a boolean representing whether
    to allow or block the frame.

    include_frames takes precedence over ignore_frames. A frame that
    matches an entry in each list will be profiled.
    """

    def __init__(
        self, db_path: Path, config=None, one_trace_per_test=False, *, source
    ) -> None:
        self.db_path = db_path
        self.source = source
        self.one_trace_per_test = one_trace_per_test
        trace_id = ulid.new()
        self.trace_id = f"trc_{trace_id}"
        self.start_test_index = 0
        self.start_test_indices: Dict[int, int] = {}
        self.frames_of_interest: List[str] = []
        self.frames: defaultdict = defaultdict(list)
        self.config = config if config is not None else {}
        self.include_frames = get_include_frames(config)
        self.ignore_frames = get_ignore_frames(config)

        self.default_include_frames: Dict[str, List[FrameProcessor]] = {}
        for plugin_data in load_plugin_data(self.config):
            processor = PluginProcessor(plugin_data, self.config)
            for co_name in plugin_data["co_names"]:
                self.default_include_frames.setdefault(co_name, []).append(processor)

        self.default_ignore_frames: List[FrameFilter] = [
            library_filter,
            frozen_filter,
            pypy_filter,
            kolo_filter,
            exec_filter,
            attrs_filter,
            pytest_generated_filter,
        ]
        self.thread_locals = KoloLocals()
        self.timestamp = time.time()
        self.rust_profiler = None
        self.use_threading = self.config.get("threading", False)
        self.omit_return_locals = self.config.get("omit_return_locals", False)
        self.main_thread_id = getattr(threading.main_thread(), "native_id", None)
        if self.config.get("lightweight_repr", False):
            self.dump_msgpack = dump_msgpack_lightweight_repr
        else:
            self.dump_msgpack = dump_msgpack

    def __call__(self, frame: types.FrameType, event: str, arg: object) -> None:
        if event in ["c_call", "c_return", "c_exception"]:
            return

        co_name = frame.f_code.co_name

        frames = []
        frame_types = []

        try:
            # Execute only the filters listening for this co_name
            for processor in self.default_include_frames.get(co_name, ()):
                try:
                    if processor(frame, event, arg):
                        frame_data = processor.process(
                            frame, event, arg, self.thread_locals.call_frames
                        )
                        if frame_data:  # pragma: no branch
                            data = self.dump_msgpack(frame_data)
                            frames.append(data)
                            frame_types.append(frame_data["type"])
                except Exception as e:
                    logger.warning(
                        DEFAULT_INCLUDE_FRAMES_WARNING,
                        processor,
                        frame.f_code.co_filename,
                        frame.f_code.co_name,
                        event,
                        frame.f_locals,
                        exc_info=e,
                    )
                    continue

            for frame_filter in self.include_frames:
                try:
                    if frame_filter(frame, event, arg):
                        frames.append(self.process_frame(frame, event, arg))
                        frame_types.append("frame")
                        return
                except Exception as e:
                    logger.warning(
                        INCLUDE_FRAMES_WARNING,
                        frame_filter,
                        frame.f_code.co_filename,
                        frame.f_code.co_name,
                        event,
                        frame.f_locals,
                        exc_info=e,
                    )
                    continue

            for frame_filter in self.default_ignore_frames:
                try:
                    if frame_filter(frame, event, arg):
                        return
                except Exception as e:
                    logger.warning(
                        DEFAULT_IGNORE_FRAMES_WARNING,
                        frame_filter,
                        frame.f_code.co_filename,
                        frame.f_code.co_name,
                        event,
                        frame.f_locals,
                        exc_info=e,
                    )
                    continue

            for frame_filter in self.ignore_frames:
                try:
                    if frame_filter(frame, event, arg):
                        return
                except Exception as e:
                    logger.warning(
                        IGNORE_FRAMES_WARNING,
                        frame_filter,
                        frame.f_code.co_filename,
                        frame.f_code.co_name,
                        event,
                        frame.f_locals,
                        exc_info=e,
                    )
                    continue

            try:
                frames.append(self.process_frame(frame, event, arg))
                frame_types.append("frame")
            except Exception as e:
                logger.warning(
                    PROCESS_FRAME_WARNING,
                    frame.f_code.co_filename,
                    frame.f_code.co_name,
                    event,
                    frame.f_locals,
                    exc_info=e,
                )

        finally:
            if not frames:
                return

            if event == "return":
                frames.reverse()
                frame_types.reverse()

            thread = threading.current_thread()

            if self.one_trace_per_test:  # pragma: no branch
                for index, frame_type in enumerate(frame_types):  # pragma: no cover
                    if frame_type == "start_test":
                        before, frames = frames[:index], frames[index:]

                        if (
                            self.main_thread_id is None
                            or thread.native_id == self.main_thread_id
                        ):
                            self.frames_of_interest.extend(before)
                        else:
                            self.frames[thread.native_id].extend(before)

                        self.start_test()

                    elif frame_type == "end_test":
                        before, frames = frames[: index + 1], frames[index + 1 :]

                        if (
                            self.main_thread_id is None
                            or thread.native_id == self.main_thread_id
                        ):
                            self.frames_of_interest.extend(before)
                        else:
                            self.frames[thread.native_id].extend(before)

                        self.end_test()

            if not self.use_threading or thread.native_id == self.main_thread_id:
                self.frames_of_interest.extend(frames)
            else:
                self.frames[thread.native_id].extend(frames)  # pragma: no cover

    def start_test(self):
        self.trace_id = f"trc_{ulid.new()}"
        self.start_test_index = len(self.frames_of_interest)
        self.start_test_indices = {
            thread_id: len(frames) for thread_id, frames in self.frames.items()
        }

    def end_test(self):
        test_frames = {
            thread_id: frames[self.start_test_indices.get(thread_id, 0) :]
            for thread_id, frames in self.frames.items()
        }
        self.save_request_in_db(
            self.frames_of_interest[self.start_test_index :],
            test_frames,
        )

    def __enter__(self) -> None:
        if self.config.get("use_rust", True):
            try:
                from ._kolo import register_profiler
            except ImportError:
                sys.setprofile(self)
                if self.config.get("threading", False):
                    threading.setprofile(self)
            else:
                register_profiler(self)
        else:
            sys.setprofile(self)
            if self.config.get("threading", False):
                threading.setprofile(self)

    def __exit__(self, *exc) -> None:
        sys.setprofile(None)
        if self.config.get("threading", False):
            threading.setprofile(None)

    def build_trace(self, frames=None, thread_frames=None):
        if self.rust_profiler:
            return self.rust_profiler.build_trace()

        timestamp = self.timestamp
        data = {
            "command_line_args": sys.argv,
            "current_commit_sha": COMMIT_SHA,
            "main_thread_id": self.main_thread_id,
            "meta": {
                "version": __version__,
                "source": self.source,
                "use_frame_boundaries": True,
            },
            "timestamp": timestamp,
            "trace_id": self.trace_id,
        }

        frames = self.frames_of_interest if frames is None else frames
        thread_frames = self.frames if thread_frames is None else thread_frames

        data["frames_of_interest"] = [
            msgpack.unpackb(f, strict_map_key=False) for f in frames
        ]
        data["frames"] = {
            thread_id: [msgpack.unpackb(f, strict_map_key=False) for f in frames]
            for thread_id, frames in thread_frames.items()
        }
        return self.dump_msgpack(data)

    def save_request_in_db(self, frames=None, thread_frames=None) -> None:
        if self.rust_profiler:
            self.rust_profiler.save_request_in_db()
            return

        serialized_data = self.build_trace(frames, thread_frames)
        timeout = self.config.get("sqlite_busy_timeout", 60)
        save_trace_in_sqlite(
            self.db_path, self.trace_id, msgpack=serialized_data, timeout=timeout
        )

    def save_trace_in_thread(self):
        if platform.machine() == "wasm32":
            self.save_request_in_db()
        else:
            name = "kolo-save_request_in_db"
            threading.Thread(target=self.save_request_in_db, name=name).start()

    def upload_trace_in_thread(self, upload_token):
        def upload():
            trace = self.build_trace()
            try:
                response = upload_to_dashboard(trace, upload_token)
                response.raise_for_status()
            except httpx.HTTPError:
                logger.exception("Failed to upload trace to Kolo dashboard.")

        if platform.machine() == "wasm32":
            upload()
        else:
            name = "kolo-upload_to_dashboard"
            threading.Thread(target=upload, name=name).start()

    def process_frame(self, frame: types.FrameType, event: str, arg: object) -> bytes:
        if event == "call":
            frame_id = f"frm_{ulid.new()}"
            self.thread_locals._frame_ids[id(frame)] = frame_id
        elif event == "return":  # pragma: no branch
            frame_id = self.thread_locals._frame_ids[id(frame)]

        user_code_call_site_ = user_code_call_site(
            self.thread_locals.call_frames, frame_id
        )

        if event == "call":
            self.thread_locals.call_frames.append((frame, frame_id))
        elif event == "return":  # pragma: no branch
            self.thread_locals.call_frames.pop()

        thread = threading.current_thread()

        if self.omit_return_locals and event == "return":
            frame_locals = None
        else:
            frame_locals = {
                k: v for k, v in frame.f_locals.items() if k != "__builtins__"
            }
        frame_data = {
            "path": frame_path(frame),
            "co_name": frame.f_code.co_name,
            "qualname": get_qualname(frame),
            "event": event,
            "frame_id": frame_id,
            "arg": arg,
            "locals": frame_locals,
            "thread": thread.name,
            # The operating system's thread ID.
            # Guaranteed to be unique for the lifetime of the thread.
            "thread_native_id": getattr(thread, "native_id", None),
            "timestamp": time.time(),
            "type": "frame",
            "user_code_call_site": user_code_call_site_,
        }
        return self.dump_msgpack(frame_data)


def get_qualname(frame: types.FrameType) -> str | None:
    try:
        qualname = frame.f_code.co_qualname  # type: ignore[attr-defined]
    except AttributeError:
        pass
    else:
        module = frame.f_globals["__name__"]
        return f"{module}.{qualname}"

    co_name = frame.f_code.co_name
    if co_name == "<module>":  # pragma: no cover
        module = frame.f_globals["__name__"]
        return f"{module}.<module>"

    try:
        outer_frame = frame.f_back
        assert outer_frame
        try:
            function = outer_frame.f_locals[co_name]
        except KeyError:
            try:
                self = frame.f_locals["self"]
            except KeyError:
                cls = frame.f_locals.get("cls")
                if isinstance(cls, type):
                    function = inspect.getattr_static(cls, co_name)
                else:
                    try:
                        qualname = frame.f_locals["__qualname__"]
                    except KeyError:
                        function = frame.f_globals[co_name]
                    else:  # pragma: no cover
                        module = frame.f_globals["__name__"]
                        return f"{module}.{qualname}"
            else:
                function = inspect.getattr_static(self, co_name)
                if isinstance(function, property):
                    function = function.fget

        return f"{function.__module__}.{function.__qualname__}"
    except Exception:
        return None


class Enabled:
    def __init__(self, config: Mapping[str, Any] | None = None):
        if config is None:
            config = {}
        self.config = load_config(config)
        self._profiler: KoloProfiler | None = None
        self._monitor = None

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner

    def __enter__(self) -> None:
        use_monitoring = self.config.get("use_monitoring", False)

        if sys.version_info < (3, 12) or not use_monitoring:
            if sys.getprofile():
                return

            if self.config.get("threading", False):
                try:
                    thread_profiler = threading.getprofile()  # type: ignore[attr-defined]
                except AttributeError:
                    thread_profiler = threading._profile_hook
                if thread_profiler:
                    return

        db_path = setup_db()
        monkeypatch_queryset_repr()

        if sys.version_info >= (3, 12) and use_monitoring:
            from .monitoring import KoloMonitor

            monitor = KoloMonitor(db_path, config=self.config, source="kolo.enable")
            monitor.monitor()
            if monitor.active:
                self._monitor = monitor
        else:
            self._profiler = KoloProfiler(
                db_path, config=self.config, source="kolo.enable"
            )
            self._profiler.__enter__()

    def __exit__(self, *exc) -> None:
        if self._profiler is not None:
            self._profiler.__exit__(*exc)
            self._profiler.save_request_in_db()
            self._profiler = None

        if self._monitor is not None:
            self._monitor.disable()
            self._monitor.save()
            self._monitor = None


F = TypeVar("F", bound=Callable[..., Any])


class CallableContextManager(Protocol):
    def __call__(self, func: F) -> F: ...  # pragma: no cover

    def __enter__(self) -> None: ...  # pragma: no cover

    def __exit__(self, *exc) -> None: ...  # pragma: no cover


@overload
def enable(_func: F) -> F:
    """Stub"""


@overload
def enable(config: Mapping[str, Any] | None = None) -> CallableContextManager:
    """Stub"""


def enable(config=None):
    if config is None or isinstance(config, Mapping):
        return Enabled(config)
    # Treat as a decorator called on a function
    return Enabled()(config)


enabled = enable
