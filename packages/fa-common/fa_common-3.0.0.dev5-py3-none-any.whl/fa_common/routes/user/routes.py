from typing import List

from fastapi import APIRouter, Security
from fastapi.security import SecurityScopes

from fa_common import AuthType, DatabaseError, ForbiddenError, NotFoundError, UnknownError, get_settings
from fa_common import logger as LOG
from fa_common.auth import AuthUser
from fa_common.models import Message
from fa_common.routes.user.models import UpdateUser, UpdateUserMe, UserDB
from fa_common.routes.user.service import create_user, delete_user, find_users, get_current_app_user, update_user

if get_settings().AUTH_TYPE is AuthType.STANDALONE:
    LOG.info("Using Standalone AuthType")
    from fa_common.auth import get_standalone_user as get_current_user
else:
    from fa_common.auth import get_current_user  # type: ignore


router = APIRouter()


@router.get("/me", response_model=UserDB, response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def read_user_me(
    create: bool = False,
    current_user: AuthUser = Security(get_current_user),
) -> UserDB:
    """
    Read the logged in user can optionally create the Licence user
    record from the AAD user record if it doesn't exist

    Returns:
        [LicenceUser] -- [Current User]
    """
    try:
        app_user = await get_current_app_user(security_scopes=SecurityScopes(), current_user=current_user)
    except NotFoundError as err:
        if create:
            return await create_user(current_user)
        raise err from err
    LOG.debug(app_user)
    return app_user


@router.patch("/me", response_model=UserDB, response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def update_user_me(
    user_in: UpdateUserMe,
    current_user: UserDB = Security(get_current_app_user),
) -> UserDB:
    """Update the logged in user

    Returns:
        [type] -- [description]
    """
    try:
        return await update_user(current_user, update_data=user_in.model_dump(exclude_unset=True))
    except DatabaseError as err:
        raise UnknownError(detail=err) from err


@router.delete("/me", response_model=Message)
async def delete_user_me(current_user: UserDB = Security(get_current_app_user)):
    """Update the logged in user

    Returns:
        [type] -- [description]
    """
    try:
        await delete_user(current_user)
    except DatabaseError as err:
        raise UnknownError(detail=err) from err

    return Message(message="Your user was deleted successfully")


@router.get("", response_model=List[UserDB], response_model_exclude=UserDB._api_out_exclude())  # type: ignore
async def find_users_route(
    name: str = "", limit: int = 5, current_user: UserDB = Security(get_current_app_user, scopes=["admin"])
) -> List[UserDB]:
    return await find_users(name, limit)


@router.patch("/{user_sub}", response_model=UserDB, response_model_exclude=UserDB._api_out_exclude())
async def patch_user(
    user_sub: str,
    user_in: UpdateUser,
    current_user: UserDB = Security(get_current_app_user, scopes=["admin"]),
) -> UserDB:
    """
    Update an existing `User`
    """
    try:
        user = await UserDB.find_one(UserDB.sub == user_sub)
        if not user:
            raise NotFoundError("Unable to find User to update!")
    except DatabaseError as e:
        raise UnknownError(detail=e) from e

    # Only an Admin may update other users
    admin_user = "admin" in current_user.roles
    if user.sub != current_user.sub and not admin_user:
        raise ForbiddenError("You do not have authority to update this User.")

    return await update_user(user, update_data=user_in.model_dump(exclude_unset=True))
