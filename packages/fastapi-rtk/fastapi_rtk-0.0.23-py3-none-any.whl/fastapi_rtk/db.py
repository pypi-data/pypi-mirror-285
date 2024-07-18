import contextlib
import inspect
import json
from typing import Any, Dict, List, Literal, Optional, Type, overload

from fastapi import Depends, HTTPException
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.models import ID, OAP, UP
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import Column, Engine, Select, create_engine, func, select
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, joinedload, selectinload, sessionmaker
from sqlalchemy.sql import Select

from .const import logger
from .filters import BaseFilter
from .model import metadata, metadatas
from .models import Model, OAuthAccount, User
from .schemas import PRIMARY_KEY, FilterSchema
from .utils import safe_call, smart_run


class UserDatabase(SQLAlchemyUserDatabase):
    """
    Modified version of the SQLAlchemyUserDatabase class from fastapi_users_db_sqlalchemy.
    - Allow the use of both async and sync database connections.
    - Allow the use of get_by_username method to get a user by username.

    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    :param oauth_account_table: Optional SQLAlchemy OAuth accounts model.
    """

    session: AsyncSession | Session

    def __init__(
        self,
        session: AsyncSession | Session,
        user_table: type,
        oauth_account_table: type[SQLAlchemyBaseOAuthAccountTable] | None = None,
    ):
        super().__init__(session, user_table, oauth_account_table)

    async def get(self, id: ID) -> Optional[UP]:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UP]:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        statement = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth)
            .where(self.oauth_account_table.account_id == account_id)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: Dict[str, Any]) -> UP:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await safe_call(self.session.commit())
        await safe_call(self.session.refresh(user))
        return user

    async def update(self, user: UP, update_dict: Dict[str, Any]) -> UP:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await safe_call(self.session.commit())
        await safe_call(self.session.refresh(user))
        return user

    async def delete(self, user: UP) -> None:
        await self.session.delete(user)
        await safe_call(self.session.commit())

    async def add_oauth_account(self, user: UP, create_dict: Dict[str, Any]) -> UP:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        await safe_call(self.session.refresh(user))
        oauth_account = self.oauth_account_table(**create_dict)
        self.session.add(oauth_account)
        user.oauth_accounts.append(oauth_account)
        self.session.add(user)

        await safe_call(self.session.commit())

        return user

    async def update_oauth_account(
        self, user: UP, oauth_account: OAP, update_dict: Dict[str, Any]
    ) -> UP:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        for key, value in update_dict.items():
            setattr(oauth_account, key, value)
        self.session.add(oauth_account)
        await safe_call(self.session.commit())

        return user

    async def get_by_username(self, username: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        )
        return await self._get_user(statement)

    async def _get_user(self, statement: Select) -> Optional[UP]:
        results = await smart_run(self.session.execute, statement)
        return results.unique().scalar_one_or_none()


