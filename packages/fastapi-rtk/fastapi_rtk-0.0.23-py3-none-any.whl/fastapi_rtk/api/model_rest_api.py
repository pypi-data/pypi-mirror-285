import re
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Tuple, Type, overload

from fastapi import Body, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, create_model
from sqlalchemy.ext.asyncio import AsyncSession

from ..const import logger
from ..db import QueryManager, get_db
from ..decorators import permission_name
from ..dependencies import (
    current_active_user,
    current_permissions,
    get_query_manager,
    has_access_dependency,
)
from ..filters import BaseFilter
from ..models import Model
from ..schemas import (
    PRIMARY_KEY,
    BaseResponseMany,
    BaseResponseSingle,
    ColumnInfo,
    ColumnRelationInfo,
    GeneralResponse,
    InfoResponse,
    QueryBody,
    QuerySchema,
    RelInfo,
)
from ..utils import generate_report, merge_schema, safe_call, smart_run
from .base_api import BaseApi
from .interface import Params, SQLAInterface


class ModelRestApi(BaseApi):
    """
    Base Class for FastAPI APIs that use a SQLAlchemy model.

    Usage:
    ```python
    from fastapi_rtk.api import ModelRestApi
    from fastapi_rtk.filters import FilterEqual
    from app.models import User
    from app.schemas import UserSchema

    class UserApi(ModelRestApi):
        datamodel = SQLAInterface(User)
        search_columns = ["username"]
        search_exclude_columns = ["password"]
        search_query_rel_fields = {
            "user": [
                ["username", FilterEqual, "admin"],
            ],
        }
        filter_options = {
            "odd_numbers": [1, 3, 5, 7, 9],
        }
    """

    """
    -------------
     GENERAL
    -------------
    """

    datamodel: SQLAInterface
    """
    The SQLAlchemy interface object.

    Usage:
    ```python
    datamodel = SQLAInterface(User)
    ```
    """

    max_page_size: int = 25
    """
    The maximum page size for the related fields in add_columns, edit_columns, and search_columns properties.
    """

    exclude_routes: List[str] = None
    """
    The list of routes to exclude. available routes: `info`, `download`, `bulk`, `list`, `get`, `post`, `put`, `delete`.
    """

    base_order: Tuple[str, Literal["asc", "desc"]] | None = None
    """
    The default order for the list endpoint. Set this to set the default order for the list endpoint.

    Example:
    ```python
    base_order = ("name", "asc")
    ```
    """

    base_filters: List[Tuple[str, BaseFilter, Any]] | None = None
    """
    The default filters for the list endpoint. Set this to set the default filters for the list endpoint. Defaults to None.

    Example:
    ```python
    base_filters = [
        ["status", FilterEqual, "active"],
    ]
    ```
    """

    show_base_filters: List[Tuple[str, BaseFilter, Any]] | None = None
    """
    The default filters for the show endpoint. Set this to set the default filters for the show endpoint. Defaults to None.

    Example:
    ```python
    show_base_filters = [
        ["status", FilterEqual, "active"],
    ]
    ```
    """

    download_base_filters: List[Tuple[str, BaseFilter, Any]] | None = None
    """
    The default filters for the download endpoint. Set this to set the default filters for the download endpoint. Defaults to None.

    Example:
    ```python
    download_base_filters = [
        ["status", FilterEqual, "active"],
    ]
    ```
    """

    description_columns: Dict[str, str] = None
    """
    The description for each column in the add columns, edit columns, and search columns properties.

    Example:
    ```python
    description_columns = {
        "name": "Name of the item",
        "description": "Description of the item",
    }
    ```
    """
    order_rel_fields: Dict[str, Tuple[str, Literal["asc", "desc"]]] = None
    """
    Order the related fields in the add columns, edit columns, and search columns properties.

    Example:
    ```python
    order_rel_fields = {
        "user": ("username", "asc"),
    }
    ```
    """
    filter_options: Dict[str, Any] = None
    """
    Additional filter options from the user for the info endpoint.

    Example:
    ```python
    filter_options = {
        "odd_numbers": [1, 3, 5, 7, 9],
    }
    ```
    """
    query_schema: Type[QuerySchema] = None
    """
    The query schema for the list endpoint.
    
    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    download_body_schema: Type[QueryBody] = None
    """
    The body schema for the download endpoint.
    
    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     INFO
    -------------
    """

    info_return_schema: Type[InfoResponse] = None
    """
    The response schema for the info endpoint. 

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     SEARCH
    -------------
    """

    search_columns: List[str] = None
    """
    The list of columns that are allowed to be filtered in the list endpoint. If not provided, all columns will be allowed.
    """
    search_exclude_columns: List[str] = None
    """
    The list of columns to exclude from the search columns.
    """
    search_filters: Dict[str, List[BaseFilter]] = None
    """
    Add additional filters to the search columns.

    Example:
    ```python
    search_filters = {
        "name": [FilterNameStartsWithA],
    }
    ```
    """
    search_query_rel_fields: Dict[str, List[Tuple[str, BaseFilter, Any]]] = None
    """
    The query fields for the related fields in the filters.

    Example:
    ```python
    search_query_rel_fields = {
        "user": [
            ["username", FilterEqual, "admin"],
        ],
    }
    ```
    """

    """
    -------------
     LIST
    -------------
    """

    list_title: str = None
    """
    The title for the list endpoint. If not provided, Defaults to "List {ModelName}".
    """
    list_columns: List[str] = None
    """
    The list of columns to display in the list endpoint. If not provided, all columns will be displayed.
    """
    list_exclude_columns: List[str] = None
    """
    The list of columns to exclude from the list endpoint.
    """
    list_join_columns: List[str] = None
    """
    The list of columns to join in the list endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    list_return_schema: Type[BaseResponseMany] = None
    """
    The response schema for the list endpoint.
    
    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    label_columns: Dict[str, str] = None
    """
    The label for each column in the list columns and show columns properties.

    Example:
    ```python
    label_columns = {
        "name": "Name",
        "description": "Description",
    }
    ```
    """
    order_columns: List[str] = None
    """
    The list of columns that can be ordered in the list endpoint. If not provided, all columns will be allowed.
    """

    """
    -------------
     SHOW
    -------------
    """

    show_title: str = None
    """
    The title for the show endpoint. If not provided, Defaults to "Show {ModelName}".
    """
    show_columns: List[str] = None
    """
    The list of columns to display in the show endpoint and for the result of the add and edit endpoint. If not provided, all columns will be displayed.
    """
    show_exclude_columns: List[str] = None
    """
    The list of columns to exclude from the show endpoint.
    """
    show_join_columns: List[str] = None
    """
    The list of columns to join in the show endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    show_return_schema: Type[BaseResponseSingle] = None
    """
    The response schema for the show endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     ADD
    -------------
    """

    add_title: str = None
    """
    The title for the add endpoint. If not provided, Defaults to "Add {ModelName}".
    """
    add_columns: List[str] = None
    """
    The list of columns to display in the add endpoint. If not provided, all columns will be displayed.
    """
    add_exclude_columns: List[str] = None
    """
    The list of columns to exclude from the add endpoint.
    """
    add_schema: Type[BaseModel] = None
    """
    The schema for the add endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    add_return_schema: Type[BaseResponseSingle] = None
    """
    The response schema for the add endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    add_query_rel_fields: Dict[str, List[Tuple[str, BaseFilter, Any]]] = None
    """
    The query fields for the related fields in the add_columns property.

    Example:
    ```python
    add_query_rel_fields = {
        "user": [
            ["username", FilterEqual, "admin"],
        ],
    }
    ```
    """

    """
    -------------
     EDIT
    -------------
    """

    edit_title: str = None
    """
    The title for the edit endpoint. If not provided, Defaults to "Edit {ModelName}".
    """
    edit_columns: List[str] = None
    """
    The list of columns to display in the edit endpoint. If not provided, all columns will be displayed.
    """
    edit_exclude_columns: List[str] = None
    """
    The list of columns to exclude from the edit endpoint.
    """
    edit_schema: Type[BaseModel] = None
    """
    The schema for the edit endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    edit_return_schema: Type[BaseResponseSingle] = None
    """
    The response schema for the edit endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    edit_query_rel_fields: Dict[str, List[Tuple[str, BaseFilter, Any]]] = None
    """
    The query fields for the related fields in the edit_columns property.

    Example:
    ```python
    edit_query_rel_fields = {
        "user": [
            ["username", FilterEqual, "admin"],
        ],
    }
    ```
    """

    """
    -------------
     PRIVATE
    -------------
    """

    _default_info_schema: bool = False
    """
    A flag to indicate if the default info schema is used.

    DO NOT MODIFY.
    """

    def __init__(self):
        if not self.datamodel:
            raise Exception(f"Missing datamodel in {self.__class__.__name__} API.")
        self.resource_name = self.resource_name or self.datamodel.obj.__name__.lower()
        super().__init__()
        self._init_titles()
        self._init_properties()
        self.post_properties()
        self._init_schema()
        self.post_schema()

    def post_properties(self):
        """
        Post properties to be called after the init_properties method.
        """
        pass

    def post_schema(self):
        """
        Post schema to be called after the init_schema method.
        """
        pass

    """
    -----------------------------------------
         INIT FUNCTIONS
    -----------------------------------------
    """

    def _init_titles(self) -> None:
        """
        Init Titles if not defined
        """
        class_name = self.datamodel.obj.__name__
        if not self.list_title:
            self.list_title = "List " + self._prettify_name(class_name)
        if not self.add_title:
            self.add_title = "Add " + self._prettify_name(class_name)
        if not self.edit_title:
            self.edit_title = "Edit " + self._prettify_name(class_name)
        if not self.show_title:
            self.show_title = "Show " + self._prettify_name(class_name)
        self.title = self.list_title

    def _init_properties(self) -> None:
        """
        Init properties if not defined
        """
        list_cols = self.datamodel.get_user_columns_list()

        self.search_filters = self.search_filters or {}
        for key, value in self.search_filters.items():
            self.datamodel._filters[key] = self.datamodel._filters[key] + value

        self.exclude_routes = self.exclude_routes or []
        self.exclude_routes = [x.lower() for x in self.exclude_routes]
        self.description_columns = self.description_columns or {}
        self.filter_options = self.filter_options or {}

        self.list_exclude_columns = self.list_exclude_columns or []
        self.show_exclude_columns = self.show_exclude_columns or []
        self.add_exclude_columns = self.add_exclude_columns or []
        self.edit_exclude_columns = self.edit_exclude_columns or []
        self.search_exclude_columns = self.search_exclude_columns or []
        self.label_columns = self.label_columns or {}

        self.list_columns = self.list_columns or [
            x for x in list_cols if x not in self.list_exclude_columns
        ]
        self.show_columns = self.show_columns or [
            x for x in list_cols if x not in self.show_exclude_columns
        ]
        self.add_columns = self.add_columns or [
            x for x in list_cols if x not in self.add_exclude_columns
        ]
        self.edit_columns = self.edit_columns or [
            x for x in list_cols if x not in self.edit_exclude_columns
        ]
        self.search_columns = self.search_columns or [
            x
            for x in self.datamodel.get_search_columns_list()
            if x not in self.search_exclude_columns
        ]

        self.list_join_columns = self.list_join_columns or [
            x for x in self.list_columns if self.datamodel.is_relation(x)
        ]
        self.show_join_columns = self.show_join_columns or [
            x for x in self.show_columns if self.datamodel.is_relation(x)
        ]

        # Add columns with @property decorator
        property_cols = self.datamodel.get_property_column_list()
        self.list_columns += [
            x
            for x in property_cols
            if x not in self.list_columns and x not in self.list_exclude_columns
        ]
        self.show_columns += [
            x
            for x in property_cols
            if x not in self.show_columns and x not in self.show_exclude_columns
        ]

        self._gen_labels_columns(self.list_columns)
        self._gen_labels_columns(self.show_columns)

        self.order_columns = (
            self.order_columns
            or self.datamodel.get_order_columns_list(list_columns=self.list_columns)
        )

        self.order_rel_fields = self.order_rel_fields or dict()
        self.add_query_rel_fields = self.add_query_rel_fields or dict()
        self.edit_query_rel_fields = self.edit_query_rel_fields or dict()
        self.search_query_rel_fields = self.search_query_rel_fields or dict()

    def _init_schema(self) -> None:
        """
        Initializes the schema for the API.

        This method creates schema models for info, list, get, add, and edit endpoints based on the datamodel's table columns.

        Returns:
            None
        """
        if not self.info_return_schema:
            self.info_return_schema = merge_schema(
                InfoResponse,
                {
                    "add_title": (str, Field(default=self.add_title)),
                    "edit_title": (str, Field(default=self.edit_title)),
                    "filter_options": (dict, Field(default={})),
                },
                name=f"{self.__class__.__name__}-InfoResponse",
            )
            self._default_info_schema = True

        order_column_enum = Enum(
            f"{self.__class__.__name__}-OrderColumnEnum",
            {col: col for col in self.order_columns},
            type=str,
        )

        self.query_schema = self.query_schema or merge_schema(
            QuerySchema,
            {
                "order_column": (order_column_enum | None, Field(default=None)),
            },
            True,
            f"{self.__class__.__name__}-QuerySchema",
        )

        self.download_body_schema = self.download_body_schema or merge_schema(
            QueryBody,
            {
                "order_column": (order_column_enum | None, Field(default=None)),
            },
            True,
            f"{self.__class__.__name__}-DownloadBodySchema",
        )

        list_obj_schema = self.datamodel.generate_schema(
            self.list_columns, False, name=f"{self.__class__.__name__}-ListObjSchema"
        )
        show_obj_schema = self.datamodel.generate_schema(
            self.show_columns, False, name=f"{self.__class__.__name__}-ShowObjSchema"
        )
        add_obj_schema = self.datamodel.generate_schema(
            self.add_columns, False, name=f"{self.__class__.__name__}-AddObjSchema"
        )
        edit_obj_schema = self.datamodel.generate_schema(
            self.edit_columns,
            False,
            optional=True,
            name=f"{self.__class__.__name__}-EditObjSchema",
        )

        # Combine props with @property functions
        property_column_dict = dict()
        for col in self.list_columns:
            if self.datamodel.is_property(col):
                property_column_dict[col] = (Any, Field(default=None))

        if property_column_dict:
            list_obj_schema = merge_schema(
                list_obj_schema,
                property_column_dict,
            )
            show_obj_schema = merge_schema(
                show_obj_schema,
                property_column_dict,
            )

        self.list_return_schema = self.list_return_schema or merge_schema(
            BaseResponseMany,
            {
                **vars(self),
                "result": (List[list_obj_schema], ...),
            },
            True,
            f"{self.__class__.__name__}-ListResponse",
        )
        self.show_return_schema = self.show_return_schema or merge_schema(
            BaseResponseSingle,
            {
                **vars(self),
                "result": (show_obj_schema, ...),
            },
            True,
            f"{self.__class__.__name__}-ShowResponse",
        )
        self.add_return_schema = self.add_return_schema or merge_schema(
            self.show_return_schema,
            {},
            name=f"{self.__class__.__name__}-AddResponse",
        )
        self.edit_return_schema = self.edit_return_schema or merge_schema(
            self.show_return_schema,
            {},
            name=f"{self.__class__.__name__}-EditResponse",
        )

        self.add_schema = self.add_schema or self._create_request_schema(
            add_obj_schema, name=f"{self.__class__.__name__}-AddSchema"
        )
        self.edit_schema = self.edit_schema or self._create_request_schema(
            edit_obj_schema, optional=True, name=f"{self.__class__.__name__}-EditSchema"
        )

    def _init_routes(self) -> None:
        """
        Initializes the routes for the API endpoints.

        This method is responsible for initializing the routes for various API endpoints,
        such as the info, list, get, create, update, and delete endpoints.

        Returns:
            None
        """
        if not "info" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/_info ['GET']")
            self._init_info_endpoint()
        if not "download" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/download ['POST']")
            self._init_download_endpoint()
        if not "bulk" in self.exclude_routes:
            logger.info(
                f"Registering route {self.router.prefix}/bulk/{{handler}} ['POST']"
            )
            self._init_bulk_endpoint()
        if not "list" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/ ['GET']")
            self._init_list_endpoint()
        if not "get" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/{{id}} ['GET']")
            self._init_get_endpoint()
        if not "post" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/ ['POST']")
            self._init_post_endpoint()
        if not "put" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/{{id}} ['PUT']")
            self._init_put_endpoint()
        if not "delete" in self.exclude_routes:
            logger.info(f"Registering route {self.router.prefix}/{{id}} ['DELETE']")
            self._init_delete_endpoint()

    @permission_name("info")
    def _init_info_endpoint(self):
        """
        Initializes the info endpoint for the API.

        This method sets up the HTTP route for retrieving information about the API.

        Returns:
            None
        """

        bind_key = getattr(self.datamodel.obj, "__bind_key__", None)

        @self.router.get(
            "/_info",
            response_model=self.info_return_schema,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "info")),
            ],
        )
        async def get_info(
            *,
            permissions: List[str] = Depends(current_permissions(self)),
            db: AsyncSession = Depends(get_db(bind_key)),
        ):
            return await smart_run(self.info_headless, permissions, db)

    async def info_headless(self, permissions: List[str], db: AsyncSession):
        """
        Retrieves information in a headless mode.

        Args:
            permissions (List[str]): A list of permissions.
            db (AsyncSession): An asynchronous database session.

        Returns:
            info_return_schema: The information return schema.
        """
        if self._default_info_schema:
            return await smart_run(self._generate_info_schema, permissions, db)
        return self.info_return_schema()

    @permission_name("download")
    def _init_download_endpoint(self):
        """
        Initializes the download endpoint for the API.

        This method sets up the HTTP route for downloading a file.

        Returns:
            None
        """

        @self.router.post(
            "/download",
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "download")),
            ],
        )
        async def download(
            body: self.download_body_schema,
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.download_headless, body, query)

    async def download_headless(self, body: QueryBody, query: QueryManager):
        """
        Downloads a file in a headless mode.

        Args:
            body (QueryBody): The query body.
            query (QueryManager): The query manager object.

        Returns:
            StreamingResponse: The streaming response.
        """
        for filter in body.filters:
            if not filter.col in self.search_columns:
                raise HTTPException(
                    status_code=400, detail=f"Invalid filter: {filter.col}"
                )

        await smart_run(
            query.add_options,
            join_columns=self.list_join_columns,
            order_column=body.order_column,
            order_direction=body.order_direction,
            filters=body.filters,
            filter_classes=self.download_base_filters,
        )

        try:
            return StreamingResponse(
                generate_report(
                    query.yield_per(100),
                    self.list_columns,
                    self.label_columns,
                ),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={self.resource_name}.csv",
                },
            )
        finally:
            await safe_call(query.db.close())

    @permission_name("bulk")
    def _init_bulk_endpoint(self):
        """
        Initializes the bulk endpoint for the API.

        This method sets up the HTTP route for bulk operations.

        Returns:
            None
        """

        @self.router.post(
            "/bulk/{handler}",
            response_model=GeneralResponse,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "bulk")),
            ],
        )
        async def bulk(
            handler: str,
            body: dict | list = Body(...),
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.bulk_headless, handler, body, query)

    async def bulk_headless(self, handler: str, body: dict | list, query: QueryManager):
        """
        Bulk handler in headless mode.

        Args:
            handler (str): The handler name.
            body (dict | list): The request body.
            query (QueryManager): The query manager object.

        Returns:
            Response: The response object.
        """
        bulk_handler: function | None = getattr(self, f"bulk_{handler}", None)
        if not bulk_handler:
            raise HTTPException(status_code=404, detail="Handler not found")
        try:
            response = await smart_run(bulk_handler, body, query)
            return response
        except NotImplementedError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def bulk_handler(self, body: dict | list, query: QueryManager) -> Response:
        """
        Bulk handler for the API.
        To be implemented by the subclass.

        Example:
        ```python
        async def bulk_read(self, body: dict | list, query: QueryManager) -> Response:
            query.where_in(self.datamodel.get_pk_attr(), [item["id"] for item in body])
            items = await smart_run(query.execute)
            pks, data = self._convert_to_result(items)
            return data
        ```

        Args:
            body (dict | list): The request body.
            query (QueryManager): The query manager object.

        Returns:
            Response: The response object.

        Raises:
            NotImplementedError: If the method is not implemented. To be implemented by the subclass.
        """
        raise NotImplementedError("Bulk handler not implemented")

    @permission_name("get")
    def _init_list_endpoint(self):
        """
        Initializes the list endpoint for the API.

        This method sets up the HTTP route for retrieving all items.

        Returns:
            None
        """

        @self.router.get(
            "/",
            response_model=self.list_return_schema,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "get")),
            ],
        )
        async def get_all(
            q: self.query_schema = Depends(),
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.get_list_headless, q, query)

    async def get_list_headless(self, q: QuerySchema, query: QueryManager):
        """
        Retrieves all items in a headless mode.

        Args:
            q (QuerySchema): The query schema.
            query (QueryManager): The query manager object.

        Returns:
            list_return_schema: The list return schema.
        """
        for filter in q.filters:
            if not filter.col in self.search_columns:
                raise HTTPException(
                    status_code=400, detail=f"Invalid filter: {filter.col}"
                )
        base_order = None
        base_order_direction = None
        if self.base_order:
            base_order, base_order_direction = self.base_order
        filter_classes = self.base_filters
        await smart_run(
            query.add_options,
            join_columns=self.list_join_columns,
            page=q.page,
            page_size=q.page_size,
            order_column=q.order_column or base_order,
            order_direction=q.order_direction or base_order_direction,
            filters=q.filters,
            filter_classes=filter_classes,
        )
        items = await smart_run(query.execute)
        count = await smart_run(query.count, q.filters, filter_classes)
        pks, data = self._convert_to_result(items)
        body = self.list_return_schema(
            result=data,
            count=count,
            ids=pks,
            description_columns=self.description_columns,
            label_columns=self.label_columns,
            list_columns=self.list_columns,
            list_title=self.list_title,
            order_columns=self.order_columns,
        )
        await smart_run(
            self.pre_get_list, body, Params(ids=pks, q=q, query=query, items=items)
        )
        return body

    async def pre_get_list(self, body: BaseResponseMany, params: Params):
        """
        Pre-process the list response before returning it.
        The response still needs to adhere to the BaseResponseMany schema.

        Args:
            body (BaseResponseMany): The response body.
            params (Params): Additional data passed to the handler.
        """
        pass

    @permission_name("get")
    def _init_get_endpoint(self):
        """
        Initializes the get endpoint for the API.

        This method sets up the HTTP route for retrieving a single item.

        Returns:
            None
        """

        @self.router.get(
            "/{id}",
            response_model=self.show_return_schema,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "get")),
            ],
        )
        async def get_one(
            id: self.datamodel.id_schema,
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.get_headless, id, query)

    async def get_headless(self, id: str | int, query: QueryManager):
        """
        Retrieves a single item in a headless mode.

        Args:
            id (str | int): The id of the item.
            query (QueryManager): The query manager object.

        Returns:
            show_return_schema: The show return schema.
        """
        await smart_run(
            query.add_options,
            join_columns=self.show_join_columns,
            where_id=id,
            filter_classes=self.show_base_filters,
        )
        item = await smart_run(query.execute, many=False)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        pk, data = self._convert_to_result(item)
        body = self.show_return_schema(
            id=pk,
            result=data,
            description_columns=self.description_columns,
            label_columns=self.label_columns,
            show_columns=self.show_columns,
            show_title=self.show_title,
        )
        await smart_run(self.pre_get, body, Params(id=id, query=query, item=item))
        return body

    async def pre_get(self, body: BaseResponseSingle, params: Params):
        """
        Pre-process the get response before returning it.
        The response still needs to adhere to the BaseResponseSingle schema.

        Args:
            body (BaseResponseSingle): The response body.
            params (Params): Additional data passed to the handler.
        """
        pass

    @permission_name("post")
    def _init_post_endpoint(self):
        """
        Initializes the post endpoint for the API.

        This method sets up the HTTP route for creating a new item.

        Returns:
            None
        """

        @self.router.post(
            "/",
            response_model=self.add_return_schema,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "post")),
            ],
        )
        async def create(
            body: self.add_schema,
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.post_headless, body, query)

    async def post_headless(self, body: BaseModel, query: QueryManager):
        """
        Creates a new item in a headless mode.

        Args:
            body (BaseModel): The request body.
            query (QueryManager): The query manager object.

        Returns:
            add_return_schema: The add return schema.
        """
        body_json = await smart_run(self._process_body, query.db, body)
        item = self.datamodel.obj(**body_json)
        await smart_run(self.pre_add, item, Params(body=body, query=query))
        query.add(item)
        await safe_call(query.commit())
        await smart_run(
            query.add_options,
            join_columns=self.show_join_columns,
            where_id=getattr(item, self.datamodel.get_pk_attr()),
        )
        item = await smart_run(query.execute, many=False)
        await smart_run(self.post_add, item, Params(body=body, query=query))
        pk, data = self._convert_to_result(item)
        body = self.add_return_schema(id=pk, result=data)
        return body

    async def pre_add(self, item: Model, params: Params):
        """
        Pre-process the item before adding it to the database.

        Args:
            item (Model): The item to be added to the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def post_add(self, item: Model, params: Params):
        """
        Post-process the item after adding it to the database.
        But before sending the response.

        Args:
            item (Model): The item to be added to the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    @permission_name("put")
    def _init_put_endpoint(self):
        """
        Initializes the put endpoint for the API.

        This method sets up the HTTP route for updating an existing item.

        Returns:
            None
        """

        @self.router.put(
            "/{id}",
            response_model=self.edit_return_schema,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "put")),
            ],
        )
        async def update(
            id: self.datamodel.id_schema,
            body: self.edit_schema,
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.put_headless, id, body, query)

    async def put_headless(self, id: str | int, body: BaseModel, query: QueryManager):
        """
        Updates an item in a headless mode.

        Args:
            id (str | int): The id of the item.
            body (BaseModel): The request body.
            query (QueryManager): The query manager object.

        Returns:
            add_return_schema: The add return schema.
        """
        await smart_run(
            query.add_options, join_columns=self.show_join_columns, where_id=id
        )
        item = await smart_run(query.execute, many=False)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        body_json = await smart_run(self._process_body, query.db, body)
        item.update(body_json)
        await smart_run(self.pre_update, item, Params(body=body, query=query))
        await safe_call(query.commit())
        await smart_run(self.post_update, item, Params(body=body, query=query))
        pk, data = self._convert_to_result(item)
        body = self.edit_return_schema(id=pk, result=data)
        return body

    async def pre_update(self, item: Model, params: Params):
        """
        Pre-process the item before updating it in the database.

        Args:
            item (Model): The item that will be updated in the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def post_update(self, item: Model, params: Params):
        """
        Post-process the item after updating it in the database.
        But before sending the response.

        Args:
            item (Model): The item that was be updated in the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    @permission_name("delete")
    def _init_delete_endpoint(self):
        """
        Initializes the delete endpoint for the API.

        This method sets up the HTTP route for deleting an item.

        Returns:
            None
        """

        @self.router.delete(
            "/{id}",
            response_model=GeneralResponse,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access_dependency(self, "delete")),
            ],
        )
        async def delete(
            id: self.datamodel.id_schema,
            query: QueryManager = Depends(self.get_query_manager),
        ):
            return await smart_run(self.delete_headless, id, query)

    async def delete_headless(self, id: str | int, query: QueryManager):
        """
        Deletes an item in a headless mode.

        Args:
            id (str | int): The id of the item.
            query (QueryManager): The query manager object.

        Returns:
            GeneralResponse: The general response.
        """
        await smart_run(
            query.add_options, join_columns=self.show_join_columns, where_id=id
        )
        item = await smart_run(query.execute, many=False)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        await smart_run(self.pre_delete, item, Params(id=id, query=query))
        await safe_call(query.delete(item))
        await safe_call(query.commit())
        await smart_run(self.post_delete, item, Params(id=id, query=query))
        body = GeneralResponse(detail="Item deleted")
        return body

    async def pre_delete(self, item: Model, params: Params):
        """
        Pre-process the item before deleting it from the database.

        Args:
            item (Model): The item that will be deleted from the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def post_delete(self, item: Model, params: Params):
        """
        Post-process the item after deleting it from the database.
        But before sending the response.

        Args:
            item (Model): The item that was be deleted from the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    """
    -----------------------------------------
            CONVERSION FUNCTIONS
    -----------------------------------------
    """

    @overload
    def _convert_to_result(self, data: Model) -> Tuple[PRIMARY_KEY, Model]: ...
    @overload
    def _convert_to_result(
        self, data: List[Model]
    ) -> Tuple[List[PRIMARY_KEY], List[Model]]: ...
    def _convert_to_result(self, data: Model | List[Model]):
        """
        Converts the given data to a result tuple.

        Args:
            data (Model | List[Model]): The data to be converted.

        Returns:
            tuple: A tuple containing the primary key(s) and the converted data.

        """
        if isinstance(data, list):
            pks: PRIMARY_KEY = (
                [getattr(item, self.datamodel.get_pk_attr()) for item in data]
                if not self.datamodel.is_pk_composite()
                else [
                    {key: getattr(item, key) for key in self.datamodel.get_pk_attrs()}
                    for item in data
                ]
            )
        else:
            pks: PRIMARY_KEY = (
                getattr(data, self.datamodel.get_pk_attr())
                if not self.datamodel.is_pk_composite()
                else {key: getattr(data, key) for key in self.datamodel.get_pk_attrs()}
            )

        return (pks, data)

    def _create_request_schema(
        self, schema: Type[BaseModel], optional=False, name: str | None = None
    ):
        """
        Create a request schema based on the provided `schema` parameter. Useful for creating request schemas for add and edit endpoints, as it will transform the relation columns into the appropriate schema.

        Args:
            schema (Type[BaseModel]): The base schema to create the request schema from.
            optional (bool, optional): Flag indicating whether the request schema is optional. Defaults to False.
            name (str | None, optional): The name of the request schema. Defaults to None.

        Returns:
            pydantic.BaseModel: The created request schema.
        """
        columns = [
            x
            for x in schema.model_fields.keys()
            if not self.datamodel.is_pk(x) and self.datamodel.is_relation(x)
        ]
        rel_schema = dict()
        for col in columns:
            params = {}
            if optional:
                params["default"] = None
            elif self.datamodel.is_nullable(col):
                params["default"] = None
            # For relation, where the relation is one-to-one or many-to-one
            if self.datamodel.is_relation_one_to_one(
                col
            ) or self.datamodel.is_relation_many_to_one(col):
                related_interface = self.datamodel.get_related_interface(col)
                type = related_interface.id_schema | RelInfo
                if optional:
                    type = type | None
                if self.datamodel.is_nullable(col):
                    type = type | None
                rel_schema[col] = (
                    type,
                    Field(**params),
                )
            else:
                if not optional:
                    params["default"] = []
                type = (
                    List[self.datamodel.get_related_interface(col).id_schema]
                    | List[RelInfo]
                )
                if optional:
                    type = type | None
                if self.datamodel.is_nullable(col):
                    type = type | None
                related_interface = self.datamodel.get_related_interface(col)
                rel_schema[col] = (
                    type,
                    Field(**params),
                )

        new_schema_name = f"{self.__class__.__name__}-{schema.__name__}"
        new_schema = create_model(
            name or new_schema_name,
            **rel_schema,
            __base__=schema,
        )
        new_schema.model_config["extra"] = "forbid"
        return new_schema

    async def _generate_info_schema(self, permissions: List[str], db: AsyncSession):
        """
        Generates the information schema for the API based on the given permissions and database session.

        Args:
            permissions (List[str]): The list of permissions for the API.
            db (AsyncSession): The database session.

        Returns:
            InfoSchema: The calculated information schema for the API.
        """
        schema = self.info_return_schema()
        schema.permissions = permissions
        schema.add_columns = []
        schema.edit_columns = []
        schema.filters = {}

        for key, val in self.filter_options.items():
            val = await smart_run(val) if callable(val) else val
            schema.filter_options[key] = val

        rel_cache = {}

        for col in self.add_columns:
            filters = self.add_query_rel_fields.get(col)
            order_column, order_direction = self.order_rel_fields.get(col, (None, None))
            cache_key = f"{col}_{filters}_{order_column}_{order_direction}"
            col_info = rel_cache.get(cache_key)
            if not col_info:
                col_info = await smart_run(
                    self._get_column_info,
                    col,
                    db,
                    filters,
                    order_column,
                    order_direction,
                )
                rel_cache[cache_key] = col_info
            schema.add_columns.append(col_info)

        for col in self.edit_columns:
            filters = self.edit_query_rel_fields.get(col)
            order_column, order_direction = self.order_rel_fields.get(col, (None, None))
            cache_key = f"{col}_{filters}_{order_column}_{order_direction}"
            col_info = rel_cache.get(cache_key)
            if not col_info:
                col_info = await smart_run(
                    self._get_column_info,
                    col,
                    db,
                    filters,
                    order_column,
                    order_direction,
                )
                rel_cache[cache_key] = col_info
            schema.edit_columns.append(col_info)

        for col in self.search_columns:
            info = dict()
            filters = self.cache.get(f"info_filters_{col}", None)
            if not filters:
                filters = [
                    {"name": filter.name, "operator": filter.arg_name}
                    for filter in self.datamodel._filters.get(col)
                ]
                self.cache[f"info_filters_{col}"] = filters
            info["filters"] = filters
            info["label"] = self.label_columns.get(col)
            query_filters = self.search_query_rel_fields.get(col)
            order_column, order_direction = self.order_rel_fields.get(col, (None, None))
            cache_key = f"{col}_{query_filters}_{order_column}_{order_direction}"
            info["schema"] = rel_cache.get(cache_key)
            if not info["schema"]:
                info["schema"] = await smart_run(
                    self._get_column_info,
                    col,
                    db,
                    query_filters,
                    order_column,
                    order_direction,
                )
            schema.filters[col] = info

        return schema

    async def _get_column_info(
        self,
        col: str,
        db: AsyncSession,
        filters: List[Tuple[str, BaseFilter, Any]] | None = None,
        order_column: str | None = None,
        order_direction: str | None = None,
    ) -> ColumnInfo | ColumnRelationInfo:
        """
        Retrieves information about a column in the database table.

        Caches the column information to avoid repeated queries (Except for relations).

        Args:
            col (str): The name of the column.
            db (AsyncSession): The async db object for the database connection.
            filters (List[Tuple[str, BaseFilter, Any]], optional): The list of filters to apply to the column. Defaults to None.
            order_column (str, optional): The column to order by. Defaults to None.
            order_direction (str, optional): The direction to order by. Defaults to None.

        Returns:
            ColumnInfo | ColumnRelationInfo: An object containing information about the column.

        Raises:
            None

        """
        column_info = self.cache.get(f"column_info_{col}", {})
        if column_info:
            return column_info

        column_info = {
            "description": self.description_columns.get(col, ""),
            "label": self.label_columns.get(col, ""),
            "name": col,
            "required": not self.datamodel.is_nullable(col),
            "unique": self.datamodel.is_unique(col),
        }

        if self.datamodel.is_relation(col):
            type = "Related"
            if self.datamodel.is_relation_one_to_many(
                col
            ) or self.datamodel.is_relation_many_to_many(col):
                type = "RelatedList"
            related_interface = self.datamodel.get_related_interface(col)
            query = QueryManager(db, related_interface)
            await smart_run(
                query.add_options,
                page=0,
                page_size=self.max_page_size,
                order_column=order_column,
                order_direction=order_direction,
                filter_classes=filters,
            )
            related_items = await smart_run(query.execute)
            count = await smart_run(query.count, filter_classes=filters)
            values = []
            for item in related_items:
                if related_interface.is_pk_composite():
                    id = {
                        pk: getattr(item, pk) for pk in related_interface.get_pk_attrs()
                    }
                else:
                    id = getattr(item, related_interface.get_pk_attr())
                values.append({"id": id, "value": str(item)})
            column_info["count"] = count
            column_info["values"] = values
            column_info["type"] = type
            return ColumnRelationInfo(**column_info)
        else:
            column_info["type"] = self.datamodel.get_type_name(col)

        info = ColumnInfo(**column_info)
        self.cache[f"column_info_{col}"] = info
        return info

    async def _process_body(
        self, db: AsyncSession, body: BaseModel | Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process the body of the request by handling relations and returning a new body dictionary.

        Args:
            db (AsyncSession): The async db object for the database connection.
            body (BaseModel | Dict[str, Any]): The request body.

        Returns:
            Dict[str, Any]: The transformed body dictionary.

        Raises:
            HTTPException: If any related items are not found or if an item is not found for a one-to-one or many-to-one relation.
        """
        body_json = (
            body.model_dump(exclude_unset=True) if isinstance(body, BaseModel) else body
        )
        new_body = {}
        for key, value in body_json.items():
            # Return the value as is if it is not a relation
            if not self.datamodel.is_relation(key):
                new_body[key] = value
                continue

            if not value:
                if self.datamodel.is_relation_one_to_many(
                    key
                ) or self.datamodel.is_relation_many_to_many(key):
                    new_body[key] = []
                else:
                    new_body[key] = None
                continue

            related_interface = self.datamodel.get_related_interface(key)
            query = QueryManager(db, related_interface)
            related_items = None

            if isinstance(value, list):
                for val in value:
                    if isinstance(val, dict):
                        val = val.get("id")

                query.where_id_in(value)
                related_items = await smart_run(query.execute)
                # If the length is not equal, then some items were not found
                if len(related_items) != len(value):
                    raise HTTPException(
                        status_code=400, detail=f"Some items in {key} not found"
                    )

                new_body[key] = related_items
                continue

            if isinstance(value, dict):
                value = value.get("id")

            query.where_id(value)
            related_item = await smart_run(query.execute, many=False)
            if not related_item:
                raise HTTPException(400, detail=f"{key} not found")
            new_body[key] = related_item

        return new_body

    """
    -------------
     DEPENDENCIES
    -------------
    """

    @property
    def get_query_manager(self) -> Callable[..., QueryManager]:
        """
        Returns the query manager dependency.

        Returns:
            Callable[..., QueryManager]: The query manager dependency.
        """
        return get_query_manager(self.datamodel)

    """
    -----------------------------------------
         HELPER FUNCTIONS
    -----------------------------------------
    """

    def _gen_labels_columns(self, list_columns: List[str]) -> None:
        """
        Auto generates pretty label_columns from list of columns
        """
        for col in list_columns:
            if not self.label_columns.get(col):
                self.label_columns[col] = self._prettify_column(col)

    @staticmethod
    def _prettify_name(name: str) -> str:
        """
        Prettify pythonic variable name.

        For example, 'HelloWorld' will be converted to 'Hello World'

        :param name:
            Name to prettify.
        """
        return re.sub(r"(?<=.)([A-Z])", r" \1", name)

    @staticmethod
    def _prettify_column(name: str) -> str:
        """
        Prettify pythonic variable name.

        For example, 'hello_world' will be converted to 'Hello World'

        :param name:
            Name to prettify.
        """
        return re.sub("[._]", " ", name).title()
