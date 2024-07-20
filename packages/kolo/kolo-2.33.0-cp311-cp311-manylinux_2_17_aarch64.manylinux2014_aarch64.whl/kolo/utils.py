import subprocess
import sys
from tempfile import NamedTemporaryFile


def pretty_byte_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes:5d} B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    bit_length = size_bytes.bit_length() - 1
    index = bit_length // 10
    denominator = 1 << (10 * index)
    ratio = size_bytes / denominator
    return f"{ratio:5.1f} {size_name[index]}"


def maybe_format(rendered):
    rendered = maybe_isort(rendered)

    try:
        import ruff
    except ImportError:
        if len(rendered) <= 1_000_000:
            rendered = maybe_black(rendered)
        return rendered

    with NamedTemporaryFile("w+", delete=False) as f:
        f.write(rendered)
        name = f.name

    subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            name,
            "--config",
            "format.skip-magic-trailing-comma=true",
        ],
        check=True,
    )
    with open(name) as f:
        rendered = f.read()

    return rendered


def maybe_black(rendered):
    try:
        from black import format_file_contents
        from black.mode import Mode
        from black.parsing import InvalidInput
        from black.report import NothingChanged
    except ImportError:
        return rendered

    try:
        return format_file_contents(
            rendered, fast=True, mode=Mode(magic_trailing_comma=False)
        )
    except (InvalidInput, NothingChanged):
        return rendered


def maybe_isort(rendered):
    try:
        from isort.api import sort_code_string
    except ImportError:
        return rendered
    return sort_code_string(rendered)


def get_terminal_formatter(mode):
    if mode == "off":
        return None

    import os

    from pygments.formatters import (
        Terminal256Formatter,
        TerminalFormatter,
        TerminalTrueColorFormatter,
    )

    style = "monokai" if mode == "dark" else "default"

    # Derived from https://github.com/pygments/pygments/blob/e49aef678a5ce40b6ed7b38cd71dddafc12f979c/pygments/cmdline.py#L448-L453
    if os.environ.get("COLORTERM", "") in ("truecolor", "24bit"):
        return TerminalTrueColorFormatter(style=style)
    if "256" in os.environ.get("TERM", ""):
        return Terminal256Formatter(style=style)
    return TerminalFormatter(bg=mode)


def get_sql_lexer(dialect):
    from pygments.lexers import MySqlLexer, PostgresLexer, SqlLexer

    if dialect == "postgres":
        return PostgresLexer()
    if dialect == "mysql":
        return MySqlLexer()
    return SqlLexer()


def highlight_sql(query, dialect, formatter):
    if formatter is None:
        # pygments adds an extra newline while highlighting.
        # Since this looks better, we also add one ourselves here.
        return query + "\n"

    from pygments import highlight

    return highlight(query, get_sql_lexer(dialect), formatter)


def highlight_python(code, formatter):
    from pygments import highlight
    from pygments.lexers import PythonLexer

    return highlight(code, PythonLexer(), formatter)