class QueryManager:
    """
    A class that manages the execution of queries on a database.
    """

    db: AsyncSession | Session
    datamodel: Any
    stmt: Select
    _joined_columns: list[Model]

    def __init__(self, db: AsyncSession | Session, datamodel: Any):
        self.db = db
        self.datamodel = datamodel
        self._init_query()

        if not self.db:
            raise Exception("No database connection provided.")

    async def add_options(
        self,
        *,
        join_columns: list[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
        order_column: str | None = None,
        order_direction: str | None = None,
        where: tuple[str, Any] | None = None,
        where_in: tuple[str, list[Any]] | None = None,
        where_id: PRIMARY_KEY | None = None,
        where_id_in: list[PRIMARY_KEY] | None = None,
        filters: list[FilterSchema] | None = None,
        filter_classes: list[tuple[str, BaseFilter, Any]] | None = None,
    ):
        """
        Adds options for pagination and ordering to the query.

        Args:
            join_columns (list[str], optional): The list of columns to join. Use attribute from the model itself. Defaults to [].
            page (int): The page number. If None, no pagination is applied. Defaults to None.
            page_size (int): The number of items per page. If None, no pagination is applied. Defaults to None.
            order_column (str | None): The column to order by. If None, no ordering is applied. Defaults to None.
            order_direction (str | None): The direction of the ordering. If None, no ordering is applied. Defaults to None.
            where (tuple[str, Any], optional): The column name and value to apply the WHERE clause on. Defaults to None.
            where_in (tuple[str, list[Any]], optional): The column name and list of values to apply the WHERE IN clause on. Defaults to None.
            where_id (PRIMARY_KEY, optional): The primary key value to apply the WHERE clause on. Defaults to None.
            where_id_in (list[PRIMARY_KEY], optional): The list of primary key values to apply the WHERE IN clause on. Defaults to None.
            filters (list[FilterSchema], optional): The list of filters to apply to the query. Defaults to [].
            filter_classes (list[tuple[str, BaseFilter, Any]], optional): The list of filter classes to apply to the query. Defaults to [].
        """
        if join_columns:
            for col in join_columns:
                self.join(col)
        if page is not None and page_size is not None:
            self.page(page, page_size)
        if order_column and order_direction:
            self.order_by(order_column, order_direction)
        if where:
            self.where(*where)
        if where_in:
            self.where_in(*where_in)
        if where_id:
            self.where_id(where_id)
        if where_id_in:
            self.where_id_in(where_id_in)
        if filters:
            for filter in filters:
                await safe_call(self.filter(filter))
        if filter_classes:
            for col, filter_class, value in filter_classes:
                await safe_call(self.filter_class(col, filter_class, value))

    def join(self, column: str):
        """
        Joins a column in the query.

        Args:
            column (str): The column to join.

        Returns:
            None
        """
        col = getattr(self.datamodel.obj, column)
        if self.datamodel.is_relation_one_to_one(
            column
        ) or self.datamodel.is_relation_many_to_one(column):
            self.stmt = self.stmt.options(joinedload(col))
            return

        self.stmt = self.stmt.options(selectinload(col))

    def page(self, page: int, page_size: int):
        """
        Paginates the query results.

        Args:
            page (int): The page number.
            page_size (int): The number of items per page.

        Returns:
            None
        """
        self.stmt = self.stmt.offset(page * page_size).limit(page_size)

    def order_by(self, column: str, direction: str):
        """
        Orders the query results by a specific column.

        Args:
            column (str): The column to order by.
            direction (str): The direction of the ordering.

        Returns:
            None
        """
        col = column

        #! If the order column comes from a request, it will be in the format ClassName.column_name
        if col.startswith(self.datamodel.obj.__class__.__name__):
            col = col.split(".", 1)[1]

        # if there is . in the column name, it means it is a relation column
        if "." in col:
            col = self._join_column(col)
        else:
            col = getattr(self.datamodel.obj, col)
        if direction == "asc":
            self.stmt = self.stmt.order_by(col)
        else:
            self.stmt = self.stmt.order_by(col.desc())

    def where(self, column: str, value: Any):
        """
        Apply a WHERE clause to the query.

        Args:
            column (str): The column name to apply the WHERE clause on.
            value (Any): The value to compare against in the WHERE clause.
        """
        column = getattr(self.datamodel.obj, column)
        self.stmt = self.stmt.where(column == value)

    def where_in(self, column: str, values: list[Any]):
        """
        Apply a WHERE IN clause to the query.

        Args:
            column (str): The column name to apply the WHERE IN clause on.
            values (list[Any]): The list of values to compare against in the WHERE IN clause.
        """
        column = getattr(self.datamodel.obj, column)
        self.stmt = self.stmt.where(column.in_(values))

    def where_id(self, id: PRIMARY_KEY):
        """
        Adds a WHERE clause to the query based on the primary key.

        Parameters:
        - id: The primary key value to filter on.
        """
        pk_dict = self._convert_id_into_dict(id)
        for col, val in pk_dict.items():
            self.where(col, val)

    def where_id_in(self, ids: list[PRIMARY_KEY]):
        """
        Filters the query by a list of primary key values.

        Args:
            ids (list): A list of primary key values.

        Returns:
            None
        """
        to_apply_dict = {}
        for id in self.datamodel.get_pk_attrs():
            to_apply_dict[id] = []

        pk_dicts = [self._convert_id_into_dict(id) for id in ids]
        for pk_dict in pk_dicts:
            for col, val in pk_dict.items():
                to_apply_dict[col].append(val)

        for col, vals in to_apply_dict.items():
            self.where_in(col, vals)

    async def filter(self, filter: FilterSchema):
        """
        Apply a filter to the query.

        Args:
            filter (FilterSchema): The filter to apply to the query.
        """
        filter_classes = self.datamodel._filters.get(filter.col)
        filter_class = None
        for f in filter_classes:
            if f.arg_name == filter.opr:
                filter_class = f
                break
        if not filter_class:
            raise HTTPException(
                status_code=400, detail=f"Invalid filter opr: {filter.opr}"
            )

        col = getattr(self.datamodel.obj, filter.col)
        value = filter.value

        # If it is a relation column, we need to join the relation
        if self.datamodel.is_relation(filter.col):
            rel_interface = self.datamodel.get_related_interface(filter.col)
            query = QueryManager(self.db, rel_interface)
            if isinstance(value, list):
                query.where_id_in(value)
                value = await smart_run(query.execute)
            else:
                query.where_id(value)
                value = await smart_run(query.execute, many=False)

        await self._apply_filter(filter_class, self.stmt, col, value)

    async def filter_class(self, col: str, filter_class: BaseFilter, value: Any):
        """
        Apply a filter class to the query.

        Args:
            col (str): The column to apply the filter class on.
            filter_class (BaseFilter): The filter class to apply to the query.
            value (Any): The value to compare against in the filter class.
        """
        # If there is . in the column name, it means it should filter on a related table
        if "." in col:
            col = self._join_column(col)
        else:
            col = getattr(self.datamodel.obj, col)

        await self._apply_filter(filter_class, self.stmt, col, value)

    def add(self, item: Model):
        """
        Add an item to the query.

        Args:
            item (Model): The item to add to the query.
        """
        self.db.add(item)

    async def delete(self, item: Model):
        """
        Delete an item from the query.

        Args:
            item (Model): The item to delete from the query.
        """
        await safe_call(self.db.delete(item))

    async def commit(self):
        """
        Commits the current transaction to the database.

        If an integrity error occurs during the commit, the transaction is rolled back
        and an HTTPException with status code 400 is raised, including the error details.

        Returns:
            None
        """
        try:
            await safe_call(self.db.commit())
        except IntegrityError as e:
            await safe_call(self.db.rollback())
            raise HTTPException(status_code=409, detail=f"Integrity error: {str(e)}")
        finally:
            self._init_query()

    async def count(
        self,
        filters: list[FilterSchema] | None = None,
        filter_classes: list[tuple[str, BaseFilter, Any]] | None = None,
    ) -> int:
        """
        Counts the number of records in the database table.
        The query is reset before and after execution.

        Args:
            filters (list[FilterSchema], optional): The list of filters to apply to the query. Defaults to [].
            filter_classes (list[tuple[str, BaseFilter, Any]], optional): The list of filter classes to apply to the query. Defaults to [].

        Returns:
            int: The number of records in the table.
        """
        try:
            self._init_query()
            if filters:
                for filter in filters:
                    await safe_call(self.filter(filter))
            if filter_classes:
                for col, filter_class, value in filter_classes:
                    await safe_call(self.filter_class(col, filter_class, value))
            stmt = select(func.count()).select_from(self.stmt.subquery())
            result = await smart_run(self.db.scalar, stmt)
            return result or 0
        finally:
            self._init_query()

    @overload
    async def execute(self, many: Literal[True]) -> List[Model]: ...
    @overload
    async def execute(self, many: Literal[False]) -> Model | None: ...
    async def execute(self, many=True) -> Model | list[Model] | None:
        """
        Executes the database query using the provided db.
        After execution, the query is reset to its initial state.

        Args:
            many (bool, optional): Indicates whether the query should return multiple results or just the first result. Defaults to True.

        Returns:
            Model | list[Model] | None: The result of the query.

        Raises:
            Exception: If an error occurs during query execution.
        """
        try:
            logger.debug(f"Executing query: {self.stmt}")
            result = await smart_run(self.db.scalars, self.stmt)
            if many:
                return result.all()

            return result.first()
        except IntegrityError as e:
            await safe_call(self.db.rollback())
            raise HTTPException(status_code=409, detail=str(e))
        finally:
            self._init_query()

    async def yield_per(self, page_size: int):
        """
        Executes the database query using the provided db and yields results in batches of the specified size.
        After execution, the query is reset to its initial state.

        Note: PLEASE ALWAYS CLOSE THE DB AFTER USING THIS METHOD

        Args:
            page_size (int): The number of items to yield per batch.

        Returns:
            Generator[Sequence, None, None]: A generator that yields results in batches of the specified size.
        """
        try:
            self.stmt = self.stmt.execution_options(stream_results=True)
            if isinstance(self.db, AsyncSession):
                result = await self.db.stream(self.stmt)
                result = result.scalars()
            else:
                result = self.db.scalars(self.stmt)
            while True:
                chunk = await smart_run(result.fetchmany, page_size)
                if not chunk:
                    break
                yield chunk
        finally:
            self._init_query()

    def _init_query(self):
        self.stmt = select(self.datamodel.obj)
        self._joined_columns = []

    def _convert_id_into_dict(self, id: PRIMARY_KEY) -> dict[str, Any]:
        """
        Converts the given ID into a dictionary format.

        Args:
            id (PRIMARY_KEY): The ID to be converted.

        Returns:
            dict[str, Any]: The converted ID in dictionary format.

        Raises:
            HTTPException: If the ID is invalid.
        """
        pk_dict = {}
        if self.datamodel.is_pk_composite():
            try:
                # Assume the ID is a JSON string
                id = json.loads(id) if isinstance(id, str) else id
                for col, val in id.items():
                    pk_dict[col] = val
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid ID")
        else:
            pk_dict[self.datamodel.get_pk_attr()] = id

        return pk_dict

    def _join_column(self, col: str) -> Column:
        """
        Joins a related model and returns the specified column.

        Args:
            col (str): The column to join in the format 'relation.column'.

        Returns:
            Column: The related column.

        Raises:
            ValueError: If the specified relation does not exist in the datamodel.
        """
        rel, col = col.split(".")
        rel_obj = self.datamodel.get_related_model(rel)
        if rel_obj not in self._joined_columns:
            self.stmt = self.stmt.join(rel_obj)
            self._joined_columns.append(rel_obj)
        col = getattr(rel_obj, col)
        return col

    async def _apply_filter(
        self, cls: Type[BaseFilter], stmt: Select, col: Column, value: Any
    ):
        """
        Helper method to apply a filter class.
        """
        if cls.is_heavy:
            self.stmt = await smart_run(cls.apply, self.stmt, col, value)
            return

        self.stmt = await safe_call(cls.apply(self.stmt, col, value))


class DatabaseSessionManager:

    _engine: AsyncEngine | Engine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | sessionmaker[Session] | None = (
        None
    )
    _engine_binds: dict[str, AsyncEngine | Engine] = None
    _sessionmaker_binds: dict[
        str, async_sessionmaker[AsyncSession] | sessionmaker[Session]
    ] = None

    def init_db(self, url: str, binds: dict[str, str] | None = None):
        """
        Initializes the database engine and session maker.

        Args:
            url (str): The URL of the database.
            binds (dict[str, str] | None, optional): Additional database URLs to bind to. Defaults to None.
        """
        self._engine = self._init_engine(url)
        self._sessionmaker = self._init_sessionmaker(self._engine)

        if binds:
            self._engine_binds = {}
            self._sessionmaker_binds = {}
            for key, value in binds.items():
                self._engine_binds[key] = self._init_engine(value)
                self._sessionmaker_binds[key] = self._init_sessionmaker(
                    self._engine_binds[key]
                )

    async def close(self):
        """
        If engine exists, disposes the engine and sets it to None.

        If engine binds exist, disposes all engine binds and sets them to None.
        """
        if self._engine:
            await safe_call(self._engine.dispose())
            self._engine = None
            self._sessionmaker = None

        if self._engine_binds:
            for engine in self._engine_binds.values():
                await safe_call(engine.dispose())
            self._engine_binds = None
            self._sessionmaker_binds = None

    @contextlib.asynccontextmanager
    async def connect(self, bind: str | None = None):
        """
        Establishes a connection to the database.

        ***EVEN IF THE CONNECTION IS SYNC, ASYNC WITH ... AS ... IS STILL NEEDED.***

        Args:
            bind (str, optional): The database URL to bind to. If none, the default database is used. Defaults to None.

        Raises:
            Exception: If the DatabaseSessionManager is not initialized.

        Yields:
            AsyncConnection | Connection: The database connection.
        """
        if bind:
            if self._engine_binds is None:
                raise Exception("DatabaseSessionManager is not initialized")
            if isinstance(self._engine_binds[bind], AsyncEngine):
                async with self._engine_binds[bind].begin() as connection:
                    try:
                        yield connection
                    except Exception:
                        await connection.rollback()
                        raise
            else:
                with self._engine_binds[bind].begin() as connection:
                    try:
                        yield connection
                    except Exception:
                        connection.rollback()
                        raise
        else:
            if self._engine is None:
                raise Exception("DatabaseSessionManager is not initialized")
            if isinstance(self._engine, AsyncEngine):
                async with self._engine.begin() as connection:
                    try:
                        yield connection
                    except Exception:
                        await connection.rollback()
                        raise
            else:
                with self._engine.begin() as connection:
                    try:
                        yield connection
                    except Exception:
                        connection.rollback()
                        raise

    @contextlib.asynccontextmanager
    async def session(self, bind: str | None = None):
        """
        Provides a database session for performing database operations.

        ***EVEN IF THE SESSION IS SYNC, ASYNC WITH ... AS ... IS STILL NEEDED.***

        Args:
            bind (str, optional): The database URL to bind to. If none, the default database is used. Defaults to None.

        Raises:
            Exception: If the DatabaseSessionManager is not initialized.

        Yields:
            AsyncSession | Session: The database session.

        Returns:
            None
        """
        if bind:
            if self._sessionmaker_binds is None:
                raise Exception("DatabaseSessionManager is not initialized")
            session = self._sessionmaker_binds[bind]()
            try:
                yield session
            except Exception:
                await safe_call(session.rollback())
                raise
            finally:
                await safe_call(session.close())
        else:
            if self._sessionmaker is None:
                raise Exception("DatabaseSessionManager is not initialized")
            session = self._sessionmaker()
            try:
                yield session
            except Exception:
                await safe_call(session.rollback())
                raise
            finally:
                await safe_call(session.close())

    # Used for testing
    async def create_all(self, binds: list[str] | Literal["all"] | None = "all"):
        """
        Creates all tables in the database.

        Args:
            binds (list[str] | Literal["all"] | None, optional): The database URLs to create tables in. Defaults to "all".
        """
        async with self.connect() as connection:
            if isinstance(connection, AsyncConnection):
                await connection.run_sync(metadata.create_all)
            else:
                metadata.create_all(connection)

        if not self._engine_binds or not binds:
            return

        bind_keys = self._engine_binds.keys() if binds == "all" else binds
        for key in bind_keys:
            async with self.connect(key) as connection:
                if isinstance(connection, AsyncConnection):
                    await connection.run_sync(metadatas[key].create_all)
                else:
                    metadatas[key].create_all(connection)

    async def drop_all(self, binds: list[str] | Literal["all"] | None = "all"):
        """
        Drops all tables in the database.

        Args:
            binds (list[str] | Literal["all"] | None, optional): The database URLs to drop tables in. Defaults to "all".
        """
        async with self.connect() as connection:
            if isinstance(connection, AsyncConnection):
                await connection.run_sync(metadata.drop_all)
            else:
                metadata.drop_all(connection)

        if not self._engine_binds or not binds:
            return

        bind_keys = self._engine_binds.keys() if binds == "all" else binds
        for key in bind_keys:
            async with self.connect(key) as connection:
                if isinstance(connection, AsyncConnection):
                    await connection.run_sync(metadatas[key].drop_all)
                else:
                    metadatas[key].drop_all(connection)

    def _init_engine(self, url: str):
        """
        Initializes the database engine.

        Args:
            url (str): The URL of the database.

        Returns:
            AsyncEngine | Engine: The database engine. If the URL is an async URL, an async engine is returned.
        """
        try:
            return create_async_engine(url)
        except InvalidRequestError:
            return create_engine(url)

    def _init_sessionmaker(self, engine: AsyncEngine | Engine):
        """
        Initializes the database session maker.

        Args:
            engine (AsyncEngine | Engine): The database engine.

        Returns:
            async_sessionmaker[AsyncSession] | sessionmaker[Session]: The database session maker.
        """
        if isinstance(engine, AsyncEngine):
            return async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return sessionmaker(
            bind=engine,
            class_=Session,
            expire_on_commit=False,
        )


session_manager = DatabaseSessionManager()


def get_db(bind: str | None = None):
    """
    A coroutine function that returns a function that yields a database session.

    Can be used as a dependency in FastAPI routes.

    Args:
        bind (str, optional): The database URL to bind to. If None, the default database is used. Defaults to None.

    Returns:
        AsyncIterator[AsyncSession]: An async generator that yields a database session.

    Usage:
    ```python
        @app.get("/items/")
        async def read_items(session: AsyncSession = Depends(get_db())):
            # Use the session to interact with the database
    ```
    """

    async def get_db_dependency():
        async with session_manager.session(bind) as session:
            yield session

    return get_db_dependency


async def get_user_db(db: AsyncSession = Depends(get_db(User.__bind_key__))):
    """
    A dependency for FAST API to get the UserDatabase instance.

    Parameters:
    - db: The async db object for the database connection.

    Yields:
    - UserDatabase: An instance of the UserDatabase class.

    """
    yield UserDatabase(db, User, OAuthAccount)
