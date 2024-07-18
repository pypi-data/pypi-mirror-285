from datetime import datetime
from typing import Any

from fastapi_users.db import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from .const import (
    API_TABLE,
    ASSOC_PERMISSION_API_ROLE_TABLE,
    ASSOC_USER_ROLE_TABLE,
    PERMISSION_API_TABLE,
    PERMISSION_TABLE,
    ROLE_TABLE,
    USER_TABLE,
)
from .model import Model, Table

permission_view_id = f"{PERMISSION_API_TABLE.replace('ab_', '')}_id"
view_menu_id = f"{API_TABLE.replace('ab_', '')}_id"

assoc_user_role = Table(
    ASSOC_USER_ROLE_TABLE,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey(f"{USER_TABLE}.id"), nullable=False),
    Column("role_id", Integer, ForeignKey(f"{ROLE_TABLE}.id"), nullable=False),
    UniqueConstraint("user_id", "role_id", name="user_role_unique"),
)

assoc_permission_api_role = Table(
    ASSOC_PERMISSION_API_ROLE_TABLE,
    Column("id", Integer, primary_key=True, index=True),
    Column("role_id", Integer, ForeignKey(f"{ROLE_TABLE}.id"), nullable=False),
    Column(
        permission_view_id,
        Integer,
        ForeignKey(f"{PERMISSION_API_TABLE}.id"),
        nullable=False,
    ),
    UniqueConstraint(
        "role_id",
        permission_view_id,
        name="role_permission_api_unique",
    ),
)


class PermissionApi(Model):
    __tablename__ = PERMISSION_API_TABLE
    __table_args__ = (UniqueConstraint(view_menu_id, "permission_id"),)
    id = Column(Integer, primary_key=True, index=True)

    api_id = Column(
        Integer,
        ForeignKey(f"{API_TABLE}.id"),
        name=view_menu_id,
        nullable=False,
    )
    api = relationship("Api", back_populates="permissions", lazy="selectin")

    permission_id = Column(
        Integer, ForeignKey(f"{PERMISSION_TABLE}.id"), nullable=False
    )
    permission = relationship("Permission", back_populates="apis", lazy="selectin")

    roles = relationship(
        "Role",
        secondary=assoc_permission_api_role,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"{self.permission} on {self.api}"


class Api(Model):
    __tablename__ = API_TABLE
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    permissions = relationship(PermissionApi, back_populates="api", lazy="selectin")

    def __eq__(self, other):
        return (isinstance(other, self.__class__)) and (self.name == other.name)

    def __neq__(self, other):
        return self.name != other.name

    def __repr__(self) -> str:
        return self.name


class Permission(Model):
    __tablename__ = PERMISSION_TABLE
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    apis = relationship(PermissionApi, back_populates="permission", lazy="selectin")

    def __repr__(self) -> str:
        return self.name


class Role(Model):
    __tablename__ = ROLE_TABLE
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    users = relationship(
        "User", secondary=assoc_user_role, back_populates="roles", lazy="selectin"
    )

    permissions = relationship(
        PermissionApi,
        secondary=assoc_permission_api_role,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return self.name


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Model):
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer, ForeignKey(f"{USER_TABLE}.id", ondelete="cascade"), nullable=False
    )
    user = relationship("User", back_populates="oauth_accounts")

    def __repr__(self) -> str:
        return f"{self.oauth_name} - {self.account_email}"


class User(Model):
    __tablename__ = USER_TABLE
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password = Column(String(1024), nullable=False)
    first_name = Column(String(64))
    last_name = Column(String(64))
    active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime)
    login_count = Column(Integer)
    fail_login_count = Column(Integer)
    created_on = Column(DateTime, default=lambda: datetime.now())
    changed_on = Column(DateTime, default=lambda: datetime.now())

    @declared_attr
    def created_by_fk(self):
        return Column(Integer, ForeignKey("ab_user.id"), default=self.get_user_id)

    @declared_attr
    def changed_by_fk(self):
        return Column(Integer, ForeignKey("ab_user.id"), default=self.get_user_id)

    oauth_accounts = relationship(
        "OAuthAccount", back_populates="user", lazy="selectin"
    )

    roles = relationship(
        Role, secondary=assoc_user_role, back_populates="users", lazy="selectin"
    )

    @classmethod
    def get_user_id(cls):
        try:
            from .globals import g

            return g.user.id
        except Exception:
            return None

    @property
    def hashed_password(self) -> str:
        return self.password

    @hashed_password.setter
    def hashed_password(self, value: str):
        self.password = value

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self):
        return self.active

    @property
    def is_verified(self):
        return True

    @is_verified.setter
    def is_verified(self, value: bool):
        pass

    @property
    def is_superuser(self):
        from .globals import g

        return any(role.name == g.admin_role for role in self.roles)

    @property
    def is_anonymous(self):
        return False

    def __repr__(self) -> str:
        return self.full_name

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        # Add email as username if username is not provided
        if not self.username:
            self.username = self.email
