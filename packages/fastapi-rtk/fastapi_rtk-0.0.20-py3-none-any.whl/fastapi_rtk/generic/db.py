from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import QueryManager
from ..schemas import FilterSchema
from .filters import GenericBaseFilter
from .interface import GenericInterface
from .model import GenericModel, GenericSession


class GenericQueryManager(QueryManager):
    """
    A class to manage database queries for generic. It provides methods to add options for pagination, ordering, and filtering to the query.

    Raises:
        e: If an error occurs during query execution.
    """

    datamodel: GenericInterface
    stmt: GenericSession | None = None

    def __init__(
        self,
        db: AsyncSession,
        datamodel: GenericInterface,
        session: GenericSession | None = None,
    ):
        self.stmt = session
        super().__init__(db, datamodel)

    def join(self, join_columns: list[str]):
        pass

    def order_by(self, order_column: str, order_direction: str):
        if not order_column or not order_direction:
            return
        col = order_column
        col = col.lstrip()

        #! If the order column comes from a request, it will be in the format ClassName.column_name
        if col.startswith(self.datamodel.obj.__class__.__name__) or col.startswith(
            self.datamodel.obj.__name__
        ):
            col = col.split(".", 1)[1]

        self.stmt = self.stmt.order_by(f"{col} {order_direction}")

    def where(self, column: str, value: Any):
        self.stmt = self.stmt.equal(column, value)

    def where_in(self, column: str, values: list[Any]):
        self.stmt = self.stmt.in_(column, values)

    def filter(self, filter: FilterSchema):
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

        col = filter.col
        value = filter.value

        self.stmt = filter_class.apply(self.stmt, col, value)

    def filter_class(self, col: str, filter_class: GenericBaseFilter, value: Any):
        self.stmt = filter_class.apply(self.stmt, col, value)

    def add(self, item: GenericModel):
        self.stmt.add(item)

    def delete(self, item: GenericModel):
        self.stmt.delete(item)

    def count(
        self,
        filters: list[FilterSchema] | None = None,
        filter_classes: list[tuple[str, GenericBaseFilter, Any]] | None = None,
    ) -> int:
        try:
            self._init_query()
            if filters:
                for filter in filters:
                    self.filter(filter)
            if filter_classes:
                for col, filter_class, value in filter_classes:
                    self.filter_class(col, filter_class, value)
            count, _ = self.stmt.all()
            return count
        finally:
            self._init_query()

    def execute(self, many=True) -> GenericModel | list[GenericModel] | None:
        try:
            _, items = self.stmt.all()
            if many:
                return items

            return items[0] if items else None
        except Exception as e:
            raise e
        finally:
            self._init_query()

    async def yield_per(self, page_size: int):
        try:
            items = self.stmt.yield_per(page_size)
            while True:
                chunk = items[:page_size]
                items = items[page_size:]
                if not chunk:
                    break
                yield chunk
        finally:
            self._init_query()

    def _init_query(self):
        self.stmt = self.stmt.query(self.datamodel.obj)
