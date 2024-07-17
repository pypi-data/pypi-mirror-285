from fastapi_cli.cli import app

from .db import db_app

app.add_typer(db_app, name="db")
