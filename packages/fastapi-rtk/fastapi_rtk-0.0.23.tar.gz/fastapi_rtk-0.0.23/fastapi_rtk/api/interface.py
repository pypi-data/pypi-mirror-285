from datetime import date, datetime
from typing import Any, List, Optional, Type

from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy import Column
from sqlalchemy.orm import SynonymProperty, class_mapper
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.sql import sqltypes as sa_types
from sqlalchemy_utils.types.uuid import UUIDType

from ..db import QueryManager
from ..filters import BaseFilter, SQLAFilterConverter
from ..models import Model
from ..schemas import PRIMARY_KEY, DatetimeUTC, QuerySchema
from ..types import FileColumn, ImageColumn


def _is_sqla_type(model: Model, sa_type: Type[sa_types.TypeEngine]) -> bool:
    return (
        isinstance(model, sa_type)
        or isinstance(model, sa_types.TypeDecorator)
        and isinstance(model.impl, sa_type)
    )


class Params(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: PRIMARY_KEY | None = None
    ids: List[PRIMARY_KEY] | None = None
    q: QuerySchema | None = None
    query: QueryManager | None = None
    body: BaseModel | None = None
    item: Model | Any | None = None
    items: List[Model | Any] | None = None
    extra: Any | None = None


class SQLAInterface:
    """
    Represents an interface for a SQLAlchemy model. It provides methods for creating a pydantic schema for the model, as well as for testing the types of the model's columns.
    """

    obj: Model
    id_schema: str | int = int
    schema: Type[BaseModel]
    """
    The pydantic schema for the model. This is the standard schema. If the field is optional, it will be set to None as default.
    """
    schema_optional: Type[BaseModel]
    """
    The pydantic schema for the model. This is the standard schema, but all fields are optional. Useful for POST and PUT requests.
    """
    filter_converter: SQLAFilterConverter = SQLAFilterConverter()

    list_columns: dict[str, Column]
    list_properties: dict[str, Column]
    with_fk: bool

    _filters: dict[str, list[BaseFilter]] = None

    def __init__(self, obj: Model, with_fk: bool = True):
        self.obj = obj
        self.with_fk = with_fk
        self._init_properties()
        self.schema = self.generate_schema(self.list_properties.keys())
        self.schema_optional = self.generate_schema(
            self.list_properties.keys(), optional=True
        )
        self._init_filters()

    def generate_schema(
        self,
        columns: List[str] | None = None,
        with_name_=True,
        optional=False,
        name: str | None = None,
    ) -> Type[BaseModel]:
        """
        Generate a Pydantic schema based on the object's properties.

        Args:
            columns (List[str], optional): A list of columns to include in the schema. Returns an empty schema if not specified. Defaults to None.
            with_name_ (bool, optional): Whether to include the name_ column. Defaults to True.
            optional (bool, optional): Whether the columns should be optional. Required for PUT or PATCH requests. Defaults to False.
            name (str, optional): The name of the schema. Defaults to None.

        Returns:
            BaseModel: The Pydantic schema for the object.
        """
        model_name = f"{self.obj.__name__}-Schema"
        if optional:
            model_name += "-Optional"
        model_name = name or model_name
        schema_dict = {
            "__config__": ConfigDict(from_attributes=True),
        }

        if with_name_:
            schema_dict["name_"] = (str, Field())

        if not columns:
            return create_model(model_name, **schema_dict)

        self._generate_schema_properties(columns, optional, schema_dict)

        if self.is_pk_composite():
            self.id_schema = str

        return create_model(model_name, **schema_dict)

    def get_type(self, col: str, optional: bool = False) -> Type:
        """
        Get the Python type corresponding to the specified column name.

        Args:
            col (str): The name of the column.
            optional (bool, optional): Whether the column should be optional. Only works for related models. Defaults to False.

        Returns:
            Type: The Python type corresponding to the column.

        """
        if self.is_text(col) or self.is_string(col):
            return str
        elif self.is_integer(col):
            return int
        elif self.is_numeric(col) or self.is_float(col):
            return float
        elif self.is_boolean(col):
            return bool
        elif self.is_date(col):
            return date
        elif self.is_datetime(col):
            return DatetimeUTC | datetime
        elif self.is_relation(col):
            schema = (
                self.get_related_interface(col, with_fk=False).schema
                if not optional
                else self.get_related_interface(col, with_fk=False).schema_optional
            )
            if self.is_relation_one_to_one(col) or self.is_relation_many_to_one(col):
                return schema
            return list[schema]
        else:
            return Any

    def get_type_name(self, col: str) -> str:
        """
        Get the name of the Python type corresponding to the specified column name.

        Args:
            col (str): The name of the column.

        Returns:
            str: The name of the Python type corresponding to the column.

        """
        name = self.list_columns[col].type.__class__.__name__
        if name == "JSON":
            return "Raw"
        return name

    def get_pk_attr(self) -> str:
        """
        Returns the name of the primary key attribute for the object.

        Returns:
            str: The name of the primary key attribute.
        """
        for key in self.list_columns.keys():
            if self.is_pk(key):
                return key

    def get_pk_attrs(self) -> List[str]:
        """
        Returns the names of the primary key attributes for the object.

        Returns:
            List[str]: The names of the primary key attributes.
        """
        return [key for key in self.list_columns.keys() if self.is_pk(key)]

    def _init_properties(self):
        """
        Initialize the properties of the object.

        This method initializes the properties of the object by creating a dictionary of the object's columns and their corresponding types.

        Returns:
            None
        """
        self.list_columns = dict()
        self.list_properties = dict()
        for prop in class_mapper(self.obj).iterate_properties:
            if type(prop) != SynonymProperty:
                self.list_properties[prop.key] = prop
        for col_name in self.obj.__mapper__.columns.keys():
            if col_name in self.list_properties:
                self.list_columns[col_name] = self.obj.__mapper__.columns[col_name]

    def _init_filters(self):
        """
        Initializes the filters dictionary by iterating over the keys of the `list_properties` dictionary.
        For each key, it checks if the class has the corresponding attribute specified in the `conversion_table`
        of the `filter_converter` object. If the attribute exists, it adds the corresponding filters to the
        `_filters` dictionary.

        Parameters:
            None

        Returns:
            None
        """
        self._filters = dict()
        for col in self.list_properties.keys():
            if self.is_pk(col):
                continue

            for func_attr, filters in self.filter_converter.conversion_table:
                if getattr(self, func_attr)(col):
                    self._filters[col] = filters
                    break

    """
    ------------------------------
     FUNCTIONS FOR RELATED MODELS
    ------------------------------
    """

    def get_col_default(self, col_name: str) -> Any:
        default = getattr(self.list_columns[col_name], "default", None)
        if default is None:
            return None

        value = getattr(default, "arg", None)
        if value is None:
            return None

        if getattr(default, "is_callable", False):
            return lambda: default.arg(None)

        if not getattr(default, "is_scalar", True):
            return None

        return value

    def get_related_model(self, col_name: str) -> Model:
        return self.list_properties[col_name].mapper.class_

    def get_related_interface(self, col_name: str, with_fk: bool | None = None):
        return self.__class__(self.get_related_model(col_name), with_fk)

    def get_related_fk(self, model: Model) -> Optional[str]:
        for col_name in self.list_properties.keys():
            if self.is_relation(col_name):
                if model == self.get_related_model(col_name):
                    return col_name
        return None

    def get_related_fks(self) -> List[str]:
        return [
            self.get_related_fk(model)
            for model in self.list_properties.values()
            if self.is_relation(model)
        ]

    def get_info(self, col_name: str):
        if col_name in self.list_properties:
            return self.list_properties[col_name].info
        return {}

    """
    -------------
     GET METHODS
    -------------
    """

    def get_columns_list(self) -> List[str]:
        """
        Returns all model's columns on SQLA properties
        """
        return list(self.list_properties.keys())

    def get_user_columns_list(self) -> List[str]:
        """
        Returns all model's columns except pk or fk
        """
        return [
            col_name
            for col_name in self.get_columns_list()
            if (not self.is_pk(col_name)) and (not self.is_fk(col_name))
        ]

    def get_property_column_list(self) -> List[str]:
        """
        Returns all model's columns that have @property decorator and is public
        """
        self_dict = vars(self.obj)
        return [
            key
            for key in self_dict.keys()
            if self.is_property(key) and not key.startswith("_")
        ]

    def get_search_columns_list(self) -> List[str]:
        ret_lst = []
        for col_name in self.get_columns_list():
            if not self.is_relation(col_name):
                tmp_prop = self.get_property_first_col(col_name).name
                if (
                    (not self.is_pk(tmp_prop))
                    and (not self.is_fk(tmp_prop))
                    and (not self.is_image(col_name))
                    and (not self.is_file(col_name))
                ):
                    ret_lst.append(col_name)
            else:
                ret_lst.append(col_name)
        return ret_lst

    def get_order_columns_list(
        self, list_columns: List[str] = None, depth=0
    ) -> List[str]:
        """
        Get all columns that can be used for ordering

        Args:
            list_columns (List[str], optional): Columns to be used for ordering. Defaults to None.
            depth (int, optional): Depth of the relation. Defaults to 0. Used for recursive calls.

        Returns:
            List[str]: List of columns that can be used for ordering
        """
        ret_lst = []
        list_columns = list_columns or self.get_columns_list()

        for col_name in list_columns:
            if self.is_relation(col_name):
                if (
                    depth > 0
                    or self.is_relation_one_to_many(col_name)
                    or self.is_relation_many_to_many(col_name)
                ):
                    continue
                related_interface = self.get_related_interface(col_name)
                ret_lst.extend(
                    [
                        f"{col_name}.{sub_col}"
                        for sub_col in related_interface.get_order_columns_list(
                            depth=depth + 1
                        )
                    ]
                )
                continue

            if hasattr(self.obj, col_name):
                attribute = getattr(self.obj, col_name)
                if not callable(attribute) or hasattr(attribute, "_col_name"):
                    ret_lst.append(col_name)
            else:
                ret_lst.append(col_name)

        return ret_lst

    def get_file_column_list(self) -> List[str]:
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, FileColumn)
        ]

    def get_image_column_list(self) -> List[str]:
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, ImageColumn)
        ]

    def get_property_first_col(self, col_name: str) -> ColumnProperty:
        # support for only one col for pk and fk
        return self.list_properties[col_name].columns[0]

    def get_relation_fk(self, col_name: str) -> Column:
        # support for only one col for pk and fk
        return list(self.list_properties[col_name].local_columns)[0]

    """
    -----------------------------------------
         FUNCTIONS for Testing TYPES
    -----------------------------------------
    """

    def is_image(self, col_name: str) -> bool:
        try:
            return isinstance(self.list_columns[col_name].type, ImageColumn)
        except KeyError:
            return False

    def is_file(self, col_name: str) -> bool:
        try:
            return isinstance(self.list_columns[col_name].type, FileColumn)
        except KeyError:
            return False

    def is_string(self, col_name: str) -> bool:
        try:
            return (
                _is_sqla_type(self.list_columns[col_name].type, sa_types.String)
                or self.list_columns[col_name].type.__class__ == UUIDType
            )
        except KeyError:
            return False

    def is_text(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Text)
        except KeyError:
            return False

    def is_binary(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.LargeBinary)
        except KeyError:
            return False

    def is_integer(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Integer)
        except KeyError:
            return False

    def is_numeric(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Numeric)
        except KeyError:
            return False

    def is_float(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Float)
        except KeyError:
            return False

    def is_boolean(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Boolean)
        except KeyError:
            return False

    def is_date(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Date)
        except KeyError:
            return False

    def is_datetime(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.DateTime)
        except KeyError:
            return False

    def is_enum(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.Enum)
        except KeyError:
            return False

    def is_json(self, col_name: str) -> bool:
        try:
            return _is_sqla_type(self.list_columns[col_name].type, sa_types.JSON)
        except KeyError:
            return False

    def is_relation(self, col_name: str) -> bool:
        try:
            return isinstance(self.list_properties[col_name], RelationshipProperty)
        except KeyError:
            return False

    def is_relation_many_to_one(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "MANYTOONE"
            return False
        except KeyError:
            return False

    def is_relation_many_to_many(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "MANYTOMANY"
            return False
        except KeyError:
            return False

    def is_relation_many_to_many_special(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "ONETOONE" and relation.uselist
            return False
        except KeyError:
            return False

    def is_relation_one_to_one(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return self.list_properties[col_name].direction.name == "ONETOONE" or (
                    relation.direction.name == "ONETOMANY" and relation.uselist is False
                )
            return False
        except KeyError:
            return False

    def is_relation_one_to_many(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "ONETOMANY" and relation.uselist
            return False
        except KeyError:
            return False

    def is_nullable(self, col_name: str) -> bool:
        if self.is_relation_many_to_one(col_name):
            col = self.get_relation_fk(col_name)
            return col.nullable
        elif self.is_relation_many_to_many(col_name) or self.is_relation_one_to_many(
            col_name
        ):
            return True
        try:
            return self.list_columns[col_name].nullable
        except KeyError:
            return False

    def is_unique(self, col_name: str) -> bool:
        try:
            return self.list_columns[col_name].unique is True
        except KeyError:
            return False

    def is_pk(self, col_name: str) -> bool:
        try:
            return self.list_columns[col_name].primary_key
        except KeyError:
            return False

    def is_pk_composite(self) -> bool:
        return len(self.obj.__mapper__.primary_key) > 1

    def is_fk(self, col_name: str) -> bool:
        try:
            return self.list_columns[col_name].foreign_keys
        except KeyError:
            return False

    def is_property(self, col_name: str) -> bool:
        return hasattr(getattr(self.obj, col_name), "fget")

    def is_function(self, col_name: str) -> bool:
        return hasattr(getattr(self.obj, col_name), "__call__")

    def is_property_or_function(self, col_name: str) -> bool:
        return self.is_property(col_name) or self.is_function(col_name)

    def get_max_length(self, col_name: str) -> int:
        try:
            if self.is_enum(col_name):
                return -1
            col = self.list_columns[col_name]
            if col.type.length:
                return col.type.length
            else:
                return -1
        except Exception:
            return -1

    def _generate_schema_properties(
        self,
        columns: List[str],
        optional: bool,
        schema_dict: dict[str, Any],
    ):
        """
        Generate schema properties based on the given columns and options.

        Args:
            columns (List[str]): The list of columns to include in the schema properties.
            optional (bool): Flag indicating whether the properties should be optional.
            schema_dict (dict[str, Any]): The dictionary to store the generated schema properties.

        Returns:
            None
        """
        prop_dict = self.list_properties if self.with_fk else self.list_columns
        for key, column in prop_dict.items():
            # Ignore it if it is a fk or not in the list of columns
            if self.is_fk(key) or key not in columns:
                continue

            params = {}
            type = self.get_type(key, optional)
            if hasattr(column, "primary_key") and column.primary_key:
                self.id_schema = type
            if self.is_nullable(key) or optional:
                params["default"] = None
                type = type | None
            if self.get_max_length(key) != -1:
                params["max_length"] = self.get_max_length(key)
            schema_dict[key] = (type, Field(**params))
