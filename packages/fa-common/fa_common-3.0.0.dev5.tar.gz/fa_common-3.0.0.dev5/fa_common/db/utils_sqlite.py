from typing import Any

import aiosqlite


# SqliteKVS sourced from https://github.com/robertsdotpm/p2pd/blob/ircdns/p2pd/sqlite_kvs.py
# with some minor changes to support PrefixedSqliteKVS
# MIT License
# This was originally described in this Stackoverflow answer
# https://stackoverflow.com/questions/47237807/use-sqlite-as-a-keyvalue-store
class SqliteKVS:
    file_path: str
    db: aiosqlite.Connection

    def __init__(self, file_path: str):
        self.file_path = file_path

    # Scheme has a text key and value.
    async def start(self):
        query = "CREATE TABLE IF NOT EXISTS kv" + "(key text unique, value text)"

        self.db = await aiosqlite.connect(self.file_path)
        await self.db.execute(query)
        await self.db.commit()
        return self

    # Ensure the DB is closed to avoid corruption.
    async def close(self):
        await self.db.close()
        self.db = None

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def len(self):
        query = "SELECT COUNT(*) FROM kv"
        cursor = await self.db.execute(query)
        rows = (await cursor.fetchone())[0]
        await cursor.close()
        return rows if rows is not None else 0

    # Overwrite a row attached to a key.
    # Create it if it doesn't exist.
    # Store complex objects as text.
    async def put(self, key: str, value: Any):
        query = "REPLACE INTO kv (key, value) VALUES (?,?)"
        value = repr(value)
        await self.db.execute(query, (key, value))
        await self.db.commit()

    # Select values by key name.
    # Decode any complex values back to Python types.
    async def get(self, key: str, default: Any = None):
        query = "SELECT value FROM kv WHERE key = ?"
        cursor = await self.db.execute(query, (key,))
        item = await cursor.fetchone()
        await cursor.close()

        # No entry by that key exists.
        if item is None:
            if default is not None:
                return default
            raise KeyError(key)

        return eval(item[0])

    # Delete key entry in DB.
    async def unset(self, key: str):
        # Raise exception if it doesn't exist.
        # We use __class__ here so it doesn't get
        # routed back to the prefixed model. It may be better
        # just to not check..
        await __class__.get(self, key)

        # Delete the key.
        query = "DELETE FROM kv WHERE key = ?"
        await self.db.execute(query, (key,))
        await self.db.commit()

    async def iterkeys(self):
        query = "SELECT key FROM kv"
        async with self.db.execute(query) as cursor:
            async for row in cursor:
                yield row[0]

    async def itervalues(self):
        query = "SELECT value FROM kv"
        async with self.db.execute(query) as cursor:
            async for row in cursor:
                yield eval(row[0])

    async def iteritems(self, limit: int = -1, offset: int = 0):
        query = "SELECT key, value FROM kv LIMIT ? OFFSET ?"
        async with self.db.execute(query, (limit, offset)) as cursor:
            async for row in cursor:
                yield row[0], eval(row[1])

    # As the moment we store the raw dictionary collection/documentid = rawdict
    # In the future we could instead store collection/documentid/field = dict[field] = value
    # async def iterfind(self, where: List[WhereCondition], limit = -1, offset = 0):
    #     where_query = ""
    #     query_variables = []
    #     for wc in where:
    #         where_query += f"AND {wc.field}" if where_query else f"WHERE {wc.field}"
    #         if wc.operator is Operator.EQUALS:
    #             where_query += ' = ? '
    #             query_variables.append(wc.value)
    #         elif wc.operator is Operator.LT:
    #             where_query += ' < ? '
    #             query_variables.append(wc.value)
    #         elif wc.operator is Operator.GT:
    #             where_query += ' > ? '
    #             query_variables.append(wc.value)
    #         else:
    #             raise NotImplementedError()

    #     async for
    #     query = f'SELECT key, value FROM kv {where_query} LIMIT ? OFFSET ?'
    #     print("WHEREQUERY", query)
    #     query_variables.append(limit)
    #     query_variables.append(offset)
    #     async with self.db.execute(query, tuple(query_variables)) as cursor:
    #         async for row in cursor:
    #             yield row[0], eval(row[1])

    async def keys(self):
        key_list = []
        async for key in self.iterkeys():
            key_list.append(key)

        return key_list

    async def values(self):
        value_list = []
        async for value in self.itervalues():
            value_list.append(value)

        return value_list

    async def items(self, limit: int = -1, offset: int = 0):
        item_list = []
        async for item in self.iteritems(limit, offset):
            item_list.append(item)

        return item_list

    async def contains(self, key: str):
        query = "SELECT 1 FROM kv WHERE key = ?"
        cursor = await self.db.execute(query, (key,))
        ret = await cursor.fetchone()
        await cursor.close()
        return ret is not None

    async def __aiter__(self):
        return self.iterkeys()


class PrefixedSqliteKVS(SqliteKVS):
    prefix: str

    def __init__(self, prefix: str, parentdb: SqliteKVS):
        if hasattr(parentdb, "prefix"):
            raise Exception
            self.prefix = prefix + parentdb.prefix
        else:
            self.prefix = prefix

        # Throw if parentdb hasn't been initialised yet
        assert parentdb.db is not None
        self.db = parentdb.db

    async def len(self):
        if self.prefix:
            query = "SELECT COUNT(*) FROM kv WHERE key LIKE ?"
            cursor = await self.db.execute(query, (self.prefix + "%",))
            rows = (await cursor.fetchone())[0]
            await cursor.close()
            return rows if rows is not None else 0
        else:
            return await super().len()

    async def put(self, key: str, value: Any):
        return await super().put(self.prefix + key, value)

    async def get(self, key: str, default: Any = None):
        return await super().get(self.prefix + key, default)

    async def unset(self, key):
        return await super().unset(self.prefix + key)

    async def iterkeys(self):
        if self.prefix:
            query = "SELECT key FROM kv WHERE key LIKE ?"
            async with self.db.execute(query, (self.prefix + "%",)) as cursor:
                async for row in cursor:
                    yield row[0].removeprefix(self.prefix)
        else:
            yield super().iterkeys()

    async def itervalues(self):
        if self.prefix:
            query = "SELECT value FROM kv WHERE key LIKE ?"
            async with self.db.execute(query, (self.prefix + "%",)) as cursor:
                async for row in cursor:
                    yield eval(row[0])
        else:
            yield super().itervalues()

    async def iteritems(self, limit: int = -1, offset: int = 0):
        if self.prefix:
            query = "SELECT key, value FROM kv WHERE key LIKE ? LIMIT ? OFFSET ?"
            async with self.db.execute(query, (self.prefix + "%", limit, offset)) as cursor:
                async for row in cursor:
                    yield row[0].removeprefix(self.prefix), eval(row[1])
        else:
            yield super().iteritems()

    async def contains(self, key: str):
        return await super().contains(self.prefix + key)
