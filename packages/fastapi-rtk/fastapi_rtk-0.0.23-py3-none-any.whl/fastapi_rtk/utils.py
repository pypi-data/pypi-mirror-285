import csv
import inspect
import logging
import os
import re
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Dict, Type, Union

from fastapi import Depends, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, create_model
from starlette.concurrency import P, T

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_windows_device_files = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(10)),
    *(f"LPT{i}" for i in range(10)),
}

log = logging.getLogger(__name__)


class Line(object):
    def __init__(self):
        self._line = None

    def write(self, line):
        self._line = line

    def read(self):
        return self._line


async def generate_report(data, list_columns, label_columns):
    line = Line()
    writer = csv.writer(line, delimiter=",")

    # header
    labels = []
    for key in list_columns:
        labels.append(label_columns[key])

    # rows
    writer.writerow(labels)
    yield line.read()

    async for chunk in data:
        for item in chunk:
            row = []
            for key in list_columns:
                value = getattr(item, key)
                # if value is a function, call it
                if callable(value):
                    try:
                        value = value()
                    except Exception as e:
                        value = "Error calling function"
                if value is None:
                    value = ""
                row.append(str(value))
            writer.writerow(row)
            yield line.read()


def merge_schema(
    schema: BaseModel,
    fields: Dict[str, tuple[type, Field]],
    only_update=False,
    name: str | None = None,
) -> Type[BaseModel]:
    """
    Replace or add fields to the given schema.

    Args:
        schema (BaseModel): The schema to be updated.
        fields (Dict[str, tuple[type, Field]]): The fields to be added or updated.
        only_update (bool): If True, only update the fields with the same name. Otherwise, add new fields.
        name (str, optional): The name of the new schema. Defaults to None.

    Returns:
        BaseModel: The updated schema.
    """
    name = name or schema.__name__
    new_fields = dict()
    if only_update:
        for key, value in schema.model_fields.items():
            if key in fields:
                val = fields[key]
                if isinstance(val, tuple):
                    new_fields[key] = val
                else:
                    new_fields[key] = (value.annotation, val)
    else:
        new_fields = fields

    return create_model(
        name,
        **new_fields,
        __base__=schema,
    )


def update_self_signature(cls, f):
    """
    Update the signature of a function to replace the first parameter with 'self' as a dependency.

    Args:
        cls (class): The class that the function belongs to.
        f (function): The function to be updated.

    Returns:
        None
    """
    # Get the function's parameters
    old_signature = inspect.signature(f)
    old_parameters = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]

    # If the first parameter is self, replace it
    if old_first_parameter.name == "self":
        new_first_parameter = old_first_parameter.replace(default=Depends(lambda: cls))

        new_parameters = [new_first_parameter] + [
            parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
            for parameter in old_parameters[1:]
        ]
        new_signature = old_signature.replace(parameters=new_parameters)

        setattr(
            f, "__signature__", new_signature
        )  # Set the new signature to the function


def uuid_namegen(file_data: UploadFile) -> str:
    """
    Generates a unique filename by combining a UUID and the original filename.

    Args:
        file_data (File): The file data object.

    Returns:
        str: The generated unique filename.
    """
    return str(uuid.uuid1()) + "_sep_" + file_data.filename


def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    for sep in os.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename


def ensure_tz_info(dt: datetime) -> datetime:
    """Ensure that the datetime has a timezone info."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def validate_utc(dt: datetime) -> datetime:
    """Validate that the datetime is in UTC."""
    if dt.tzinfo.utcoffset(dt) != timezone.utc.utcoffset(dt):
        raise ValueError("Timezone must be UTC")
    return dt


async def smart_run(
    func: Callable[P, Union[T, Awaitable[T]]], *args: P.args, **kwargs: P.kwargs
) -> T:
    """
    A utility function that can run a function either as a coroutine or in a threadpool.

    Args:
        func: The function to be executed.
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        The result of the function execution.

    Raises:
        Any exceptions raised by the function.

    """
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return await run_in_threadpool(func, *args, **kwargs)


async def safe_call(coro: Awaitable[T] | T) -> T:
    """
    A utility function that can await a coroutine or return a non-coroutine object.

    Args:
        coro (Any): The function call or coroutine to be awaited.

    Returns:
        The result of the function call or coroutine.
    """
    if isinstance(coro, Coroutine):
        return await coro
    return coro


class ImportStringError(ImportError):
    """
    COPIED FROM WERKZEUG LIBRARY

    Provides information about a failed :func:`import_string` attempt.
    """

    #: String in dotted notation that failed to be imported.
    import_name: str
    #: Wrapped exception.
    exception: BaseException

    def __init__(self, import_name: str, exception: BaseException) -> None:
        self.import_name = import_name
        self.exception = exception
        msg = import_name
        name = ""
        tracked = []
        for part in import_name.replace(":", ".").split("."):
            name = f"{name}.{part}" if name else part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, getattr(imported, "__file__", None)))
            else:
                track = [f"- {n!r} found in {i!r}." for n, i in tracked]
                track.append(f"- {name!r} not found.")
                track_str = "\n".join(track)
                msg = (
                    f"import_string() failed for {import_name!r}. Possible reasons"
                    f" are:\n\n"
                    "- missing __init__.py in a package;\n"
                    "- package or module path not included in sys.path;\n"
                    "- duplicated package or module name taking precedence in"
                    " sys.path;\n"
                    "- missing module, class, function or variable;\n\n"
                    f"Debugged import:\n\n{track_str}\n\n"
                    f"Original exception:\n\n{type(exception).__name__}: {exception}"
                )
                break

        super().__init__(msg)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}({self.import_name!r}, {self.exception!r})>"


def import_string(import_name: str, silent: bool = False) -> Any:
    """
    COPIED FROM WERKZEUG LIBRARY

    Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    import_name = import_name.replace(":", ".")
    try:
        try:
            __import__(import_name)
        except ImportError:
            if "." not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit(".", 1)
        module = __import__(module_name, globals(), locals(), [obj_name])
        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e) from None

    except ImportError as e:
        if not silent:
            raise ImportStringError(import_name, e).with_traceback(
                sys.exc_info()[2]
            ) from None

    return None


def ignore_in_migrate(f):
    """
    Decorator that can be used to ignore a function during database migrations.

    This decorator can be applied to a function to prevent it from being executed
    when the application is running in migration mode. It checks the value of the
    `g.is_migrate` flag and returns immediately if it is set to True.

    Args:
        f: The function to be decorated.

    Returns:
        The decorated function.

    Example:
        @ignore_in_migrate
        def my_function():
            # This function will not be executed during database migrations.
            pass
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        from .globals import g

        if g.is_migrate:
            return
        return f(*args, **kwargs)

    return wrapper
