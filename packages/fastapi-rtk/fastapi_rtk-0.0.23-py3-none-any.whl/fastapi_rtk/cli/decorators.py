from functools import wraps

import typer
from fastapi_cli.discover import get_import_string
from fastapi_cli.exceptions import FastAPICLIException

from ..globals import g
from .const import logger


def check_existing_app(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            get_import_string(path=g.path)
            return f(*args, **kwargs)
        except FastAPICLIException as e:
            logger.error(str(e))
            raise typer.Exit(code=1) from None

    return wrapper


def set_migrate_mode(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        g.is_migrate = True
        return f(*args, **kwargs)

    return wrapper
