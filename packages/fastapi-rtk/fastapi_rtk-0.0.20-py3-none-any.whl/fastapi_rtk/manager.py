import inspect
from datetime import UTC, datetime
from typing import Any, Callable, Optional

from fastapi import HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, exceptions
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import PasswordHelperProtocol
from sqlalchemy import select

from .db import UserDatabase
from .models import Role, User
from .schemas import UserCreate


class IDParser:
    def parse_id(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except ValueError as e:
            raise exceptions.InvalidID() from e


class UserManager(IDParser, BaseUserManager[User, int]):
    user_db: UserDatabase

    def __init__(
        self,
        user_db: BaseUserDatabase[User, int],
        secret_key: str,
        password_helper: PasswordHelperProtocol | None = None,
    ):
        super().__init__(user_db, password_helper)
        self.reset_password_token_secret = secret_key
        self.verification_token_secret = secret_key

    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by its username.

        :param username: The username of the user.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_username(username)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> User | None:
        """
        Override the default authenticate method to search by username instead of email.

        Args:
            credentials (OAuth2PasswordRequestForm): The credentials to authenticate the user.

        Returns:
            User | None: The user if the credentials are valid, None otherwise.
        """
        try:
            user = await self.get_by_username(credentials.username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            await self.user_db.update(
                user, {"fail_login_count": (user.fail_login_count or 0) + 1}
            )
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        await self.user_db.update(user, {"fail_login_count": 0})
        return user

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Modified version of the default `create` method to add roles to the user during creation.

        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        # Get the roles if they exist
        roles = user_dict.get("roles", [])
        if roles:
            stmt = select(Role).where(Role.name.in_(roles))
            result = await self.user_db.session.execute(stmt)
            roles = result.scalars().all()
            if len(roles) != len(user_dict["roles"]):
                raise Exception("One or more roles do not exist.")
            user_dict["roles"] = roles

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def oauth_callback(
        self,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: int | None = None,
        refresh_token: str | None = None,
        request: Request | None = None,
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = False,
        on_after_register: Optional[Callable[[User, str], Any]] = None,
    ) -> User:
        """
        Modified version of the default `oauth_callback` method to allow custom on_after_register handler.

        Handle the callback after a successful OAuth authentication.

        If the user already exists with this OAuth account, the token is updated.

        If a user with the same e-mail already exists and `associate_by_email` is True,
        the OAuth account is associated to this user.
        Otherwise, the `UserNotExists` exception is raised.

        If the user does not exist, it is created and the on_after_register handler
        is triggered.

        :param oauth_name: Name of the OAuth client.
        :param access_token: Valid access token for the service provider.
        :param account_id: models.ID of the user on the service provider.
        :param account_email: E-mail of the user on the service provider.
        :param expires_at: Optional timestamp at which the access token expires.
        :param refresh_token: Optional refresh token to get a
        fresh access token from the service provider.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :param associate_by_email: If True, any existing user with the same
        e-mail address will be associated to this user. Defaults to False.
        :param is_verified_by_default: If True, the `is_verified` flag will be
        set to `True` on newly created user. Make sure the OAuth Provider you're
        using does verify the email address before enabling this flag.
        Defaults to False.
        :param on_after_register: Optional callback to be executed after a new user is registered.
        :return: A user.
        """
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }

        try:
            user = await self.get_by_oauth_account(oauth_name, account_id)
        except exceptions.UserNotExists:
            try:
                # Associate account
                user = await self.get_by_email(account_email)
                if not associate_by_email:
                    raise exceptions.UserAlreadyExists()
                user = await self.user_db.add_oauth_account(user, oauth_account_dict)
            except exceptions.UserNotExists:
                # Create account
                password = self.password_helper.generate()
                user_dict = {
                    "email": account_email,
                    "hashed_password": self.password_helper.hash(password),
                    "is_verified": is_verified_by_default,
                }
                user = await self.user_db.create(user_dict)
                user = await self.user_db.add_oauth_account(user, oauth_account_dict)
                if on_after_register:
                    if inspect.iscoroutinefunction(on_after_register):
                        await on_after_register(user, access_token)
                    else:
                        on_after_register(user, access_token)
                await self.on_after_register(user, request)
        else:
            # Update oauth
            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == account_id
                    and existing_oauth_account.oauth_name == oauth_name
                ):
                    user = await self.user_db.update_oauth_account(
                        user, existing_oauth_account, oauth_account_dict
                    )

        return user

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        """
        Perform logic after user login.

        Please call await super().on_after_login(user, request, response) to keep the default behavior.

        *You should overload this method to add your own logic.*

        :param user: The user that is logging in
        :param request: Optional FastAPI request
        :param response: Optional response built by the transport.
        Defaults to None
        """
        update_fields = {
            "last_login": datetime.now(UTC),
            "login_count": (user.login_count or 0) + 1,
        }
        await self.user_db.update(user, update_fields)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        raise HTTPException(status_code=501, detail="Not implemented")

    async def on_after_reset_password(
        self, user: User, request: Request | None = None
    ) -> None:
        raise HTTPException(status_code=501, detail="Not implemented")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        raise HTTPException(status_code=501, detail="Not implemented")
