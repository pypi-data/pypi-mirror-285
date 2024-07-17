from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .const import PERMISSION_PREFIX
from .db import QueryManager, get_db
from .globals import g
from .models import PermissionApi, User

current_active_user = g.auth.fastapi_users.current_user(active=True)
current_user_or_none = g.auth.fastapi_users.current_user(
    active=True, default_to_none=True
)


async def set_global_user(user: User | None = Depends(current_user_or_none)):
    """
    Sets the global user for the application.

    To be used as a dependency in FastAPI routers.
    """
    g.user = user


def permissions(as_object=False):
    """
    A dependency for FAST API to list all the apis that the current user has access to.

    Usage:
    ```python
    async def get_info(
            *,
            permissions: List[str] = Depends(permissions()),
            db: AsyncSession = Depends(get_async_session),
        ):
    ...more code
    ```

    Args:
        as_object (bool): Whether to return the permission objects or just the names.

    """

    async def permissions_depedency(
        user: User = Depends(current_active_user),
    ):
        if not user.roles:
            raise HTTPException(status_code=403, detail="Forbidden")

        permissions = []
        for role in user.roles:
            for permission_api in role.permissions:
                if as_object:
                    permissions.append(permission_api)
                else:
                    permissions.append(permission_api.api.name)
        permissions = list(set(permissions))

        return permissions

    return permissions_depedency


def current_permissions(api):
    """
    A dependency for FAST API to list all the permissions of current user in the specified API.

    Usage:
    ```python
    async def get_info(
            *,
            permissions: List[str] = Depends(current_permissions(self)),
            db: AsyncSession = Depends(get_async_session),
        ):
    ...more code
    ```

    Args:
        api (ModelRestApi): The API to be checked.
    """

    async def current_permissions_depedency(
        permissions_apis: list[PermissionApi] = Depends(permissions(as_object=True)),
    ):
        permissions = []
        for permission_api in permissions_apis:
            if api.__class__.__name__ in permission_api.api.name:
                permissions = permissions + permission_api.permission.name.split("|")
        return permissions

    return current_permissions_depedency


def has_access_dependency(
    api,
    permission: str,
):
    """
    A dependency for FAST API to check whether current user has access to the specified API and permission.

    Usage:
    ```python
    @self.router.get(
            "/_info",
            response_model=self.info_return_schema,
            dependencies=[
                Depends(current_active_user),
                Depends(has_access(self, "info")),
            ],
        )
    ...more code
    ```

    Args:
        api (ModelRestApi): The API to be checked.
        permission (str): The permission to check.
    """

    async def check_permission(
        permissions: list[str] = Depends(current_permissions(api)),
    ):
        if f"{PERMISSION_PREFIX}{permission}" not in permissions:
            raise HTTPException(status_code=403, detail="Forbidden")
        return

    return check_permission


def get_query_manager(interface, generic: bool = False):
    """
    Returns a dependency function that provides a query manager based on the given interface.

    Usage:
    ```python
    @self.router.get(
            "/_info",
            response_model=self.info_return_schema,
            dependencies=[
                Depends(get_query_manager(self.interface)),
            ],
        )
    ...more code
    ```

    Args:
        interface (SQLAInterface | GenericInterface): The interface to be used for the query manager.
        generic (bool, optional): Specifies whether to use a generic query manager. Defaults to False.

    Returns:
        Callable: A dependency function that provides a query manager based on the given interface.
    """

    bind_key = getattr(interface.obj, "__bind_key__", None)

    def get_query_manager_dependency(
        db: AsyncSession = Depends(get_db(bind_key)),
    ):
        if generic:
            from .generic.db import GenericQueryManager

            return GenericQueryManager(db, interface, interface.session)
        return QueryManager(db, interface)

    return get_query_manager_dependency
