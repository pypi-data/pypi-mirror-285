import re
from typing import Any, Callable, Collection, Dict, Sequence, Set, Tuple

from sqlalchemy import Connection, Engine, MetaData
from sqlalchemy import Table as SA_Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import SchemaConst, SchemaItem

camelcase_re = re.compile(r"([A-Z]+)(?=[a-z0-9])")


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ("_%s_%s" % (word[:-1], word[-1])).lower()

        return "_" + word.lower()

    return camelcase_re.sub(_join, name).lstrip("_")


metadatas: dict[str, MetaData] = {
    "default": MetaData(),
}


class Model(DeclarativeBase):
    """
    Use this class has the base for your models,
    it will define your table names automatically
    MyModel will be called my_model on the database.

    ::

        from sqlalchemy import Integer, String
        from fastapi-rtk import Model

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique = True, nullable=False)

    """

    __bind_key__ = None
    """
    The bind key to use for this model. This allow you to use multiple databases. None means the default database. Default is None.
    """

    metadata = metadatas["default"]

    def __init_subclass__(cls, **kw: Any) -> None:
        # Overwrite the metadata if the bind key is set
        if cls.__bind_key__:
            if cls.__bind_key__ not in metadatas:
                metadatas[cls.__bind_key__] = MetaData()
            cls.metadata = metadatas[cls.__bind_key__]
        return super().__init_subclass__(**kw)

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Returns the table name for the given class.

        The table name is derived from the class name by converting
        any uppercase letters to lowercase and inserting an underscore
        before each uppercase letter.

        Returns:
            str: The table name.
        """
        return camel_to_snake_case(cls.__name__)

    __table_args__ = {"extend_existing": True}

    def update(self, data: dict[str, any]):
        """
        Updates the model instance with the given data.

        Args:
            data (dict): The data to update the model instance with.

        Returns:
            None
        """
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def name_(self):
        """
        Returns the string representation of the object.
        """
        return str(self)


metadata = metadatas["default"]


class Table(SA_Table):
    """
    Represents a table in the database.

    The metadata is automatically set to the default metadata. Please use bind_key to use a different metadata.

    DO NOT MANUALLY SET THE METADATA, LET THE MODEL HANDLE IT.
    """

    def __init__(
        self,
        name: str,
        *args: SchemaItem,
        schema: str | None | SchemaConst = None,
        quote: bool | None = None,
        quote_schema: bool | None = None,
        autoload_with: Engine | Connection | None = None,
        autoload_replace: bool = True,
        keep_existing: bool = False,
        extend_existing: bool = False,
        resolve_fks: bool = True,
        include_columns: Collection[str] | None = None,
        implicit_returning: bool = True,
        comment: str | None = None,
        info: Dict[Any, Any] | None = None,
        listeners: Sequence[Tuple[str | Callable[..., Any]]] | None = None,
        prefixes: Sequence[str] | None = None,
        _extend_on: Set[SA_Table] | None = None,
        _no_init: bool = True,
        bind_key: str | None = None,
        **kw: Any
    ) -> None:
        metadata, *rest_args = args

        super().__init__(
            name,
            metadata,
            *rest_args,
            schema=schema,
            quote=quote,
            quote_schema=quote_schema,
            autoload_with=autoload_with,
            autoload_replace=autoload_replace,
            keep_existing=keep_existing,
            extend_existing=extend_existing,
            resolve_fks=resolve_fks,
            include_columns=include_columns,
            implicit_returning=implicit_returning,
            comment=comment,
            info=info,
            listeners=listeners,
            prefixes=prefixes,
            _extend_on=_extend_on,
            _no_init=_no_init,
            **kw
        )

    @classmethod
    def _new(cls, *args: Any, **kw: Any) -> Any:
        table_name, second_arg, *remaining_args = args
        if isinstance(second_arg, MetaData):
            raise Exception(
                "Please do not pass metadata to the Table, let it be handled by the Model"
            )

        table_metadata = metadatas["default"]
        if "bind_key" in kw:
            if kw["bind_key"] not in metadatas:
                metadatas[kw["bind_key"]] = MetaData()
            table_metadata = metadatas[kw["bind_key"]]

        new_args = (table_name, table_metadata, second_arg, *remaining_args)
        return super()._new(*new_args, **kw)


"""
    This is for retro compatibility
"""
Base = Model
