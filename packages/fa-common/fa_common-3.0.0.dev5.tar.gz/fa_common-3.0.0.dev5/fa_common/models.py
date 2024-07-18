from datetime import date, datetime, time, timezone
from typing import Annotated, Any, Dict, Generic, List, TypeVar

import pytz
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from pydantic.functional_serializers import PlainSerializer

from fa_common.utils import sizeof_fmt, utcnow

MT = TypeVar("MT")


def camel_case(string: str) -> str:
    assert isinstance(string, str), "Input must be of type str"

    first_alphabetic_character_index = -1
    for index, character in enumerate(string):
        if character.isalpha():
            first_alphabetic_character_index = index
            break

    empty = ""

    if first_alphabetic_character_index == -1:
        return empty

    string = string[first_alphabetic_character_index:]

    titled_string_generator = (character for character in string.title() if character.isalnum())

    try:
        return next(titled_string_generator).lower() + empty.join(titled_string_generator)

    except StopIteration:
        return empty


def to_camel(string):
    if string == "id":
        return "_id"
    if string.startswith("_"):  # "_id"
        return string
    return camel_case(string)


DatetimeType = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: dt.replace(microsecond=0, tzinfo=timezone.utc).isoformat(),
        return_type=str,
        when_used="json",
    ),
]
DateType = Annotated[date, PlainSerializer(lambda dt: dt.isoformat(), return_type=str, when_used="json")]
TimeType = Annotated[
    time,
    PlainSerializer(
        lambda dt: dt.replace(microsecond=0, tzinfo=timezone.utc).isoformat(),
        return_type=str,
        when_used="json",
    ),
]
ObjectIdType = Annotated[ObjectId, PlainSerializer(lambda oid: str(oid), return_type=str, when_used="json")]


class CamelModel(BaseModel):
    """
    Replacement for pydanitc BaseModel which simply adds a camel case alias to every field
    NOTE: This has been updated for Pydantic 2 to remove some common encoding helpers
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class BucketMeta(CamelModel):
    """
    A more generic concept for bucket, helping to handle
    multi bucket scenarios or reference to different subpaths
    within a bucket

    :param: name: bucket name
    :param: base_path: base_path to a collection of items
    """

    name: str
    base_path: str


class File(CamelModel):
    size: str | None = None  # e.g. '3 KB'
    size_bytes: int | None = None
    url: str | None = None  # download url
    public_url: str | None = None  # public download url
    id: str | None = None  # id can be path or database id
    dir: bool = False
    path: str | None = None  # path to current item (e.g. /folder1/someFile.txt)
    # optional (but we are using id as name if name is not present) (e.g. someFile.txt)
    name: str
    bucket: str | None = None
    content_type: str | None = None

    def set_size(self, bytes: int):  # noqa: A002
        self.size = sizeof_fmt(bytes)
        self.size_bytes = bytes


class FileDownloadRef(CamelModel):
    name: str
    url: str
    extension: str
    size: int


class Message(CamelModel):
    message: str = ""
    warnings: List[str] | None = None


class MessageValue(Message, Generic[MT]):
    return_value: MT | None = None


class MessageValueList(Message):
    return_value: List[str]


class MessageValueFiles(Message):
    return_value: List[File]


class ErrorResponse(CamelModel):
    code: str | None = None
    detail: str | None = None
    fields: List[Dict[str, Any]] | None = None
    error: str | None = None
    errors: List[Dict[str, Any]] = []
    trace: str | None = None


class Version(CamelModel):
    version: str
    commit_id: str | None = None
    build_date: datetime | str | None = None
    framework_version: str | None = None


class StorageLocation(CamelModel):
    """"""

    bucket_name: str = ""
    """Name of the bucket, None for local storage"""
    path_prefix: str = ""
    """Absolute Path for the StorageLocation in the bucket, use '/' to separate folders"""

    description: str | None = None
    """What is this storage location for?"""

    @field_validator("path_prefix")
    @classmethod
    def validate_path_prefix(cls, v: str) -> str:
        """Validate the path prefix and convert double slashes to single slash"""
        if v:
            v = v.replace("//", "/")
        return v

    @computed_field
    def storage_folder(self) -> str:
        """Folder name for the storage location, last part of the path prefix"""
        if self.path_prefix:
            return self.path_prefix.split("/")[-1]
        return ""

    @computed_field
    def storage_full_path(self) -> str:
        """Full path including the bucket name and path prefix"""
        path = ""
        if self.bucket_name:
            path += self.bucket_name
        if self.path_prefix:
            if path:
                path += "/"
            return f"{path}{self.path_prefix}"
        return path


class TimeStampedModel(CamelModel):
    """
    TimeStampedModel (FOR BEANIE) to use when you need to have `created` field,
    populated at your model creation time.

    Use it as follows:

    .. code-block:: python

        class MyTimeStampedModel(Document, TimeStampedModel): # from beanie import Document

            class Collection:
                name = "my_model"


        mymodel = MyTimeStampedModel()
        mymodel.save()

        assert isinstance(mymodel.id, int)
        assert isinstance(mymodel.created, datetime)
    """

    created: datetime | None = None

    @field_validator("created", mode="before")
    @classmethod
    def set_created_now(cls, v: datetime | None) -> datetime:
        """
        If created is supplied (ex. from DB) -> use it, otherwise generate new.
        """
        if v is not None:
            return v
        now = utcnow()
        return now.replace(microsecond=0, tzinfo=timezone.utc)


class WorkflowProject(TimeStampedModel):
    """
    WorkflowProject
    """

    name: str = Field(..., pattern="^[0-9a-zA-Z_-]+$")
    user_id: str
    storage: StorageLocation
    timezone: str = "UTC"

    @field_validator("timezone")
    @classmethod
    def must_be_valid_timezone(cls, v):
        """ """
        if v not in pytz.all_timezones:
            raise ValueError(f"{v} is not a valid timezone")
        return v

    @computed_field()
    def bucket_id(self) -> str:
        return self.storage.path_prefix
