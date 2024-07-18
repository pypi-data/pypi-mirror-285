import os

import typer
from alembic import command
from alembic.config import Config as AlembicConfig
from rich import print

from ..globals import g
from ..version import __version__
from .decorators import check_existing_app


class Config(AlembicConfig):
    def __init__(self, *args, **kwargs):
        self.template_directory = kwargs.pop("template_directory", None)
        super().__init__(*args, **kwargs)

    def get_template_directory(self):
        if self.template_directory:
            return self.template_directory
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, "templates")


def version_callback(value: bool) -> None:
    if value:
        print(f"FastAPI DB CLI version: [green]{__version__}[/green]")
        raise typer.Exit()


def set_path(value: str | None) -> None:
    g.path = value


def list_templates():
    config = Config()
    config.print_stdout("Available templates:\n")
    for tempname in sorted(os.listdir(config.get_template_directory())):
        with open(
            os.path.join(config.get_template_directory(), tempname, "README")
        ) as readme:
            synopsis = next(readme).strip()
        config.print_stdout("%s - %s", tempname, synopsis)


def init(
    directory: str = "migrations",
    multidb: bool = False,
    template: str = "fastapi",
    package: bool = False,
):
    template_directory = None
    if "/" in template or "\\" in template:
        template_directory, template = os.path.split(template)
    config = Config(template_directory=template_directory)
    config.set_main_option("script_location", directory)
    config.config_file_name = os.path.join(directory, "alembic.ini")
    # TODO: Fix this
    # config = current_app.extensions["migrate"].migrate.call_configure_callbacks(config)
    if multidb and template == "fastapi":
        template = "fastapi-multidb"
    command.init(config, directory, template=template, package=package)


@check_existing_app
def revision(
    directory: str = "migrations",
    message: str = "",
    autogenerate: bool = False,
    sql: bool = False,
    head: str = "head",
    splice: bool = False,
    branch_label: str = None,
    version_path: str = None,
    rev_id: str = None,
):
    opts = ["autogenerate"] if autogenerate else None
    config = Config()
    config.set_main_option("script_location", directory)
    config.cmd_opts = opts
    # config = current_app.extensions["migrate"].migrate.get_config(directory, opts=opts)
    command.revision(
        config,
        message,
        autogenerate=autogenerate,
        sql=sql,
        head=head,
        splice=splice,
        branch_label=branch_label,
        version_path=version_path,
        rev_id=rev_id,
    )


def migrate(
    directory: str = "migrations",
    message: str = "",
    sql: bool = False,
    head: str = "head",
    splice: bool = False,
    branch_label: str = None,
    version_path: str = None,
    rev_id: str = None,
):
    return revision(
        directory=directory,
        message=message,
        autogenerate=True,
        sql=sql,
        head=head,
        splice=splice,
        branch_label=branch_label,
        version_path=version_path,
        rev_id=rev_id,
    )


@check_existing_app
def edit(
    directory: str = "migrations",
    revision: str = "current",
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.edit(config, revision)


def merge(
    directory: str = "migrations",
    revisions: str = "",
    message: str = "",
    branch_label: str = None,
    rev_id: str = None,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.merge(
        config,
        revisions,
        message=message,
        branch_label=branch_label,
        rev_id=rev_id,
    )


@check_existing_app
def upgrade(
    directory: str = "migrations",
    revision: str = "head",
    sql: bool = False,
    tag: str = None,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.upgrade(config, revision, sql=sql, tag=tag)


@check_existing_app
def downgrade(
    directory: str = "migrations",
    revision: str = "-1",
    sql: bool = False,
    tag: str = None,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.downgrade(config, revision, sql=sql, tag=tag)


def show(directory: str = "migrations", revision: str = "head"):
    config = Config()
    config.set_main_option("script_location", directory)
    command.show(config, revision)


def history(
    directory: str = "migrations",
    rev_range: str = None,
    verbose: bool = False,
    indicate_current: bool = False,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.history(
        config, rev_range, verbose=verbose, indicate_current=indicate_current
    )


def heads(
    directory: str = "migrations",
    verbose: bool = False,
    resolve_dependencies: bool = False,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.heads(config, verbose=verbose, resolve_dependencies=resolve_dependencies)


@check_existing_app
def branches(
    directory: str = "migrations",
    verbose: bool = False,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.branches(config, verbose=verbose)


@check_existing_app
def current(directory: str = "migrations", verbose: bool = False):
    config = Config()
    config.set_main_option("script_location", directory)
    command.current(config, verbose=verbose)


@check_existing_app
def stamp(
    directory: str = "migrations",
    revision: str = "head",
    sql: bool = False,
    tag: str = None,
    purge: bool = False,
):
    config = Config()
    config.set_main_option("script_location", directory)
    command.stamp(config, revision, sql=sql, tag=tag, purge=purge)


@check_existing_app
def check(directory: str = "migrations"):
    config = Config()
    config.set_main_option("script_location", directory)
    command.check(config)
