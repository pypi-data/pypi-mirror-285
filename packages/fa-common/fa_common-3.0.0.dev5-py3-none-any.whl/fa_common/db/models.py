import abc
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Tuple

from pydantic import ConfigDict, Field, field_validator, model_validator

from fa_common import logger as LOG
from fa_common.models import CamelModel
from fa_common.utils import get_now

from .utils import get_db_client

# from pymongo.results import UpdateResult, DeleteResult


class SortOrder(str, Enum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class DBIndex(CamelModel):
    index_fields: List[Tuple[str, SortOrder]]
    unique: bool


class FireOffset(CamelModel):
    # Start at or Start After
    start_at: bool = False
    start_id: Optional[str] = None
    start_fields: Optional[dict] = None

    @model_validator(mode="after")
    def check_for_start(self) -> "FireOffset":
        if self.start_id is None and self.start_fields is None:
            raise ValueError("Either start_id or start_fields needs a value")
        return self


class Operator(str, Enum):
    EQUALS = "=="
    LT = "<"
    GT = ">"
    IN = "in"
    ARRAY_CONTAINS = "array_contains"
    ARRAY_CONTAINS_ANY = "array_contains_any"


class WhereCondition(CamelModel):
    field: str
    operator: Operator = Operator.EQUALS
    value: Any


class WriteResult(CamelModel):
    success: bool = True
    new_id: Optional[str] = None
    transform_results: Optional[List[Any]] = None


class DeleteResult(CamelModel):
    success: bool = True
    delete_time: Optional[datetime] = None


class DocumentDBModel(CamelModel, abc.ABC):
    """
    Base Model to use for any information saving in MongoDB.
    Provides `id` field as a base, populated by id-generator.
    Use it as follows:

    .. code-block:: python

        class MyModel(DocumentDBModel):
            additional_field1: str
            optional_field2: int = 42

            class Meta:
                collection = "mymodel_collection"

        mymodel = MyModel(additional_field1="value")
        mymodel.save()
        assert mymodel.additional_field1 == "value"
        assert mymodel.optional_field2 == 42
        assert isinstance(mymodel.id, int)
    """

    id: Optional[str] = Field(None, alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def id_as_string(cls, v):
        return v if v is None or isinstance(v, str) else str(v)

    def set_id(self) -> Optional[str]:
        """
        If id is supplied (ex. from DB) then use it, otherwise generate new.
        """
        if not self.id:
            db = get_db_client()
            self.id = db.generate_id(self.get_db_collection())

        return self.id

    @classmethod
    @abc.abstractmethod
    def get_db_collection(cls) -> str:
        pass

    @classmethod
    async def get(cls, _id: str) -> Optional["DocumentDBModel"]:
        db = get_db_client()
        return await db.get(cls, _id)

    @classmethod
    async def find_one(cls, where: List[WhereCondition]) -> Optional["DocumentDBModel"]:
        db = get_db_client()
        return await db.find_one(cls, where)

    @classmethod
    async def delete(cls, _id: str) -> DeleteResult:
        db = get_db_client()
        return await db.delete(cls, _id)

    @classmethod
    async def count(cls) -> int:
        db = get_db_client()
        return await db.count(cls)

    @classmethod
    async def list(
        cls,
        where: List[WhereCondition] = [],
        _limit: int = 0,
        _sort: List[Tuple[str, SortOrder]] | None = None,
        mongo_offset: int = 0,
        fire_offset: Optional[FireOffset] = None,
    ) -> List["DocumentDBModel"]:
        db = get_db_client()
        return await db.list(
            cls,
            where,
            _limit=_limit,
            _sort=_sort,
            mongo_offset=mongo_offset,
            fire_offset=fire_offset,
        )

    async def save(
        self,
        include: set | None = None,
        exclude: set | None = None,
        rewrite_fields: dict | None = None,
    ) -> Optional[str]:
        db = get_db_client()
        # _id = self.set_id()

        if not rewrite_fields:
            rewrite_fields = {}

        for field, value in rewrite_fields.items():
            setattr(self, field, value)

        insert_result = await db.insert(self, include=include, exclude=exclude)
        LOG.debug(insert_result.transform_results)
        if not self.id:
            self.id = insert_result.new_id

        return self.id

    @classmethod
    async def update_one(cls, _id: str, data: dict) -> WriteResult:
        db = get_db_client()
        return await db.update_one(cls, _id, data)

    @classmethod
    async def update_many(cls, data: List[Tuple[str, dict]]) -> WriteResult:
        db = get_db_client()
        return await db.update_many(cls, data)

    @classmethod
    async def create_indexes(cls) -> Optional[List[str]]:
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "indexes"):  # type:ignore
            db = get_db_client()
            return await db.create_indexes(cls, cls.Meta.indexes, cls.Meta.collection)  # type:ignore
        return None

    model_config = ConfigDict(str_strip_whitespace=True)


class DocumentDBTimeStampedModel(DocumentDBModel):
    """
    TimeStampedModel to use when you need to have `created` field,
    populated at your model creation time.

    Use it as follows:

    .. code-block:: python

        class MyTimeStampedModel(MongoDBTimeStampedModel):

            class Meta:
                collection = "timestamped_collection"


        mymodel = MyTimeStampedModel()
        mymodel.save()

        assert isinstance(mymodel.id, int)
        assert isinstance(mymodel.created, datetime)
    """

    created: Optional[datetime] = None

    @field_validator("created", mode="before")
    @classmethod
    def set_created_now(cls, v: datetime) -> datetime:
        """
        If created is supplied (ex. from DB) -> use it, otherwise generate new.
        """
        if v:
            return v
        now = get_now()
        return now.replace(microsecond=0)
