import asyncio

from agptools.helpers import build_uri, parse_xuri, parse_uri
from agptools.logs import logger

from syncmodels.definitions import (
    BODY_KEY,
    KIND_KEY,
    METHOD_KEY,
    FUNC_KEY,
    MONOTONIC_KEY,
    CRAWLER_KEY,
    BOT_KEY,
    # MONOTONIC_SINCE,
    MONOTONIC_SINCE_KEY,
    MONOTONIC_SINCE_VALUE,
    REG_PRIVATE_KEY,
    REG_SPLIT_PATH,
    URI,
    DURI,
    JSON,
)

from syncmodels.http import (
    guess_content_type,
    AUTHORIZATION,
    AUTH_USER,
    AUTH_SECRET,
    AUTH_URL,
    AUTH_KEY,
    AUTH_VALUE,
    AUTH_METHOD,
    AUTH_PAYLOAD,
    METHOD_BASIC,
    METHOD_JSON,
    CONTENT_TYPE,
    USER_AGENT,
    APPLICATION_JSON,
    APPLICATION_ZIP,
    BASIC_HEADERS,
    extract_result,
)

from syncmodels.crawler import iRunner

from ..crud import parse_duri, DEFAULT_DATABASE, DEFAULT_NAMESPACE, tf

from ..context import iContext
from ..schema import iSchema, StructShema
from ..registry import iRegistry
from ..requests import iResponse

log = logger(__name__)


class iSession(iContext, iSchema, iRegistry):  # , iAuthenticator):
    "The base for all 3rd party session accessors"

    DEFAULT_METHOD = "get"

    RESPONSE_META = ["headers", "links", "real_url"]

    hide_SESSION_FACTORY = {}  # TODO: delete
    CACHE = {}
    "some data to be cached and shared"

    def __init__(self, bot, **kw):
        self.bot = bot
        self.connection_pool = {}
        self.headers = {}
        self.context = kw

    def _schema(self, _uri: DURI, **kw):
        return self.CACHE.get(_uri["uri"], {}).get(_uri[KIND_KEY])

    async def _create_connection(self, uri: DURI, **_uri):
        raise NotImplementedError()

    def _get_base_url(self, **kw) -> URI:
        url = build_uri(
            fscheme=self.context["fscheme"],
            xhost=self.context["xhost"],
            **kw,
        )
        return url

    async def _process_response(self, response):
        def expand(value):
            iterator = getattr(value, "items", None)
            if iterator:
                value = {k: expand(v) for k, v in iterator()}
            return value

        meta = {
            k: expand(getattr(response, k, None))
            for k in self.RESPONSE_META
            if hasattr(response, k)
        }
        content_type = guess_content_type(meta.get("headers", {}))
        if content_type == APPLICATION_JSON:
            stream = await response.json()
        elif content_type == APPLICATION_ZIP:
            stream = await response.read()  # bytes object
        else:
            stream = await response.text()
            assert isinstance(stream, str)
            # stream = [{'data': block} for block in stream.splitlines()]
            stream = [{"result": stream}]

        return stream, meta

    def _get_connection_key(self, uri: DURI):
        namespace = tf(uri.get("fscheme", DEFAULT_NAMESPACE))
        database = tf(uri.get("host", DEFAULT_DATABASE))
        key = namespace, database
        return key

    async def _get_connection(self, uri: DURI, **kw):
        key = self._get_connection_key(uri)
        connection = self.connection_pool.get(
            key
        ) or await self._create_connection(uri)
        return connection

    @classmethod
    async def new(cls, url, bot, **context):
        def score(item):
            "score by counting how many uri values are not None"
            options, m = item
            _uri = parse_xuri(url)
            sc = 100 * len(m.groups()) + len(
                [_ for _ in _uri.values() if _ is not None]
            )
            return sc, options

        blue, factory, args, kw = cls.get_factory(
            url, __klass__=cls, score=score
        )
        if factory:
            uri = parse_uri(url)
            try:
                context.update(kw)
                item = factory(bot=bot, *args, **uri, **context)
                return item
            except Exception as why:  # pragma: nocover
                print(why)
                foo = 1

        # option = cls.locate(url, __klass__=cls, score=score)
        # if option:
        #     uri = parse_uri(url)
        #     factory, info = option
        #     for __key__, (args, kw) in info.items():
        #         try:
        #             context.update(kw)
        #             item = factory(bot=bot, *args, **uri, **context)
        #             return item
        #         except Exception as why:
        #             print(why)

        raise RuntimeError(f"Unable to create a item {url}")

    async def get(self, url, headers=None, params=None, **kw) -> iResponse:
        "Note: Returns is not properly a iResponse, but we mimic the same interface"
        headers = headers or {}
        params = params or {}
        connection = await self._get_connection(
            url, **headers, **params, **kw
        )
        return await connection.get(
            url, headers=headers, params=params, **kw
        )

    async def _get_schema(self, _uri: DURI):
        uri = _uri["uri"]
        kind = _uri[KIND_KEY]
        schema = self.CACHE.setdefault(uri, {})[kind] = (
            await self._inspect_schema(_uri)
        )

        return schema

    async def _inspect_schema(self, _uri: DURI) -> StructShema:
        """performs an introspection to figure-out the schema
        for a particular kind object
        """
        schema = StructShema(
            names=[],
            types=[],
            d_fields={},
            monotonic_since_key="",
            struct={},
        )
        return schema

    async def update_params(self, url, params, context):
        "last chance to modify params based on context for a specific iSession type"
        wave0 = context.get(MONOTONIC_KEY, None)
        if wave0:
            _uri = parse_uri(url, **context)
            schema = self._schema(_uri) or await self._get_schema(_uri)
            monotonic_since_key = schema.monotonic_since_key
            if monotonic_since_key in wave0:
                params[MONOTONIC_SINCE_KEY] = monotonic_since_key
                params[MONOTONIC_SINCE_VALUE] = wave0[monotonic_since_key]
            else:
                log.warning(
                    "MONOTONIC_SINCE_KEY [%s] is missing in wave: %s: schema=[%s]",
                    monotonic_since_key,
                    wave0,
                    schema.__dict__,
                )
        call_kw = {
            "url": url,
            "headers": self.headers,
        }
        if context.get(METHOD_KEY, "get").lower() in ("post", "put"):
            if body := context.get(BODY_KEY):
                call_kw["json"] = body
        else:
            call_kw["params"] = params
        return call_kw


class iActiveSession(iSession, iRunner):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.running = False

    async def start(self):
        pass

    async def stop(self):
        pass

    async def run(self):
        while self.running:
            await asyncio.sleep(1)
