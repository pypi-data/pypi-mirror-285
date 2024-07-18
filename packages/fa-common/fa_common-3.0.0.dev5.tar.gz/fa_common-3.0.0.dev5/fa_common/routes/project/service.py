from typing import List, Optional

from beanie.operators import Or
from bson import ObjectId

from fa_common import AlreadyExistsError, NotFoundError, UnauthorizedError
from fa_common import logger as LOG
from fa_common.routes.user.models import UserDB
from fa_common.storage import get_storage_client

from .models import ProjectDB, UpdateProject


async def get_project(user_id: str, project_name: str, expected: bool = True) -> Optional[ProjectDB]:
    """[summary]

    Arguments:
        user_id {str} -- [description]
        project_name {str} -- [description]

    Keyword Arguments:
        expected {bool} -- [description] (default: {True})

    Raises:
        NotFoundError: When project is expected but does not exist
    """

    project = await ProjectDB.find(ProjectDB.user_id == user_id, ProjectDB.name == project_name).first_or_none()
    if expected and project is None:
        LOG.warning(f"Project for user: {user_id} with name: {project_name} does not exist but was expected")
        raise NotFoundError(f"Project: {project_name} does not exist")

    if project is not None and not isinstance(project, ProjectDB):
        raise ValueError(f"ProjectDB: {project_name} was found but its type is invalid.")
    return project


async def create_project(user: UserDB, project: dict) -> ProjectDB:
    project_name = project.get("name", None)
    if project_name is None:
        raise ValueError("No project name was given")

    project_obj = await get_project(user.sub, project_name, expected=False)

    if project_obj is None:
        # wp = await create_workflow_project(user.sub, project_name, storage=storage)

        project_obj = ProjectDB(
            user_id=user.sub,
            **project,
        )
        await project_obj.initialise_project()
        client = get_storage_client()
        if (
            project_obj.storage is not None
            and project_obj.storage.bucket_name is not None
            and not await client.bucket_exists(project_obj.storage.bucket_name)
        ):
            await client.make_bucket(project_obj.storage.bucket_name)
            LOG.info(f"Created bucket {project_obj.storage.bucket_name}")
        LOG.info(f"ProjectDB {project_obj.id}")
    else:
        raise AlreadyExistsError(f"ProjectDB with the name {project_obj.name} for this user already exists.")

    return project_obj


async def update_project(
    project: ProjectDB,
    update: UpdateProject,
) -> ProjectDB:
    if project is None or project.id is None:
        raise NotFoundError("Project does not exist")

    update_project = project.model_copy(update=update.get_update_dict())
    if update.add_tags is not None:
        update_project.tags.extend(update.add_tags)
    if update.add_project_users is not None:
        update_project.project_users.extend(update.add_project_users)
    await update_project.save()

    return update_project


async def delete(project_id: ObjectId, user_sub: str | None = None) -> bool:
    """Deletes all stored data for a given project

    Arguments:
        user_token {[str]} -- [user]
        project_name {[str]} -- [project]

    Returns:
        [bool] -- [True if a project was deleted false if it didn't exist]
    """

    project = await ProjectDB.find_one(ProjectDB.id == project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} does not exist")
    elif user_sub is not None and project.user_id != user_sub:
        raise UnauthorizedError(f"Project {project_id} does not belong to user {user_sub}")

    storage_client = get_storage_client()
    if project.storage is not None and await storage_client.bucket_exists(project.storage.bucket_name):
        try:
            await storage_client.delete_file(project.storage.bucket_name, project.storage.path_prefix, True)
            LOG.info(f"Deleted project folder {project.storage.storage_full_path}")
        except Exception as err:
            if await storage_client.file_exists(project.storage.bucket_name, project.storage.path_prefix):
                raise err

    if project is not None:
        await project.delete()
        return True

    return False


async def get_projects_for_user(user: UserDB, owner_only=False, offset: int = 0, limit: int = 10, sort: list[str] = []) -> List[ProjectDB]:
    """Get projects for a user.

    Parameters
    ----------
    user_sub : str
        The user's sub (subject) identifier.
    offset : int, optional
        The number of projects to skip before returning results. Default is 0.
    limit : int, optional
        The maximum number of projects to return. Default is 10.
    sort : list[str], optional
        The list of fields to sort the projects by using the syntax `['+fieldName', '-secondField']`.
        See https://beanie-odm.dev/tutorial/finding-documents/
        Default is an empty list.

    Returns
    -------
    List[ProjectDB]
        A list of projects belonging to the user.
    """

    if owner_only:
        query = ProjectDB.find(ProjectDB.user_id == user.sub)
    else:
        query = ProjectDB.find(
            Or(ProjectDB.user_id == user.sub, {"projectUsers": {"$elemMatch": {"$regex": f"^{user.email}$", "$options": "i"}}})
        )
    if sort:
        query = query.sort(*sort)
    return await query.skip(offset).limit(limit).to_list()


async def get_project_for_user(
    user_sub: str,
    project_id: ObjectId,
) -> ProjectDB:
    """[summary]

    Arguments:
        user_token {str} -- [description]

    Returns:
        [type] -- [description]
    """
    projects = await ProjectDB.find(ProjectDB.user_id == user_sub, ProjectDB.id == project_id).to_list()

    if projects is None or len(projects) < 1:
        raise NotFoundError(f"ProjectDB {project_id} could not be found")
    elif len(projects) > 1:
        raise RuntimeError(f"Multiple projects found with id: {project_id} for user {user_sub}")

    return projects[0]


async def delete_projects_for_user(user: UserDB) -> bool:
    """[summary]

    Arguments:
        user_token {str} -- [description]

    Returns:
        [type] -- [description]
    """
    projects = await get_projects_for_user(user, owner_only=True, limit=100)

    if len(projects) > 0:
        for project in projects:
            if project.id:
                await delete(project.id, user.sub)

    return True
