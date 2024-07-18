from datetime import date, datetime
from typing import Any, List

from pydantic import BaseModel

from .model import GenericSession


class GenericBaseFilter:
    name: str
    arg_name: str

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        """
        Apply the filter to the given SQLAlchemy Select statement.

        Args:
            db (GenericSession): The generic session object.
            col (str): The column to filter on.
            value (Any): The value to filter by.

        Returns:
            List[BaseModel]: The list of BaseModel with the filter applied.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError()


class GenericFilterStartsWith(GenericBaseFilter):
    name = "Starts with"
    arg_name = "sw"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.starts_with(col, value)


class GenericFilterNotStartsWith(GenericBaseFilter):
    name = "Not Starts with"
    arg_name = "nsw"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.not_starts_with(col, value)


class GenericFilterEndsWith(GenericBaseFilter):
    name = "Ends with"
    arg_name = "ew"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.ends_with(col, value)


class GenericFilterNotEndsWith(GenericBaseFilter):
    name = "Not Ends with"
    arg_name = "new"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.not_ends_with(col, value)


class GenericFilterContains(GenericBaseFilter):
    name = "Contains"
    arg_name = "ct"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.like(col, value)


class GenericFilterIContains(GenericBaseFilter):
    name = "Contains (insensitive)"
    arg_name = "ict"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.ilike(col, value)


class GenericFilterNotContains(GenericBaseFilter):
    name = "Not Contains"
    arg_name = "nct"

    def apply(db: GenericSession, col: str, value: Any) -> List[BaseModel]:
        return db.not_like(col, value)


class GenericFilterEqual(GenericBaseFilter):
    name = "Equal to"
    arg_name = "eq"

    def apply(
        db: GenericSession, col: str, value: str | bool | int | date | datetime
    ) -> List[BaseModel]:
        return db.equal(col, value)


class GenericFilterNotEqual(GenericBaseFilter):
    name = "Not Equal to"
    arg_name = "neq"

    def apply(
        db: GenericSession, col: str, value: str | bool | int | date | datetime
    ) -> List[BaseModel]:
        return db.not_equal(col, value)


class GenericFilterGreater(GenericBaseFilter):
    name = "Greater than"
    arg_name = "gt"

    def apply(
        db: GenericSession, col: str, value: int | date | datetime
    ) -> List[BaseModel]:
        return db.greater(col, value)


class GenericFilterSmaller(GenericBaseFilter):
    name = "Smaller than"
    arg_name = "lt"

    def apply(
        db: GenericSession, col: str, value: int | date | datetime
    ) -> List[BaseModel]:
        return db.smaller(col, value)


class GenericFilterGreaterEqual(GenericBaseFilter):
    name = "Greater equal"
    arg_name = "ge"

    def apply(
        db: GenericSession, col: str, value: int | date | datetime
    ) -> List[BaseModel]:
        return db.greater_equal(col, value)


class GenericFilterSmallerEqual(GenericBaseFilter):
    name = "Smaller equal"
    arg_name = "le"

    def apply(
        db: GenericSession, col: str, value: int | date | datetime
    ) -> List[BaseModel]:
        return db.smaller_equal(col, value)


class GenericFilterIn(GenericBaseFilter):
    name = "One of"
    arg_name = "in"

    def apply(
        db: GenericSession, col: str, value: list[str | bool | int]
    ) -> List[BaseModel]:
        return db.in_(col, value)


class GenericFilterConverter:
    """
    Helper class to get available filters for a generic column type.
    """

    conversion_table = (
        ("is_enum", [GenericFilterEqual, GenericFilterNotEqual, GenericFilterIn]),
        ("is_boolean", [GenericFilterEqual, GenericFilterNotEqual, GenericFilterIn]),
        (
            "is_text",
            [
                GenericFilterStartsWith,
                GenericFilterNotStartsWith,
                GenericFilterEndsWith,
                GenericFilterNotEndsWith,
                GenericFilterContains,
                GenericFilterIContains,
                GenericFilterNotContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_string",
            [
                GenericFilterStartsWith,
                GenericFilterNotStartsWith,
                GenericFilterEndsWith,
                GenericFilterNotEndsWith,
                GenericFilterContains,
                GenericFilterIContains,
                GenericFilterNotContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_integer",
            [
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterGreater,
                GenericFilterSmaller,
                GenericFilterGreaterEqual,
                GenericFilterSmallerEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_date",
            [
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterGreater,
                GenericFilterSmaller,
                GenericFilterGreaterEqual,
                GenericFilterSmallerEqual,
                GenericFilterIn,
            ],
        ),
    )
