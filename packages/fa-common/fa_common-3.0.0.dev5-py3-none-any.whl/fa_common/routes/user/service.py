from typing import Union

from beanie.operators import RegEx
from fastapi import Depends
from fastapi.security import SecurityScopes

from fa_common import AuthType, ForbiddenError, get_settings
from fa_common import logger as LOG
from fa_common.auth import AuthUser
from fa_common.exceptions import NotFoundError
from fa_common.routes.user.models import UserDB

if get_settings().AUTH_TYPE is AuthType.STANDALONE:
    from fa_common.auth import get_standalone_user as get_current_user
else:
    from fa_common.auth import get_current_user  # type:ignore

# from fa_common.workflow import delete_workflow_user

# from data_mosaic_backend.workspace.service import update_workspace


async def get_current_app_user(
    security_scopes: SecurityScopes,
    current_user: Union[AuthUser, UserDB] = Depends(get_current_user),
) -> UserDB:
    if current_user is not None and current_user.sub is not None:
        user = current_user if isinstance(current_user, UserDB) else await UserDB.find_one(UserDB.sub == current_user.sub)

        if user is not None and isinstance(user, UserDB):
            # FIXME temporary way to apply roles to existing users
            # if not user.roles:
            #     user.apply_roles_from_email()
            #     await user.save()

            for scope in security_scopes.scopes:
                if scope not in user.scopes and scope not in user.roles:
                    raise ForbiddenError(detail="Not enough permissions to access this data")

            return user

    raise NotFoundError(detail="The current user does not exist as a user of this application.")


async def update_user(user: UserDB, update_data: dict):
    updated_user = user.model_copy(update=update_data)
    await updated_user.replace()
    return updated_user


async def create_user(new_user: AuthUser) -> UserDB:
    user: UserDB = UserDB(valid_user=True, **new_user.model_dump())

    # if new_user.emails:
    #     user.apply_roles_from_email()

    await user.save()
    LOG.info(f"Created New User: {user.name}")

    # # Sets all the paths for the users storage
    # user.set_user_folder()

    # await user.replace()
    # LOG.info(f"Updated New User with storage folder: {user.user_folder}")

    # # Create Bucket
    # if user.bucket_id and not get_settings().BUCKET_NAME:
    #     storage_client = get_storage_client()
    #     await storage_client.make_bucket(user.bucket_id)
    #     LOG.info(f"Created New Bucket: {user.bucket_id}")

    return user


async def delete_user(user: UserDB):
    # if user.path_prefix is not None:
    #     try:
    #         storage_client = get_storage_client()
    #         if user.bucket_id and not get_settings().BUCKET_NAME:
    #             await storage_client.delete_bucket(user.get_bucket())
    #             LOG.info(f"Deleted user bucket {user.bucket_id}")
    #         else:
    #             await storage_client.delete_file(user.get_bucket(), user.path_prefix, True)
    #             LOG.info(f"Deleted user folder {user.path_prefix}")
    #     except StorageError as err:
    #         LOG.error(f"Folder {user.path_prefix} was not deleted. Error: {err}")

    # TODO: Replace this behaviour in backend
    # datasets = await DMDataState.find(DMDataState.user_id == user.sub).to_list()
    # for dataset in datasets:
    #     if dataset.id is not None:
    #         await dataset.delete()

    if user.id is not None:
        await user.delete()
        LOG.info(f"Deleted user {user.id}")


async def find_users(name: str, limit: int = 5):
    """
    Find all users with partial match on the provided `name`.
    """
    return await UserDB.find_many(RegEx(UserDB.name, f"{name}", "i")).limit(limit).to_list()
