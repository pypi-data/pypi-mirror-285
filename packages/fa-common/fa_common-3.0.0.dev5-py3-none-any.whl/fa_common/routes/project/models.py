import pymongo
from beanie import Document, PydanticObjectId
from pydantic import Field

from fa_common import File, get_settings
from fa_common.models import CamelModel, StorageLocation, WorkflowProject


class ProjectDB(Document, WorkflowProject):
    dataset_links: list[str] = []
    tags: list[str] = []
    files: list[File] = []
    project_users: list[str] = []
    """List of user emails that have access to the project"""
    storage: StorageLocation | None = None  # type: ignore

    @staticmethod
    def _api_out_exclude() -> set[str]:
        """
        Fields to exclude from an API output
        """
        return set()

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}project"
        indexes = [pymongo.IndexModel([("name", pymongo.TEXT), ("user_id", pymongo.TEXT)], name="name_text_index", unique=True)]

    def link_dataset(self, dataset_id: str):
        if dataset_id not in self.project_links:
            self.project_links.append(dataset_id)

    def unlink_dataset(self, dataset_id: str):
        if dataset_id in self.project_links:
            self.project_links.remove(dataset_id)

    async def initialise_project(self):
        if self.id is not None:
            raise ValueError("Project already initialised")
        settings = get_settings()
        self.id = PydanticObjectId()
        self.storage = StorageLocation(
            bucket_name=settings.BUCKET_NAME,
            path_prefix=f"{settings.BUCKET_PROJECT_FOLDER}{self.id}",
            description="Default Project file storage",
        )

        return await self.save()

    def get_storage(self) -> StorageLocation:
        if self.id is None:
            raise ValueError("Project must be saved before storage can be accessed")

        if self.storage is None:
            settings = get_settings()
            self.storage = StorageLocation(
                bucket_name=settings.BUCKET_NAME,
                path_prefix=f"{settings.BUCKET_PROJECT_FOLDER}/{self.id}",
                description="Default Project file storage",
            )
        return self.storage


class CreateProject(CamelModel):
    name: str = Field(..., pattern="^[0-9a-zA-Z_]+$")
    description: str = ""
    """ Project description """
    tags: list[str] = []
    project_users: list[str] = []


class UpdateProject(CamelModel):
    name: str | None = Field(None, pattern="^[0-9a-zA-Z_]+$")
    description: str | None = None
    """ Project description """
    tags: list[str] | None = None
    """Tags replaces existing tags with the new array unless None is passed in which case it is ignored."""
    add_tags: list[str] | None = None
    """Add tags appends the new tags to the existing tags unless None is passed in which case it is ignored."""
    project_users: list[str] | None = None
    """Project users replaces existing project users with the new array unless None is passed in which case it is ignored."""
    add_project_users: list[str] | None = None
    """Add project users appends the new project users to the existing project users unless None is passed in which case it is ignored."""

    def get_update_dict(self) -> dict:
        return self.model_dump(exclude_unset=True, exclude_none=True, exclude={"add_tags", "add_project_users"})
