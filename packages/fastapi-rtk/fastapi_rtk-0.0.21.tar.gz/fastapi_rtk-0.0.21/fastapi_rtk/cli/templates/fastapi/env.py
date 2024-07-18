import asyncio
from logging.config import fileConfig

from alembic import context
from fastapi_rtk import DatabaseSessionManager, g, metadata
from sqlalchemy import Connection

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    sqlalchemy_url = g.config.get("SQLALCHEMY_DATABASE_URI")
    if not sqlalchemy_url:
        raise Exception("SQLALCHEMY_DATABASE_URI not found in config")

    alembic_session_manager = DatabaseSessionManager()
    alembic_session_manager.init_db(sqlalchemy_url)

    try:
        engine_url = alembic_session_manager._engine.url.render_as_string(
            hide_password=False
        ).replace("%", "%%")
    except AttributeError:
        engine_url = str(alembic_session_manager._engine.url).replace("%", "%%")
    config.set_main_option("sqlalchemy.url", engine_url)

    async with alembic_session_manager.connect() as connection:
        if isinstance(connection, Connection):
            do_run_migrations(connection)
        else:
            await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
