import io
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, TemplateNotFound, select_autoescape
from sqlalchemy import and_, insert
from starlette.routing import _DefaultLifespan

# Import all submodules
from .auth import *
from .const import *
from .db import *
from .file_manager import *
from .filters import *
from .globals import *
from .hasher import *
from .manager import *
from .model import *
from .models import *
from .routers import *
from .schemas import *
from .types import *
from .utils import *
from .version import __version__

# Ignored submodules, so that some auth module can be replaced with custom implementation
# from .dependencies import *
# from .api import *
# from .apis import *
# from .decorators import *
# from .generic import *
# from .generic.api import *


class FastapiReactToolkit:
    """
    The main class for the `FastapiReactToolkit` library.

    This class provides a set of methods to initialize a FastAPI application, add APIs, manage permissions and roles,
    and initialize the database with permissions, APIs, roles, and their relationships.

    Args:
        `app` (FastAPI | None, optional): The FastAPI application instance. If set, the `initialize` method will be called with this instance. Defaults to None.
        `auth` (AuthDict | None, optional): The authentication configuration. Set this if you want to customize the authentication system. See the `AuthDict` type for more details. Defaults to None.
        `create_tables` (bool, optional): Whether to create tables in the database. Not needed if you use a migration system like Alembic. Defaults to False.
        `on_startup` (Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]], optional): Function to call when the app is starting up. Defaults to None.
        `on_shutdown` (Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]], optional): Function to call when the app is shutting down. Defaults to None.

    ## Example:

    ```python
    import logging

    from fastapi import FastAPI, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi_rtk import FastapiReactToolkit, User
    from fastapi_rtk.manager import UserManager

    from .base_data import add_base_data

    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    logging.getLogger().setLevel(logging.INFO)


    class CustomUserManager(UserManager):
        async def on_after_login(
            self,
            user: User,
            request: Request | None = None,
            response: Response | None = None,
        ) -> None:
            await super().on_after_login(user, request, response)
            print("User logged in: ", user)


    async def on_startup(app: FastAPI):
        await add_base_data()
        print("base data added")
        pass


    app = FastAPI(docs_url="/openapi/v1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:6006"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    toolkit = FastapiReactToolkit(
        auth={
            "user_manager": CustomUserManager,
            # "password_helper": FABPasswordHelper(),  #! Add this line to use old password hash
        },
        create_tables=True,
        on_startup=on_startup,
    )
    toolkit.config.from_pyfile("./app/config.py")
    toolkit.initialize(app)

    from .apis import *

    toolkit.mount()
    ```
    """

    app: FastAPI = None
    apis: list = None
    initialized: bool = False
    create_tables: bool = False
    on_startup: (
        Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
    ) = None
    on_shutdown: (
        Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
    ) = None
    _mounted = False

    def __init__(
        self,
        *,
        app: FastAPI | None = None,
        auth: AuthDict | None = None,
        create_tables: bool = False,
        on_startup: (
            Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
        ) = None,
        on_shutdown: (
            Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
        ) = None,
    ) -> None:
        if auth:
            for key, value in auth.items():
                setattr(g.auth, key, value)

        if app:
            self.initialize(app)

        self.create_tables = create_tables
        self.on_startup = on_startup
        self.on_shutdown = on_shutdown

    @ignore_in_migrate
    def initialize(self, app: FastAPI) -> None:
        """
        Initializes the FastAPI application.

        Args:
            app (FastAPI): The FastAPI application instance.

        Returns:
            None
        """
        if self.initialized:
            return

        self.initialized = True
        self.app = app
        self.apis = []

        self.pre_initialize()

        from .dependencies import set_global_user

        # Initialize the lifespan
        self._init_lifespan()

        # Add the GlobalsMiddleware
        self.app.add_middleware(GlobalsMiddleware)
        self.app.router.dependencies.append(Depends(set_global_user))

        # Add the APIs
        self._init_info_api()
        self._init_auth_api()
        self._init_users_api()
        self._init_roles_api()
        self._init_permissions_api()
        self._init_apis_api()
        self._init_permission_apis_api()

        # Add the JS manifest route
        self._init_js_manifest()

    @ignore_in_migrate
    def pre_initialize(self):
        """
        Function to be called before initializing the FastAPI application.

        Default implementation sets the auth configuration from the global configuration.
        """
        auth_keys = g.auth.keys()
        cookie_config: CookieConfig = {}
        cookie_strategy_config: JWTStrategyConfig = {}
        jwt_strategy_config: JWTStrategyConfig = {}
        for key, value in g.config.items():
            lower_key = key.lower()
            if lower_key in auth_keys:
                setattr(g.auth, lower_key, value)
            if lower_key in COOKIE_CONFIG_KEYS:
                cookie_config[lower_key] = value
            if lower_key in COOKIE_STRATEGY_KEYS:
                lower_key = lower_key.replace("cookie_", "")
                cookie_strategy_config[lower_key] = value
            if lower_key in JWT_STRATEGY_KEYS:
                lower_key = lower_key.replace("jwt_", "")
                jwt_strategy_config[lower_key] = value
            if lower_key in ROLE_KEYS:
                setattr(g, lower_key, value)

        if cookie_config:
            g.auth.cookie_config = cookie_config
        if cookie_strategy_config:
            g.auth.cookie_strategy_config = cookie_strategy_config
        if jwt_strategy_config:
            g.auth.jwt_strategy_config = jwt_strategy_config

    @ignore_in_migrate
    def add_api(self, api) -> None:
        """
        Adds the specified API to the FastAPI application.

        Parameters:
        - api (ModelRestApi): The API to be added.

        Returns:
        - None

        Raises:
        - ValueError: If the API is added after the `mount()` method is called.
        """
        if self._mounted:
            raise ValueError(
                "API Mounted after mount() was called, please add APIs before calling mount()"
            )

        from .api import ModelRestApi

        api = api if isinstance(api, ModelRestApi) else api()
        self.apis.append(api)
        api.integrate_router(self.app)
        api.toolkit = self

    @ignore_in_migrate
    def total_permissions(self) -> list[str]:
        """
        Returns the total list of permissions required by all APIs.

        Returns:
        - list[str]: The total list of permissions.
        """
        permissions = []
        for api in self.apis:
            permissions.extend(getattr(api, "permissions", []))
        return list(set(permissions))

    @ignore_in_migrate
    def mount(self):
        """
        Mounts the static and template folders specified in the configuration.

        PLEASE ONLY RUN THIS AFTER ALL APIS HAVE BEEN ADDED.
        """
        if self._mounted:
            return

        self._mounted = True
        self._mount_static_folder()
        self._mount_template_folder()

    @ignore_in_migrate
    def connect_to_database(self):
        """
        Connects to the database using the configured SQLAlchemy database URI.

        This method initializes the database session maker with the SQLAlchemy
        database URI specified in the configuration.

        Raises:
            ValueError: If the `SQLALCHEMY_DATABASE_URI` is not set in the configuration.
        """
        uri = g.config.get("SQLALCHEMY_DATABASE_URI")
        if not uri:
            raise ValueError("SQLALCHEMY_DATABASE_URI is not set in the configuration")

        binds = g.config.get("SQLALCHEMY_BINDS")
        session_manager.init_db(uri, binds)
        logger.info("Connected to database")
        logger.info(f"URI: {uri}")
        logger.info(f"Binds: {binds}")

    @ignore_in_migrate
    async def init_database(self):
        """
        Initializes the database by inserting permissions, APIs, roles, and their relationships.

        The initialization process is as follows:
        1. Inserts permissions into the database.
        2. Inserts APIs into the database.
        3. Inserts roles into the database.
        4. Inserts the relationship between permissions and APIs into the database.
        5. Inserts the relationship between permissions, APIs, and roles into the database.

        Returns:
            None
        """
        async with session_manager.session() as db:
            logger.info("INITIALIZING DATABASE")
            await self._insert_permissions(db)
            await self._insert_apis(db)
            await self._insert_roles(db)
            await self._associate_permission_with_api(db)
            await self._associate_permission_api_with_role(db)
            logger.info("DATABASE INITIALIZED")

    async def _insert_permissions(self, db: AsyncSession | Session):
        new_permissions = self.total_permissions()
        stmt = select(Permission).where(Permission.name.in_(new_permissions))
        result = await smart_run(db.scalars, stmt)
        existing_permissions = [permission.name for permission in result.all()]
        if len(new_permissions) == len(existing_permissions):
            return

        permission_objs = [
            Permission(name=permission)
            for permission in new_permissions
            if permission not in existing_permissions
        ]
        for permission in permission_objs:
            logger.info(f"ADDING PERMISSION {permission}")
            db.add(permission)
        await smart_run(db.commit)

    async def _insert_apis(self, db: AsyncSession | Session):
        new_apis = [api.__class__.__name__ for api in self.apis]
        stmt = select(Api).where(Api.name.in_(new_apis))
        result = await smart_run(db.scalars, stmt)
        existing_apis = [api.name for api in result.all()]
        if len(new_apis) == len(existing_apis):
            return

        api_objs = [Api(name=api) for api in new_apis if api not in existing_apis]
        for api in api_objs:
            logger.info(f"ADDING API {api}")
            db.add(api)
        await smart_run(db.commit)

    async def _insert_roles(self, db: AsyncSession | Session):
        new_roles = [g.admin_role, g.public_role]
        stmt = select(Role).where(Role.name.in_(new_roles))
        result = await smart_run(db.scalars, stmt)
        existing_roles = [role.name for role in result.all()]
        if len(new_roles) == len(existing_roles):
            return

        role_objs = [
            Role(name=role) for role in new_roles if role not in existing_roles
        ]
        for role in role_objs:
            logger.info(f"ADDING ROLE {role}")
            db.add(role)
        await smart_run(db.commit)

    async def _associate_permission_with_api(self, db: AsyncSession | Session):
        for api in self.apis:
            new_permissions = getattr(api, "permissions", [])
            if not new_permissions:
                continue

            # Get the api object
            api_stmt = select(Api).where(Api.name == api.__class__.__name__)
            api_result = await smart_run(db.scalars, api_stmt)
            api_obj = api_result.first()

            if not api_obj:
                raise ValueError(f"API {api.__class__.__name__} not found")

            permission_stmt = select(Permission).where(
                and_(
                    Permission.name.in_(new_permissions),
                    ~Permission.id.in_([p.permission_id for p in api_obj.permissions]),
                )
            )
            permission_result = await smart_run(db.scalars, permission_stmt)
            new_permissions = permission_result.all()

            if not new_permissions:
                continue

            for permission in new_permissions:
                permission_api_stmt = insert(PermissionApi).values(
                    permission_id=permission.id, api_id=api_obj.id
                )
                await smart_run(db.execute, permission_api_stmt)
                logger.info(f"ASSOCIATING PERMISSION {permission} WITH API {api_obj}")
            await smart_run(db.commit)

    async def _associate_permission_api_with_role(self, db: AsyncSession | Session):
        # Read config based roles
        roles_dict = g.config.get("ROLES") or g.config.get("FAB_ROLES", {})
        admin_ignored_apis: list[str] = []

        for role_name, role_permissions in roles_dict.items():
            role_stmt = select(Role).where(Role.name == role_name)
            role_result = await smart_run(db.scalars, role_stmt)
            role = role_result.first()
            if not role:
                role = Role(name=role_name)
                logger.info(f"ADDING ROLE {role}")
                db.add(role)

            for api_name, permission_name in role_permissions:
                admin_ignored_apis.append(api_name)
                permission_api_stmt = (
                    select(PermissionApi)
                    .where(
                        and_(Api.name == api_name, Permission.name == permission_name)
                    )
                    .join(Permission)
                    .join(Api)
                )
                permission_api_result = await smart_run(db.execute, permission_api_stmt)
                permission_api: PermissionApi | None = (
                    permission_api_result.scalar_one_or_none()
                )
                if not permission_api:
                    permission_stmt = select(Permission).where(
                        Permission.name == permission_name
                    )
                    permission_result = await smart_run(db.execute, permission_stmt)
                    permission: Permission | None = (
                        permission_result.scalar_one_or_none()
                    )
                    if not permission:
                        permission = Permission(name=permission_name)
                        logger.info(f"ADDING PERMISSION {permission}")
                        db.add(permission)

                    stmt = select(Api).where(Api.name == api_name)
                    result = await smart_run(db.execute, stmt)
                    api: Api | None = result.scalar_one_or_none()
                    if not api:
                        api = Api(name=api_name)
                        logger.info(f"ADDING API {api}")
                        db.add(api)

                    permission_api = PermissionApi(permission=permission, api=api)
                    logger.info(f"ADDING PERMISSION-API {permission_api}")
                    db.add(permission_api)

                # Associate role with permission-api
                if role not in permission_api.roles:
                    permission_api.roles.append(role)
                    logger.info(
                        f"ASSOCIATING {role} WITH PERMISSION-API {permission_api}"
                    )

                await smart_run(db.commit)

        # Get admin role
        admin_role_stmt = select(Role).where(Role.name == g.admin_role)
        admin_role_result = await smart_run(db.execute, admin_role_stmt)
        admin_role: Role | None = admin_role_result.scalar_one_or_none()

        if admin_role:
            # Get list of permission-api.assoc_permission_api_id of the admin role
            stmt = (
                select(PermissionApi)
                .where(
                    and_(
                        ~PermissionApi.roles.contains(admin_role),
                        ~Api.name.in_(admin_ignored_apis),
                    )
                )
                .join(Api)
            )
            result = await smart_run(db.scalars, stmt)
            existing_assoc_permission_api_roles = result.all()

            # Add admin role to all permission-api objects
            for permission_api in existing_assoc_permission_api_roles:
                permission_api.roles.append(admin_role)
                logger.info(
                    f"ASSOCIATING {admin_role} WITH PERMISSION-API {permission_api}"
                )
            await smart_run(db.commit)

    def _mount_static_folder(self):
        """
        Mounts the static folder specified in the configuration.

        Returns:
            None
        """
        # If the folder does not exist, create it
        os.makedirs(g.config.get("STATIC_FOLDER", DEFAULT_STATIC_FOLDER), exist_ok=True)

        static_folder = g.config.get("STATIC_FOLDER", DEFAULT_STATIC_FOLDER)
        self.app.mount("/static", StaticFiles(directory=static_folder), name="static")

    def _mount_template_folder(self):
        """
        Mounts the template folder specified in the configuration.

        Returns:
            None
        """
        # If the folder does not exist, create it
        os.makedirs(
            g.config.get("TEMPLATE_FOLDER", DEFAULT_TEMPLATE_FOLDER), exist_ok=True
        )

        templates = Jinja2Templates(
            directory=g.config.get("TEMPLATE_FOLDER", DEFAULT_TEMPLATE_FOLDER)
        )

        @self.app.get("/{full_path:path}", response_class=HTMLResponse)
        def index(request: Request):
            try:
                return templates.TemplateResponse(
                    request=request,
                    name="index.html",
                    context={"base_path": g.config.get("BASE_PATH", "/")},
                )
            except TemplateNotFound:
                raise HTTPException(status_code=404, detail="Not Found")

    """
    -----------------------------------------
         INIT FUNCTIONS
    -----------------------------------------
    """

    def _init_lifespan(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Run when the app is starting up
            self.connect_to_database()

            if self.create_tables:
                await session_manager.create_all()

            # Creating permission, apis, roles, and connecting them
            await self.init_database()

            # On startup
            if self.on_startup:
                if inspect.iscoroutinefunction(self.on_startup):
                    await self.on_startup(app)
                else:
                    self.on_startup(app)

            yield

            # On shutdown
            if self.on_shutdown:
                if inspect.iscoroutinefunction(self.on_shutdown):
                    await self.on_shutdown(app)
                else:
                    self.on_shutdown(app)

            # Run when the app is shutting down
            await session_manager.close()

        # Check whether lifespan is already set
        if not isinstance(self.app.router.lifespan_context, _DefaultLifespan):
            raise ValueError(
                "Lifespan already set, please do not set lifespan directly in the FastAPI app"
            )

        self.app.router.lifespan_context = lifespan

    def _init_info_api(self):
        from .apis import InfoApi

        self.add_api(InfoApi)

    def _init_auth_api(self):
        from .apis import AuthApi

        self.add_api(AuthApi)

    def _init_users_api(self):
        from .apis import UsersApi

        self.add_api(UsersApi)

    def _init_roles_api(self):
        from .apis import RolesApi

        self.add_api(RolesApi)

    def _init_permissions_api(self):
        from .apis import PermissionsApi

        self.add_api(PermissionsApi)

    def _init_apis_api(self):
        from .apis import ViewsMenusApi

        self.add_api(ViewsMenusApi)

    def _init_permission_apis_api(self):
        from .apis import PermissionViewApi

        self.add_api(PermissionViewApi)

    def _init_js_manifest(self):
        @self.app.get("/server-config.js", response_class=StreamingResponse)
        def js_manifest():
            env = Environment(autoescape=select_autoescape(["html", "xml"]))
            template_string = "window.fab_react_config = {{ react_vars |tojson }}"
            template = env.from_string(template_string)
            rendered_string = template.render(
                react_vars=json.dumps(g.config.get("FAB_REACT_CONFIG", {}))
            )
            content = rendered_string.encode("utf-8")
            scriptfile = io.BytesIO(content)
            return StreamingResponse(
                scriptfile,
                media_type="application/javascript",
            )

    """
    -----------------------------------------
         PROPERTY FUNCTIONS
    -----------------------------------------
    """

    @property
    def config(self):
        return g.config
