import json
from datetime import datetime
from typing import Annotated, Any, Dict, Literal, Optional

from fastapi import HTTPException
from fastapi_users import schemas
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    ValidationError,
    ValidationInfo,
    field_validator,
)

from .utils import ensure_tz_info, validate_utc

PRIMARY_KEY = int | str | Dict[str, str | int]

DatetimeUTC = Annotated[
    datetime, BeforeValidator(ensure_tz_info), AfterValidator(validate_utc)
]


class RoleSchema(BaseModel):
    """
    Represents a role schema.

    Attributes:
        id (int): The ID of the role.
        name (str): The name of the role.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserRead(schemas.CreateUpdateDictModel, BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    first_name: str | None = None
    last_name: str | None = None
    roles: list[RoleSchema] = []
    is_active: bool = True
    permissions: list[str] = []


class UserReadWithStringRoles(UserRead):
    roles: list[str] = []


class UserCreate(schemas.CreateUpdateDictModel, BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    active: Optional[bool] = True
    roles: list[str] = []


class UserUpdate(schemas.CreateUpdateDictModel, BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    active: Optional[bool] = None


class RelInfo(BaseModel):
    """
    Represents information about a relationship.

    Attributes:
        id (PRIMARY_KEY): The ID of the relationship.
        value (str): The value of the relationship.
    """

    id: PRIMARY_KEY = 0
    value: str = ""


class ColumnInfo(BaseModel):
    """
    Represents information about a column.

    Attributes:
        description (str): The description of the column.
        label (str): The label of the column.
        name (str): The name of the column.
        required (bool): Indicates if the column is required.
        type (str): The type of the column.
        unique (bool): Indicates if the column values must be unique.
    """

    description: str = ""
    label: str = ""
    name: str = ""
    required: bool = False
    type: str = "string"
    unique: bool = False


class ColumnRelationInfo(ColumnInfo):
    """
    Represents information about a column relation.

    Attributes:
        count (int): The count of column relations.
        values (List[RelInfo]): The list of column relations.
    """

    count: int = 0
    values: list[RelInfo] = []


class SearchFilter(BaseModel):
    """
    Represents a search filter.

    Attributes:
        name (str): The name of the filter.
        operator (str): The operator to be used for filtering.
    """

    name: str = ""
    operator: str = ""


class InfoResponse(BaseModel):
    """
    Represents the info response object.

    Attributes:
        add_columns (list[ColumnInfo | ColumnRelationInfo]): The allowed columns for adding.
        add_title (str): The title for adding.
        edit_columns (list[ColumnInfo | ColumnRelationInfo]): The allowed columns for editing.
        edit_title (str): The title for editing.
        filters (dict[str, Any]): The filters for the response.
        filter_options (dict[str, Any]): The filter options for the response.
        permissions (list[str]): The permissions for the response.
        relations (list[str]): The relations for the response.
    """

    add_columns: list[ColumnInfo | ColumnRelationInfo] = []
    add_title: str = ""
    edit_columns: list[ColumnInfo | ColumnRelationInfo] = []
    edit_title: str = ""
    filters: dict[str, Any] = {}
    filter_options: dict[str, Any] = {}
    permissions: list[str] = []
    relations: list[str] = []


class BaseResponse(BaseModel):
    """
    Represents a base response object.

    Attributes:
        description_columns (dict[str, str]): The description columns for the response.
        label_columns (dict[str, str]): The label columns for the response.
    """

    description_columns: dict[str, str] = {}
    label_columns: dict[str, str] = {}


class BaseResponseSingle(BaseResponse):
    """
    Represents a response containing a single item.

    Attributes:
        id (PRIMARY_KEY): The ID of the item.
        show_columns (list[str]): The columns to show in the response.
        show_title (str): The title for the response.
        result (BaseModel | None): The result of the response.
    """

    id: PRIMARY_KEY
    show_columns: list[str] = []
    show_title: str = ""
    result: BaseModel | None = None


class BaseResponseMany(BaseResponse):
    """
    Represents a response containing multiple items.

    Attributes:
        count (int): The count of items.
        ids (List[PRIMARY_KEY]): The IDs of the items.
        list_columns (List[str]): The columns to show in the list.
        list_title (str): The title for the list.
        order_columns (List[str]): The columns to order the items by.
        result (List[BaseModel] | None): The result of the response.
    """

    count: int
    ids: list[PRIMARY_KEY]
    list_columns: list[str] = []
    list_title: str = ""
    order_columns: list[str] = []
    result: list[BaseModel] | None = None


class GeneralResponse(BaseModel):
    """
    Represents a general response object.

    Attributes:
        detail (str): The detail of the response.
    """

    detail: str


class FilterSchema(BaseModel):
    """
    Represents a filter for querying data.

    Attributes:
        col (str): The column name to filter on.
        opr (str): The operator to use for the filter.
        value (Union[str, int, List[Union[str, int]]]): The value to filter by.

    """

    col: str
    opr: str
    value: str | int | list[str | int]


class QuerySchema(BaseModel):
    """
    Represents the query parameters for pagination, ordering, and filtering.

    Attributes:
        page (int): The page number for pagination. Defaults to 0.
        page_size (int, optional): The number of items per page. Defaults to 25.
        order_column (str, optional): The column to order the results by.
        order_direction (Literal['asc', 'desc'], optional): The direction of the ordering (asc or desc).
        filters (str, optional): The filters to apply to the query. Defaults to '[]'.
    """

    page: int = 0
    page_size: int | None = 25
    order_column: str | None = None
    order_direction: Literal["asc", "desc"] | None = None
    filters: str = "[]"

    @field_validator("order_direction")
    @classmethod
    def validate_order_fields(cls, v: str | None, info: ValidationInfo):
        data = info.data
        try:
            if bool(v) != bool(data.get("order_column")):
                raise ValueError(
                    "Both order_column and order_direction must be filled or empty"
                )
            return str(v) if v else v
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Both order_column and order_direction must be filled or empty",
            )

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: str | list[FilterSchema], info: ValidationInfo):
        try:
            filters = json.loads(v) if isinstance(v, str) else v
            if not isinstance(filters, list):
                raise ValueError("Filters must be a list")
            new_filters = []
            for filter in filters:
                if isinstance(filter, FilterSchema):
                    new_filters.append(filter)
                elif isinstance(filter, dict):
                    new_filters.append(FilterSchema(**filter))
                else:
                    raise ValueError("Filter must be a dictionary")
            return new_filters
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid filters: Not a valid JSON string"
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "ValidationError",
                    "loc": ["query", "filters"],
                    "msg": e.errors(),
                },
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))


class QueryBody(QuerySchema):
    """
    Schema for query, but in the request body.
    """

    filters: list[FilterSchema] = []
