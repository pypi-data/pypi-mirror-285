from typing import Any, List, Optional, Tuple, Type

from uuid_extensions import uuid7

from fa_common import DatabaseError, get_current_app
from fa_common import logger as LOG
from fa_common.db.utils_sqlite import PrefixedSqliteKVS, SqliteKVS

from .base_client import BaseClient
from .models import DBIndex, DeleteResult, DocumentDBModel, FireOffset, Operator, SortOrder, WhereCondition, WriteResult


class SQLiteDBClient(BaseClient):
    """
    Singleton client for interacting with sqlite.
    Operates mostly using models, specified when making DB queries.

    Please don't use it directly, use `db.utils.get_db_client`.
    """

    __instance = None
    sqlitedb: SqliteKVS = None

    def __new__(cls) -> "SQLiteDBClient":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        app = get_current_app()
        # If the application calls setup_db more than once (such as in the unit tests)
        # We have to make sure this client remains synced with the application's db
        if app.sqlitedb != cls.__instance.sqlitedb:
            if app.sqlitedb is None or hasattr(app.sqlitedb, "db") is False or app.sqlitedb.db is None:
                raise RuntimeError("The database hasn't been configured on the main application")
            cls.__instance.sqlitedb = app.sqlitedb  # type: ignore
        return cls.__instance

    def get_collection(self, collection_name: str) -> PrefixedSqliteKVS:
        return PrefixedSqliteKVS(collection_name + "/", self.sqlitedb)

    # Should only be done on program exit (or test exit), as
    # it's effectively removing access to the database from the class
    # instance.
    # Currently used by the unit tests to prevent pytest hanging
    # async def close_database(self):
    #    await self.sqlitedb.close()
    #    self.sqlitedb = None

    @classmethod
    async def delete_collection_fs(cls, collection: PrefixedSqliteKVS, batch_size: int) -> None:
        deleted = 0

        keys = await collection.keys()
        for key in keys:
            await collection.unset(key)
            deleted = deleted + 1

            if deleted >= batch_size:
                await cls.delete_collection_fs(collection, batch_size)

    async def delete_collection(self, collection_name: str) -> None:
        collection = self.get_collection(collection_name)
        await self.delete_collection_fs(collection, 50)

    def generate_id(self, collection_name: str) -> str:
        # collection = self.get_collection(collection_name)
        # Generate an id for the document to use
        document_id = uuid7(as_type="str")
        return str(document_id)

    async def insert(
        self,
        model: DocumentDBModel,
        include=None,
        exclude=None,
        session: Any = None,
    ) -> WriteResult:
        data = model.model_dump(include=include, exclude=exclude)

        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        if data["id"] is None:
            data["id"] = self.generate_id(collection_name)
        _id = data["id"]

        already_exists = await collection.contains(_id)
        if already_exists:
            LOG.error("Error caught adding record to sqlitedb")
            LOG.error(f"Dict = {data}")
            raise DatabaseError(f"Document with id: {_id} already exists")
        else:
            await collection.put(_id, data)

        return WriteResult(new_id=_id, transform_results=[])

    async def count(self, model: Type[DocumentDBModel], session: Any = None) -> int:
        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        return await collection.len()

    async def delete(self, model: Type[DocumentDBModel], _id: str, session: Any = None) -> DeleteResult:
        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        try:
            await collection.unset(_id)
            LOG.info(f"Record {_id} deleted")
            return DeleteResult()
        except KeyError as err:
            LOG.warning(f"Error deleting record {_id} from sqlitedb, record not found")
            raise err

    async def update_one(self, model: Type[DocumentDBModel], _id: str, data: dict, session: Any = None) -> WriteResult:
        collection_name = model.get_db_collection()
        collection = self.get_collection(collection_name)
        await collection.put(_id, data)
        return WriteResult()

    async def get_dict(
        self,
        collection_name: str,
        _id: str,
        session: Any = None,
    ) -> Optional[dict]:
        collection = self.get_collection(collection_name)

        result = await collection.get(_id, None)

        if not result:
            return None

        return result

    async def get(self, model: Type[DocumentDBModel], _id: str, session: Any = None) -> Optional[DocumentDBModel]:
        collection_name = model.get_db_collection()
        result = await self.get_dict(collection_name, _id, session)
        if result is None:
            return None
        return model(**result)

    @staticmethod
    async def filter_results(results: List[Tuple[str, dict]], where: List[WhereCondition], limit=-1, offset=0) -> List[dict]:
        # This is particularly inefficient at the moment as retrieve all data
        # from the database and then filter. We should instead add the data
        # at a particular collection/document/field and filter via the
        # WHERE query
        def item_matches(item: Tuple[str, dict]):
            key, item_dict = item
            matches = True
            for wc in where:
                if wc.field in item_dict:
                    if wc.operator is Operator.EQUALS:
                        matches = item_dict[wc.field] == wc.value
                    elif wc.operator is Operator.LT:
                        matches = item_dict[wc.field] < wc.value
                    elif wc.operator is Operator.GT:
                        matches = item_dict[wc.field] > wc.value
                    else:
                        raise NotImplementedError()
                else:
                    print("MATCHES FALSE")
                    matches = False
            return matches

        results = [x for x in results if item_matches(x)]
        if offset != 0:
            results = results[offset:]
        if limit != -1:
            results = results[: limit + 1]

        return results

    async def find_one_dict(
        self,
        collection_name: str,
        where: List[WhereCondition] = [],
        session: Any = None,
    ) -> Optional[dict]:
        collection = self.get_collection(collection_name)
        results = await collection.items()

        results = await SQLiteDBClient.filter_results(results, where)

        if len(results > 0):
            return results[0]

        return None

    async def find_one(
        self,
        model: Type[DocumentDBModel],
        where: List[WhereCondition] = [],
        session: Any = None,
    ) -> Optional[DocumentDBModel]:
        collection_name = model.get_db_collection()
        result = await self.find_one_dict(collection_name, where, session)

        if result is not None:
            return model(**result)
        return None

    async def list_dict(
        self,
        collection_name: str,
        where: List[WhereCondition] = [],
        _limit: int = 0,
        _sort: List[Tuple[str, SortOrder]] | None = None,
        mongo_offset: int = 0,
        fire_offset: Optional[FireOffset] = None,
    ) -> List[dict]:
        results = []
        collection = self.get_collection(collection_name)

        # Sqlite uses -1 for no limit
        if _limit == 0:
            _limit = -1
        if len(where) == 0:
            items = await collection.items(limit=_limit, offset=mongo_offset)
        else:
            # Don't filter by limit / offset before we collect the items to filter
            items = await collection.items()
            items = await SQLiteDBClient.filter_results(items, where, _limit, mongo_offset)

        for _documentid, document in items:
            results.append(document)

        if _sort is not None:
            for s in _sort:
                results.sort(reverse=(s == SortOrder.ASCENDING))

        return results

    async def list(
        self,
        model: Type[DocumentDBModel],
        where: List[WhereCondition] = [],
        _limit: int = 0,
        _sort: List[Tuple[str, SortOrder]] | None = None,
        mongo_offset: int = 0,
        fire_offset: Optional[FireOffset] = None,
    ) -> List[DocumentDBModel]:
        collection_name = model.get_db_collection()
        results = await self.list_dict(collection_name, where, _limit, _sort, mongo_offset, fire_offset)

        return [model(**res) for res in results]

    async def create_indexes(self, index: List[DBIndex], collection: str) -> Optional[List[str]]:
        return None
