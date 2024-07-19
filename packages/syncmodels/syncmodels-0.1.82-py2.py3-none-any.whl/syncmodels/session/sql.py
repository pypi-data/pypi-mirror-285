from typing import Dict
import re
from itertools import chain

from agptools.helpers import parse_uri
from syncmodels.definitions import (
    KIND_KEY,
    TABLE_KEY,
    MONOTONIC_SINCE_KEY,
    MONOTONIC_SINCE_VALUE,
    URI,
    DURI,
    JSON,
)

from ..crud import DEFAULT_NAMESPACE, tf, parse_duri
from ..schema import StructShema
from ..requests import iResponse
from . import iSession


class iSQLSession(iSession):
    "base class for SQL Based Sessions"
    DEFAULT_METHOD = "post"
    ELAPSED_KEYS = r"(?imux)(duration|elapsed)"
    SENTENCE_KEY = "stmt"

    def _get_connection_key(self, _uri: DURI):
        namespace = tf(_uri.get("fscheme", DEFAULT_NAMESPACE))
        # database = tf(uri.get("host", DEFAULT_DATABASE))
        database = _uri["path"]
        key = namespace, database
        return key

    async def get_samples(self, _uri: DURI, N=10):
        # get connection
        conn = await self._get_connection(_uri)

        # get some data
        table = _uri.get(TABLE_KEY) or _uri[KIND_KEY]
        # _kind = parse_duri(kind)
        sql = f"SELECT * FROM {table} LIMIT {N}"
        return await self._execute(conn, sql)

    async def _execute(self, connection, sql, **params):
        result = connection.execute(sql, **params)
        return result.fetchall()

    async def _execute(self, connection, sql, **params):
        res = connection.execute(sql, params)

        result = {
            "cols": [_[0] for _ in res.description],
            "data": [_ for _ in res],
        }
        return result

    def _map_result_structure(self, data, rows=1, **kw) -> Dict:
        """try to map the info from the structure returned
        from a simple typicl query with the keys that we expect:
        i.e: 'names', 'data', 'elapsed'
        """
        result = {}
        candidates = set(["cols"])
        keys = list(data.keys())
        # iterate in a particular order: candidates + rest from data
        for key in chain(
            candidates.intersection(keys),
            candidates.symmetric_difference(keys),
        ):
            value = data[key]
            if isinstance(value, list):
                if all([_.__class__ == str for _ in value]):
                    result["names"] = key
                elif len(value) == rows or key in ("data", "stream"):
                    # TODO: has DB-API2.0 a method for table instrospection?
                    result["data"] = key
            elif isinstance(value, float):
                if re.match(self.ELAPSED_KEYS, key):
                    result["elapsed"] = key
        return result

    async def _inspect_schema(self, _uri: DURI) -> StructShema:
        """Guess table schema by inspecting returned data.
        Session is authenticated already.
        """
        N = 10
        data = await self.get_samples(_uri, N)
        struct = self._map_result_structure(data, rows=N)

        names, types, d_fields, monotonic_since_key = self.guess_schema(
            data[struct["names"]], data[struct["data"]]
        )
        schema = StructShema(
            names, types, d_fields, monotonic_since_key, struct
        )
        return schema

    async def update_params(self, url: URI, params: JSON, context: JSON):
        "last chance to modify params based on context for a specific iSession type"
        call_kw = await super().update_params(url, params, context)

        _uri = parse_duri(url, **context)
        _uri["query_"].update(params)
        schema = self._schema(_uri) or await self._get_schema(_uri)

        since_key = params.get(MONOTONIC_SINCE_KEY)
        table = context[KIND_KEY]
        if since_key in schema.names:
            query = f"SELECT * FROM {table} WHERE {since_key} > :{MONOTONIC_SINCE_VALUE}"
        else:
            query = f"SELECT * FROM {table}"

        call_kw.setdefault("json", {})[self.SENTENCE_KEY] = query
        return call_kw

    async def _process_response(self, response):
        stream, meta = await super()._process_response(response)
        schema = self._schema(self.context)
        struct = schema.struct
        data_key = struct["data"]
        rows = stream.pop(data_key)

        # map the remaing info into meta
        for key, value in struct.items():
            if value in stream:
                meta[key] = stream[value]
        cols = meta["names"]

        _stream = []
        for row in rows:
            item = {cols[i]: value for i, value in enumerate(row)}
            _stream.append(item)

        meta["count"] = len(_stream)
        return _stream, meta

    async def get(self, url, headers=None, params=None, **kw):
        headers = headers or {}
        params = params or {}

        _uri = parse_uri(url)
        _uri["query_"].update(params)
        _uri.setdefault(KIND_KEY, self.context[KIND_KEY])

        # schema = self._schema(_uri) or await self._get_schema(_uri)

        # # check SINCE
        # since_key = params.get(MONOTONIC_SINCE_KEY)
        # if since_key in fields:
        #     query = f"SELECT * FROM {table} WHERE {since_key} > :{MONOTONIC_SINCE_VALUE}"
        # else:
        #     query = f"SELECT * FROM {table}"

        sql = kw["json"]["stmt"]
        # connection = sqlite3.connect(_uri["path"])
        # cursor = connection.cursor()
        conn = await self._get_connection(_uri)
        body = await self._execute(conn, sql, **_uri.get("query_", {}))

        # data = res[schema.struct["data"]]
        # body = [
        #     {schema.names[i]: v for i, v in enumerate(row)} for row in data
        # ]

        response = iResponse(
            status=200, headers=headers, links=None, real_url=url, body=body
        )
        return response
