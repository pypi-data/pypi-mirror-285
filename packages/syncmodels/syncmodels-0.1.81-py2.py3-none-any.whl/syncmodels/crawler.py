"""
Asyncio Crawler Support
"""

import asyncio
import base64

from asyncio.queues import Queue
from collections import deque
from datetime import datetime
import queue
from itertools import chain
import hashlib
import random
import re
import os
import sys
import traceback
from typing import Dict, List, Any, Callable
import time
import types

# from pprint import pformat
import yaml
import requests
import aiohttp


from agptools.helpers import (
    expandpath,
    I,
    parse_uri,
    build_uri,
    parse_xuri,
)
from agptools.progress import Progress
from agptools.containers import (
    walk,
    myassign,
    rebuild,
    SEP,
    list_of,
    overlap,
    soft,
    build_paths,
    combine_uri,
    expand_expression,
)

# from agptools.calls import scall

from agptools.logs import logger
from syncmodels import __version__
from syncmodels.definitions import (
    PATH_KEY,
    KIND_KEY,
    METHOD_KEY,
    FUNC_KEY,
    MONOTONIC_KEY,
    CRAWLER_KEY,
    BOT_KEY,
    ORG_URL,
    PREFIX_URL,
    CALLABLE_KEY,
    # MONOTONIC_SINCE,
    # MONOTONIC_SINCE_KEY,
    # MONOTONIC_SINCE_VALUE,
    REG_PRIVATE_KEY,
    # REG_SPLIT_PATH,
    # URI,
    # DURI,
    # JSON,
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
from syncmodels.model import BaseModel
from syncmodels.registry import iRegistry
from syncmodels.auth import iAuthenticator
from syncmodels.storage import WaveStorage
from syncmodels.exceptions import NonRecoverable
from syncmodels.syncmodels import SyncModel, COPY
from .crud import parse_duri, DEFAULT_DATABASE, DEFAULT_NAMESPACE, tf


# from syncmodels.syncmodels import Transformer


from .helpers import analyze_url
from .context import iContext
from .requests import iResponse
from .runner import iRunner

from .session import iSession

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------
log = logger(__name__)

DEFAULT = "__default__"
UNKNOWN = "__unknown__"

SINGLE = "single"  # single stream sub-type element, not a list
REG_KIND = r"(?P<parent>[^-]*)(-(?P<sub>.*))?$"


# ---------------------------------------------------------
# SQL Bots
# ---------------------------------------------------------


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------
class iAgent(iRunner):
    "the minimal interface for an agent in crawler module"
    CREDENTIALS = {}

    @classmethod
    def clean(cls):
        "clean shared (classmethod) data"

    def __init__(
        self,
        config_path=None,
        include=None,
        exclude=None,
        credentials=None,
        prefix="",
        *args,
        **kw,
    ):
        super().__init__(*args, **kw)

        # tasks to be included or excluded
        self.include = include or [".*"]
        self.exclude = exclude or []
        self.credentials = {
            **self.CREDENTIALS,
            **(credentials or {}),
        }
        self.prefix = prefix
        _uri = parse_duri(prefix)
        if not _uri["_path"] and (
            m := re.match(r"/?(?P<prefix>.*?)/?$", prefix)
        ):
            d = m.groupdict()
            if d["prefix"]:
                self.prefix = "/{prefix}".format_map(d)

        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)
        self.root = os.path.dirname(config_path)
        self.stats_path = os.path.join(self.root, "stats.yaml")

        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)

        try:
            with open(config_path, "rt", encoding="utf-8") as f:
                self.cfg = yaml.load(f, Loader=yaml.Loader)
        except Exception:
            self.cfg = {}

        self.cfg.update(kw)

    async def _bootstrap(self):
        "Add the initial tasks to be executed by agent"
        log.info(">> [%s] entering bootstrap()", self.name)

        # get iWave storages (if any) to get the starting
        # point of the synchronization
        i = -1
        _tasks = self.bootstrap
        if not isinstance(_tasks, list):
            _tasks = [_tasks]

        tasks = []
        for _ in _tasks:
            if _ is None:
                tasks.extend(self.default_bootstrap())
            else:
                tasks.append(_)

        for i, task in enumerate(tasks):
            task.setdefault(FUNC_KEY, "get_data")
            log.info("+ [%s]: [%s] %s", i, self.name, task)

            task[PREFIX_URL] = self.prefix
            wave0 = await self._get_initial_wave(task)
            if not wave0:
                log.warning(
                    "Can't find initial sync wave for task: [%s]",
                    task,
                )
            else:
                task.setdefault(MONOTONIC_KEY, wave0)

            self.add_task(task)
        if i < 0:
            log.info("[%s] no task provided by bootstrap()", self.name)

        log.info("<< [%s] exit bootstrap()", self.name)

    # async def bootstrap(self):
    # "Add the initial tasks to be executed by crawler"

    async def idle(self):
        "default implementation when loop has nothing to do"
        if self.remain_tasks() < 1:
            log.info("[%s] hasn't more pending tasks", self)
            # self.running = False
            await asyncio.sleep(0.1)
        else:
            await asyncio.sleep(0.1)

    async def _get_initial_wave(self, *args, **kw):
        return 0

    def default_bootstrap(self):
        """Provide the initial tasks to ignite the process

        yield a tuple with:
          - function to be executed | name of the function (to be located in any iBot instance)
          - args (call args, if any)
          - kwargs (call kwargs, if any)

        Note: KIND_KEY is the name of the item kind to be synced
              Must match the mapper name in MAPPERS
        """
        return []

    def add_task(self, task, expire=0):
        "add a new pending task to be executed by this iAgent"
        raise NotImplementedError()


# ---------------------------------------------------------
# iPlugin
# ---------------------------------------------------------
class iPlugin:
    "A plugin that manipulate received data before giving to main crawler"
    SPECS = {}

    def __init__(self, bot=None, specs=None):
        self.bot = bot
        specs = {} if specs is None else specs
        self.specs = overlap(specs, self.SPECS, overwrite=True)
        self.stats = {}

    def handle(self, data, **context):
        return data, context

    @classmethod
    def matches(self, serie, *patterns):
        for string in serie:
            string = str(string)
            for pattern in patterns:
                if re.match(pattern, string):
                    yield string


class iStreamPlugin(iPlugin):
    """Plugins that received the whole stream instead single data"""


class iPrePlugin(iStreamPlugin):
    """Plugins that must be executed at the beginning of process, just once"""

    SPECS = {
        **iPlugin.SPECS,
    }


class iPostPlugin(iStreamPlugin):
    """Plugins that must be executed at the end of process, just once"""

    SPECS = {
        **iPlugin.SPECS,
    }


class iEachPlugin(iPlugin):
    """Plugins that must be executed for each data received"""

    SPECS = {
        **iPlugin.SPECS,
    }


class NormalizeStreamKeys(iPrePlugin):
    NEED_KEYS = {
        "result": r"result|data",
        "meta": r"meta|info",
    }

    def handle(self, stream, **context):
        #  try to find if match the typical structure

        assert isinstance(stream, list)
        _stream = []
        for item in stream:
            if isinstance(item, dict):
                _item = {}
                used = set()
                for key, pattern in self.NEED_KEYS.items():
                    for k, v in item.items():
                        if re.match(pattern, k):
                            _item[key] = v
                            used.add(k)
                            break
                # complement with not used keys
                for k in used.symmetric_difference(item):
                    _item[k] = item[k]

                # if not set(_item).difference(self.NEED_KEYS):
                # _stream.append(_item)
                _stream.append(_item)
            else:
                _stream.append(item)
        stream = _stream
        return stream, context


class UnwrapStream(iPrePlugin):
    NEED_KEYS = {
        "result",
        "meta",
    }

    def handle(self, stream, **context):
        #  try to find if match the typical structure
        #  TODO: review with josega Multimedia Stats crawler
        assert isinstance(stream, list)
        _stream = []
        for data in stream:
            if isinstance(data, dict) and self.NEED_KEYS.issubset(data):
                _data = data["result"]
                if isinstance(_data, list):
                    _stream.extend(_data)
                    soft(context, data["meta"])
                    continue
            _stream.append(data)
        return _stream, context


# ---------------------------------------------------------
# Bot
# ---------------------------------------------------------
PLUGIN_FAMILIES = set([iPrePlugin, iEachPlugin, iPostPlugin])
"the allowed flow execution families for any plugin"


class iBot(iAgent):
    "Interface for a bot"

    MAX_RETRIES = 15
    DEFAULT_PARAMS = {}
    ALLOWED_PARAMS = [".*"]
    # allowed params from context to build the query

    EXCLUDED_PARAMS = list(parse_uri(""))

    MAX_QUEUE = 200
    DONE_TASKS = {}  # TODO: review faster method

    @classmethod
    def blueprint(cls, **params):
        keys = list(params)
        keys.sort()
        blueprint = [(k, params[k]) for k in keys]
        blueprint = str(blueprint)
        blueprint = hashlib.md5(blueprint.encode("utf-8")).hexdigest()
        return blueprint

    def __init__(
        self,
        *args,
        parent=None,
        context=None,
        headers=None,
        **kw,
    ):
        super().__init__(*args, **kw)
        self.fiber = None
        self.plugins = {}
        self.parent = parent

        context = context or {}
        self.headers = headers or {}
        self.context = {
            **context,
            **self.headers,
            **kw,
        }

        self._sessions: Dict[str, iSession] = {}

    @classmethod
    def clean(cls):
        "clean shared (classmethod) data"
        # cls.DONE_TASKS.clear()

    def add_plugin(self, plugin: iPlugin):
        "add a new plugin to be executed by this iBot grouped by some PLUGIN_FAMILIES"
        assert isinstance(
            plugin, iPlugin
        ), f"{plugin} is not a subclass of iPlugin!"
        for klass in PLUGIN_FAMILIES:
            if isinstance(plugin, klass):
                self.plugins.setdefault(klass, []).append(plugin)
                break
        else:
            raise RuntimeError(
                f"plugin: {plugin} does not belongs to {PLUGIN_FAMILIES} allowed classification categories"
            )
        if not plugin.bot:
            plugin.bot = self

    def can_handle(self, func, *args, **kw):
        "return if the function can be handled by this iBot"
        return True

    def process(self, klass, data: Dict | List[Dict], **context):
        "chain execution for all plugins of the given `klass` or transforming the data"
        # check the data received with the kind of pluggin
        if issubclass(klass, iStreamPlugin):
            if not isinstance(data, list):
                raise RuntimeError(
                    f"for plugins [{klass}], data must be a list of dict"
                )
        elif issubclass(klass, iEachPlugin):
            if not isinstance(data, dict):
                raise RuntimeError(
                    f"for plugins [{klass}], data must be a dict"
                )

        for plugin in self.plugins.get(klass, []):
            data, context = plugin.handle(data, **context)
            if not data:
                break
        return data, context

    def add_task(self, task, expire=0):
        "add a new pending task to be executed by this iBot"
        # universe = list(kw.values()) + list(args)

        # def check():
        #     "check if this task must be considered or ignored"
        #     return True
        #     # for string in universe:
        #     #     string = str(string)
        #     #     for pattern in self.include:
        #     #         if re.match(pattern, string):
        #     #             return True
        #     #     for pattern in self.exclude:
        #     #         if re.match(pattern, string):
        #     #             return False
        if CALLABLE_KEY in task:
            # process itself
            self.input_queue.push(task, expire)
        else:
            assert isinstance(task[FUNC_KEY], str)
            # must be processed by parent for round_robin
            if self.parent:
                self.parent.add_task(task, expire=expire)
            else:
                log.warning(
                    "[%s] hasn't parent trying to process: %s",
                    self.name,
                    task,
                )

    async def _add_plugins(self):
        # add plugins
        self.add_plugin(Cleaner())

    async def get_task(self, timeout=2) -> dict:
        "get the next task or raise a timeout exception"
        while (pending := self.output_queue.qsize()) > self.MAX_QUEUE:
            now = time.time()
            if now - self._last_announce > 10:
                print(
                    f"Pause worker due too much results pending in queue: {pending}"
                )
            self._last_announce = now
            await asyncio.sleep(1)

        return await super().get_task(timeout=timeout)

    async def hide_run(self) -> bool:
        "the entry point / main loop of a single `fiber` in pool"
        progress = Progress(label=self.name)

        log.info(">> [%s] entering run()", self.name)
        log.info(" > [%s] adding plugins", self.name)
        await self._add_plugins()
        log.info(" < [%s] adding plugins done", self.name)
        await super().run()

        self._last_announce = 0
        while True:
            try:
                while (
                    pending := self.output_queue.qsize()
                ) > self.MAX_QUEUE:
                    now = time.time()
                    if now - self._last_announce > 10:
                        print(
                            f"Pause worker due too much results pending in queue: {pending}"
                        )
                    self._last_announce = now
                    await asyncio.sleep(1)

                progress.update(pending=pending)

                # Get a task from the queue
                task = await asyncio.wait_for(
                    self.input_queue.get(), timeout=5
                )
                if task is None:
                    break  # Break the loop
                try:
                    self._wip.append(1)
                    func = task.pop(CALLABLE_KEY)
                    async for data in func(**task):
                        item = task, data
                        # Note: self.output_queue --> parent/crawler.input_queue
                        await self.output_queue.put(item)
                except Exception as why:  # pragma: nocover
                    log.error(why)
                    log.error(
                        "".join(traceback.format_exception(*sys.exc_info()))
                    )
                finally:
                    self._wip.pop()
            except queue.Empty:
                pass
            except asyncio.exceptions.TimeoutError:
                pass
            except Exception as why:  # pragma: nocover
                log.error(why)
                log.error(
                    "".join(traceback.format_exception(*sys.exc_info()))
                )

        log.info("<< [%s] exit run()", self.name)

    async def hide_dispatch(self, task, data, *args, **kw):
        "do nothing"
        log.info(" - dispatch: %s: %s ; %s, %s", task, data, args, kw)

    def remain_tasks(self):
        "compute how many pending tasks still remains"
        return len(self._wip) + self.input_queue.qsize()

    async def stop(self):
        await super().stop()
        await self.parent.remove_bot(self)
        foo = 1

    async def _get_session(self, url, **context) -> iSession:
        uri = parse_uri(url)
        session = self._sessions.get(uri["xhost"])
        if session is None:
            session = self._sessions[uri["xhost"]] = await iSession.new(
                url, bot=self, **context
            )
        return session

    async def hide_get_data(self, **task):
        """
        Example a crawling function for recommender crawler.

        Get data related to the given kind and path.
        May add more tasks to be done by crawler.
        """
        context = {
            CRAWLER_KEY: self.parent,
            BOT_KEY: self,
            # "limit": 50,
            # "offset": 0,
            **task,
        }
        # method to gather the information from 3rd system
        stream, meta = await self._get_data(**context)
        if not stream:
            return

        if isinstance(
            stream,
            (
                list,
                types.GeneratorType,
            ),
        ):
            ##log.debug("received (%s) items of type '%s'", len(stream), context['kind'])
            pass
        else:
            ##log.debug("received a single items of type: '%s'", context['kind'])
            stream = [stream]

        log.info(
            "received (%s) items of type '%s'",
            len(stream),
            context[KIND_KEY],
        )

        context.update(meta)

        # transform the stream if needed before proccesing each item
        stream, context = self.process(iPrePlugin, stream, **context)

        # process each item from stream
        for _, org in enumerate(stream):
            # data = {**data, **org}

            data = {**org}
            data, ctx = self.process(iEachPlugin, data, **context)

            yield data, (ctx, org)
            # if random.random() < 0.05:
            # await asyncio.sleep(0.25)  # to be nice with other fibers
            ##log.debug("[%s]:[%s]#%s: processed", i, context['kind'], data.get('id', '-'))

        # last chance to execute any action or request more data
        # based on the received stream, i.e. pagination, stats, etc
        stream, context = self.process(iPostPlugin, stream, **context)

        # don't update metadata here
        # tube must be full-qualified with crawler prefix
        # tube = context[KIND_KEY]
        # meta = {
        #     k: v
        #     for k, v in context.items()
        #     if isinstance(v, (int, float, str, dict, list))
        # }
        # await self.parent.update_meta(tube, meta)

    async def get_data(self, **task):
        """
        Example a crawling function for recommender crawler.

        Get data related to the given kind and path.
        May add more tasks to be done by crawler.
        """
        context = {
            CRAWLER_KEY: self.parent,
            BOT_KEY: self,
            # "limit": 50,
            # "offset": 0,
            **task,
        }
        # method to gather the information from 3rd system
        stream, meta = await self._get_data(**context)
        if stream:
            self.add_task(
                {
                    CALLABLE_KEY: self.process_stream,
                    "stream": stream,
                    "meta": meta,
                    "context": context,
                    **task,
                }
            )

    async def process_stream(self, stream, meta, context, **task):
        """
        TBD
        """
        if isinstance(
            stream,
            (
                list,
                types.GeneratorType,
            ),
        ):
            ##log.debug("received (%s) items of type '%s'", len(stream), context['kind'])
            pass
        else:
            ##log.debug("received a single items of type: '%s'", context['kind'])
            stream = [stream]

        log.info(
            "received (%s) items of type '%s'",
            len(stream),
            context[KIND_KEY],
        )

        context.update(meta)

        # transform the stream if needed before proccesing each item
        stream, context = self.process(iPrePlugin, stream, **context)

        # process each item from stream
        for _, org in enumerate(stream):
            # data = {**data, **org}

            data = {**org}
            data, ctx = self.process(iEachPlugin, data, **context)

            result = {
                FUNC_KEY: "inject",
                "task": task,
                "data": (data, (ctx, org)),
            }
            self.output_queue.push(result)

            # yield data, (ctx, org)
            # if random.random() < 0.05:
            # await asyncio.sleep(0.25)  # to be nice with other fibers
            ##log.debug("[%s]:[%s]#%s: processed", i, context['kind'], data.get('id', '-'))

        # last chance to execute any action or request more data
        # based on the received stream, i.e. pagination, stats, etc
        stream, context = self.process(iPostPlugin, stream, **context)

        # don't update metadata here
        # tube must be full-qualified with crawler prefix
        # tube = context[KIND_KEY]
        # meta = {
        #     k: v
        #     for k, v in context.items()
        #     if isinstance(v, (int, float, str, dict, list))
        # }
        # await self.parent.update_meta(tube, meta)

    async def _get_data(self, **context):
        "A helper method to get the data from external system"

        soft(context, self.DEFAULT_PARAMS)
        # TODO: MONOTONIC_KEY context must be passed to iSession
        params = self._build_params(**context)

        path = context.get(PATH_KEY, "")
        _source = parse_duri(self.parent.app_url)
        _local = parse_xuri(path)
        _uri = combine_uri(
            _source,
            _local,
            context,
        )
        url = build_uri(**_uri)

        exception_raised = None
        # get the session related to this url
        proxy = await self._get_session(url, **context)

        # provide extra params to the proxy before calling EP
        call_kw = await proxy.update_params(url, params, context)

        timeout = self.parent.cache_timeout
        assert "url" in call_kw
        if self._set_already(timeout=timeout, **call_kw):
            # self._set_already(url, **params)
            try:
                for tries in range(1, self.MAX_RETRIES):
                    try:
                        exception_raised = None
                        # authenticate when is needed
                        # await proxy.authenticate(url, params)
                        # a chance to create a more specific instance in a context
                        # to deal with the real get() method
                        async with proxy as session:
                            # log.debug(
                            # "[%s][%s/%s] %s : %s", self.name, tries, self.MAX_RETRIES, url, params
                            # )
                            # merge headers without key conflicts
                            soft(call_kw["headers"], self.headers)
                            method = getattr(
                                session, context.get(METHOD_KEY, "get")
                            )
                            response = await method(**call_kw)

                            async with response:
                                if 200 <= response.status < 300:
                                    stream, meta = (
                                        await proxy._process_response(
                                            response
                                        )
                                    )
                                    soft(meta, params)
                                    return stream, meta
                                #  https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
                                elif response.status in (401, 403, 404, 407):
                                    # forbidden
                                    result = await extract_result(response)
                                    # result = await response.text()
                                    log.error(
                                        "[%s] server sent: %s",
                                        response.status,
                                        result,
                                    )
                                    # await proxy.authenticate(url, params)

                                    await iAuthenticator.auth(
                                        url, params, proxy
                                    )

                                    await asyncio.sleep(0.1)
                                    continue
                                elif 400 <= response.status < 500:
                                    log.warning(
                                        "Status: %s, ABORT, not recoverable error",
                                        response.status,
                                    )
                                    ##log.debug("%s: %s: %s", response.status, path, params)
                                    # result = await response.json()
                                    result = await extract_result(response)

                                    log.error("server sent: %s", result)
                                    raise NonRecoverable(result)
                                elif 500 <= response.status < 600:
                                    log.warning(
                                        "Status: %s, RETRY", response.status
                                    )
                                    ##log.debug("%s: %s: %s", response.status, path, params)
                                    # result = await response.json()
                                    # log.error("server sent: %s", result)
                                else:
                                    log.error("Status: %s", response.status)
                    except NonRecoverable:
                        break
                    except Exception as why:  # pragma: nocover
                        log.error(why)
                        msg = "".join(
                            traceback.format_exception(*sys.exc_info())
                        )
                        log.error(msg)
                        exception_raised = why

                    log.warning("retry: %s: %s, %s", tries, path, params)
                    await asyncio.sleep(0.5)
            except Exception as why:  # pragma: nocover
                log.error(why)
                msg = "".join(traceback.format_exception(*sys.exc_info()))
                log.error(msg)
                exception_raised = why

            finally:
                # self._set_already(url)
                if exception_raised:
                    raise exception_raised
        else:
            log.info("[%s] SKIPPING %s : %s", self.name, url, params)

        return None, None

    def _build_params(self, **context):
        params = {}

        def match(text) -> bool:
            if re.match(REG_PRIVATE_KEY, text):
                return False

            if text in self.EXCLUDED_PARAMS:
                return False

            for pattern in self.ALLOWED_PARAMS:
                if re.match(pattern, text):
                    return True

            return False

        # TODO: remove / deprecated
        if "kind" in context:
            log.warning(
                "['%s'] key is deprecated, use KIND_KEY instead", "kind"
            )
            context[KIND_KEY] = context.pop("kind")

        for k, v in context.items():
            if match(k) and isinstance(v, (int, str, float)):
                params[k] = v

        return params

    def _is_already(self, timeout=600, **params):
        blueprint = self.blueprint()
        last = self.DONE_TASKS.get(blueprint, 0)
        return time.time() - last < timeout

    def _set_already(self, timeout=600, **params):
        if not self._is_already(timeout=timeout, **params):
            blueprint = self.blueprint(**params)
            self.DONE_TASKS[blueprint] = time.time()
            return True
        return False

    def _clean_already(self):
        self.DONE_TASKS.clear()


# ---------------------------------------------------------
# Helper Plugins
# ---------------------------------------------------------
class Cleaner(iEachPlugin):
    SPECS = {
        **iEachPlugin.SPECS,
    }

    def handle(self, data, **context):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        return data, context


class RegExtractor(iEachPlugin):
    # example for gitLab
    SPECS = {
        **iEachPlugin.SPECS,
    }

    def handle(self, data, **context):
        # TODO: review
        # TODO: create a reveal + regexp + SEP ?

        aux = {**data, **context}
        values = list([aux[x] for x in self.matches(aux, "path")])

        # for key in self.matches(aux, KIND_KEY):
        # kind = aux[key]
        for regexp in self.specs:
            for value in values:
                m = re.match(regexp, value)
                if m:
                    data.update(m.groupdict())
        return data, context


class Restructer(iEachPlugin):
    # example for gitLab
    SPECS = {
        **iEachPlugin.SPECS,
    }

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.__mask_restruct_data()

    def __mask_restruct_data(self):
        for container in self.specs.values():
            for k in list(container):
                if SEP in k:
                    continue
                v = container.pop(k)
                k = k.replace("/", SEP)
                v = tuple([v[0].replace("/", SEP), *v[1:]])
                container[k] = v

    def handle(self, data, **context):
        restruct = {}
        kind = context.get(KIND_KEY, UNKNOWN)
        info = self.specs.get("default", {})
        info.update(self.specs.get(kind, {}))
        reveal = build_paths(data)
        for path, value in reveal.items():
            for pattern, (new_path, new_value) in info.items():
                m = re.match(pattern, path)
                if m:
                    d = m.groupdict()
                    d["value"] = value
                    key = tuple(new_path.format_map(d).split(SEP))
                    _value = (
                        value
                        if new_value == COPY
                        else new_value.format_map(d)
                    )
                    restruct[key] = _value

        restruct = rebuild(restruct, result={})
        data = {**data, **restruct}

        return data, context


class FQIUD(iEachPlugin):
    SPECS = {
        **iEachPlugin.SPECS,
        "root": ("{url}", I, "url"),
        # 'groups': ("{id}", int, 'id'),
    }

    def handle(self, data, **context):
        patterns = context.get("kind_key", KIND_KEY)
        for key in self.matches(data, patterns):
            kind = data[key]
            for specs in self.specs.get(kind, []):
                if not specs:
                    continue
                uid_key, func, id_key = specs
                try:
                    uid = uid_key.format_map(data)
                    fquid = func(uid)
                    data[id_key] = fquid
                    data["_fquid"] = fquid
                    data["_uid"] = uid
                    return data
                except Exception as why:  # pragma: nocover
                    # TODO: remove, just debugging
                    log.error(why)
                    log.error(
                        "".join(traceback.format_exception(*sys.exc_info()))
                    )
        return data, context


class Tagger(iEachPlugin):
    SPECS = {
        **iEachPlugin.SPECS,
    }

    def handle(self, data, **context):
        return data, context


class DeepSearch(iEachPlugin):
    SPECS = {
        **iEachPlugin.SPECS,
    }

    def handle(self, data, **context):
        aux = {**data, **context}
        patterns = aux.get("kind_key", KIND_KEY)

        for key in self.matches(aux, patterns):
            kind = aux.get(key)
            for specs in self.specs.get(kind, []):
                if not specs:
                    continue
                try:
                    sub_kind, sub_url = specs
                    sub_url = sub_url.format_map(aux)
                    aux[key] = sub_kind
                    aux["path"] = sub_url

                    self.bot.add_task(
                        func="get_data",
                        **aux,
                    )
                except Exception as why:  # pragma: nocover
                    # TODO: remove, just debugging
                    log.error(why)
                    log.error(
                        "".join(traceback.format_exception(*sys.exc_info()))
                    )

        return data, context


class PaginationDisabled:
    "represent no pagination for an item"


class iPaginationPlugin(iPostPlugin):
    PER_PAGE = "per_page"

    MAX_PAGES = "max_pages"
    FIRST_PAGE = "first_page"
    AHEAD_PAGES = "ahead_pages"
    PAGE = "page"

    FIRST_ITEM = "first_item"
    MAX_ITEMS = "max_items"
    OFFSET = "offset"


class GenericPagination(iPaginationPlugin):

    SPECS = {
        **iPostPlugin.SPECS,
        **{
            DEFAULT: {
                iPaginationPlugin.MAX_ITEMS: "count",
                iPaginationPlugin.MAX_PAGES: "max_pages",
                iPaginationPlugin.OFFSET: "offset",
                iPaginationPlugin.PER_PAGE: "limit",
                iPaginationPlugin.FIRST_ITEM: 0,
            },
            "gitlab": {
                iPaginationPlugin.PAGE: "page",
                iPaginationPlugin.PER_PAGE: "per_page",
                iPaginationPlugin.FIRST_PAGE: 1,
                iPaginationPlugin.AHEAD_PAGES: 1,
            },
        },
    }

    def handle(self, data, **context):
        "Request the next pagination (just the next one!)"

        for name, spec in self.specs.items():
            page = int(context.get(spec[self.PAGE], -1))
            per_page = int(context.get(spec[self.PER_PAGE], 50))
            if context.get(spec.get(self.MAX_ITEMS), -1) < page * per_page:
                page = max(page, spec.get(self.FIRST_PAGE, 0))
                for batch in range(spec.get(self.AHEAD_PAGES, 1)):
                    context[spec[self.PAGE]] = page + 1
                    ##log.debug("> request: %s", context)
                    self.bot.add_task(
                        func="get_data",  # TODO: extract from context
                        # **data,
                        **context,
                    )
                break
        return data, context


class SimplePagination(iPaginationPlugin):
    """
    kind: specs_for_this_kind

    used: kind: [] to explicit avoid pagination
    DEFAULT: a default pagination when no other is defined
    """

    SPECS = {
        # **iPostPlugin.SPECS, # don't use base class
        **{
            DEFAULT: {
                iPaginationPlugin.PAGE: "page",
                iPaginationPlugin.PER_PAGE: "per_page",
                iPaginationPlugin.FIRST_PAGE: 1,
                iPaginationPlugin.AHEAD_PAGES: 1,
            },
            # "groups": {},
            # "projects": {},
            # "users": {},
            # "wikis": {},
            # "issues": {},
            # "milestones": {},
            # "notes": {},
        },
    }

    def handle(self, stream, **context):
        "Request the next pagination"
        kind = context.get(KIND_KEY, UNKNOWN)
        spec = self.specs.get(kind, self.specs.get(DEFAULT))

        # poi and poi-single
        d = re.match(REG_KIND, kind).groupdict()
        if spec == PaginationDisabled or d["sub"] in (SINGLE,):
            # single items doesn't use pagination
            ##log.debug("skip pagination for '%s'", kind)
            # remove parent pagination context
            kind = d["parent"]
            spec = self.specs.get(kind, self.specs.get(DEFAULT))
            if spec:
                foo = 1
            for k in spec.values():
                context.pop(k, None)
            foo = 1
        else:
            ##log.debug("for '%s' use pagination: %s", kind, spec)
            ##log.debug("page: %s, per_page: %s", page, per_page)

            # we have 2 options: pagination based on pages or based on num items
            per_page = int(context.get(spec.get(self.PER_PAGE), 20))
            max_items = context.get(spec.get(self.MAX_ITEMS))
            page = context.get(spec.get(self.PAGE))
            offset = int(context.get(spec.get(self.OFFSET), -1))
            offset = max(offset, spec.get(self.FIRST_ITEM, 0))
            if max_items is not None:
                if max_items > offset:
                    for batch in range(spec.get(self.AHEAD_PAGES, 1)):
                        context[spec[self.OFFSET]] = offset + per_page
                        ##log.debug("> request page: [%s]:%s", kind, context.get(spec[self.PAGE], -1))

                        # use name instead callable so crawler can assign the
                        # request to another bot apartt current one
                        # using calleable will always assign the task to itself
                        func_name = context[FUNC_KEY].__name__

                        self.bot.add_task(
                            func=func_name,
                            # **data,
                            **context,
                        )

            elif page is not None:
                page = max(offset, spec.get(self.FIRST_PAGE, 0))
                max_pages = max(
                    page, spec.get(self.MAX_PAGES, sys.float_info.max)
                )

                if max_pages >= page:
                    for batch in range(spec.get(self.AHEAD_PAGES, 1)):
                        context[spec[self.PAGE]] = page + per_page
                        ##log.debug("> request page: [%s]:%s", kind, context.get(spec[self.PAGE], -1))
                        self.bot.add_task(
                            func="get_data",  # TODO: extract from context
                            # **data,
                            **context,
                        )

            else:
                log.debug("no pagination info found")

        return stream, context


# ---------------------------------------------------------
# HTTP Bots
# ---------------------------------------------------------


class HTTPBot(iBot):
    "Basic HTTPBot"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.headers = {
            # USER_AGENT: f"python-{self.__class__.__name__.lower()}/{__version__}",
            USER_AGENT: "Mozilla/5.0 (X11; Linux i686; rv:125.0) Gecko/20100101 Firefox/125.0",
            CONTENT_TYPE: APPLICATION_JSON,
            # "Authorization": f"Bearer {personal_access_token}",
        }

    async def _add_plugins(self):
        await super()._add_plugins()
        self.add_plugin(NormalizeStreamKeys())
        self.add_plugin(UnwrapStream())

        # self.add_plugin(RegExtractor())
        # self.add_plugin(Cleaner())
        # self.add_plugin(FQIUD())
        # self.add_plugin(DeepSearch())
        # self.add_plugin(SimplePagination())


# ---------------------------------------------------------
# SQL Bots
# ---------------------------------------------------------


class SQLBot(iBot):
    "Basic SQLBot"

    # RESPONSE_META = ["headers", "links", "real_url"]
    TABLE_NAME = {
        DEFAULT: "{name}",
    }
    "syncmodel table for a particular database schema"
    WAVE_COLUMN_NAME = {
        DEFAULT: MONOTONIC_KEY,
    }
    "wave column for a particular table"

    #
    MAX_RETRIES = 15
    DEFAULT_PARAMS = {}
    ALLOWED_PARAMS = [".*"]
    # allowed params from context to build the query

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # self.add_plugin(RegExtractor())
        # self.add_plugin(Cleaner())
        # self.add_plugin(FQIUD())
        # self.add_plugin(DeepSearch())
        # self.add_plugin(SimplePagination())
        # self.headers = {
        # "User-Agent": "python-httpbot/0.1.0",
        # "Content-type": "application/json",
        ## "Authorization": f"Bearer {personal_access_token}",
        # }

    async def get_rows(self, **context):
        """
        Example a crawling function for recommender crawler.

        Get data related to the given kind and path.
        May add more tasks to be done by crawler.
        """
        context = {
            # "limit": 50,
            # "offset": 0,
            **context,
        }
        # method to gather the information from 3rd system
        stream, meta = await self._get_rows(**context)
        if not stream:
            return

        if isinstance(stream, list):
            ##log.debug("received (%s) items of type '%s'", len(stream), context['kind'])
            pass
        else:
            ##log.debug("received a single items of type: '%s'", context['kind'])
            stream = [stream]

        context.update(meta)
        for _, org in enumerate(stream):
            # data = {**data, **org}
            data = {**org}
            data, ctx = self.process(iEachPlugin, data, **context)

            yield data, (ctx, org)
            # if random.random() < 0.05:
            # await asyncio.sleep(0.25)  # to be nice with other fibers
            ##log.debug("[%s]:[%s]#%s: processed", i, context['kind'], data.get('id', '-'))

        # params['offset'] = (page := page + len(result))
        data, context = self.process(iPostPlugin, data, **context)

    async def _get_rows(self, path, **context):
        "A helper method to get the data from external system"

        soft(context, self.DEFAULT_PARAMS)
        params = self._build_params(**context)

        uri = parse_uri(path)
        if not uri["host"]:
            uri2 = self.context["app_url"]  # must exists!
            uri2 = parse_uri(uri2)
            uri["path"] = uri2["path"] = (uri2["path"] or "") + uri["path"]
            uri = overlap(uri2, uri, overwrite=True)
        uri["query_"] = params

        #
        url = build_uri(**uri)
        # print(url)
        if self._is_already(url):
            ##log.info("[%s] SKIPING %s : %s", self.name, url, params)
            foo = 1
        else:
            self._set_already(url)
            try:
                for tries in range(1, self.MAX_RETRIES):
                    try:
                        session = self._get_session()

                        async with aiohttp.ClientSession() as session:
                            # log.debug(
                            # "[%s][%s/%s] %s : %s", self.name, tries, self.MAX_RETRIES, url, params
                            # )
                            async with session.get(
                                url, headers=self.headers, params=params
                            ) as response:
                                if response.status in (200,):
                                    stream, meta = (
                                        await proxy._process_response(
                                            response
                                        )
                                    )
                                    soft(meta, params)
                                    return stream, meta
                                elif response.status in (400, 404):
                                    log.warning(
                                        "Status: %s, RETRY", response.status
                                    )
                                    ##log.debug("%s: %s: %s", response.status, path, params)
                                    # result = await response.json()
                                    # log.error("server sent: %s", result)
                                elif response.status in (403,):
                                    log.error(
                                        "Status: %s, SKIPPING",
                                        response.status,
                                    )
                                else:
                                    log.error("Status: %s", response.status)
                    except Exception as why:  # pragma: nocover
                        log.error(why)
                        log.error(
                            "".join(
                                traceback.format_exception(*sys.exc_info())
                            )
                        )
                    log.warning("retry: %s: %s, %s", tries, path, params)
                    await asyncio.sleep(0.5)
            finally:
                # self._set_already(url)
                pass
        return None, None

    def _is_already(self, url):
        return url in self.DONE_TASKS

    def _set_already(self, url):
        if not self._is_already(url):
            self.DONE_TASKS[url] = time.time()
            return True
        return False


# ---------------------------------------------------------
# Crawler
# ---------------------------------------------------------
class iCrawler(iAgent):
    "Interface for a crawler"
    bots: Dict[Any, iBot]

    def __init__(
        self,
        syncmodel: SyncModel = None,
        raw_storage=None,
        app_url=None,
        *args,
        **kw,
    ):
        super().__init__(*args, **kw)
        self.bot: Dict[str, iBot] = {}
        self.round_robin: deque[iBot] = deque()

        self.stats = {}
        self.show_stats = True
        self.syncmodel = list_of(syncmodel, SyncModel)
        self.raw_storage = raw_storage

        self.app_url = app_url or self.cfg.get("app_url") or ""
        # self.app_url = (
        # self.cfg["app_url_dev"] if app_url else self.cfg["app_url"]
        # )
        self._app_uri = parse_uri(self.app_url)

    async def hide_run(self) -> bool:
        """TBD"""
        await super().run()

    def _storages(self, klass):
        "get storages that match some class"
        result = []
        for syncmodel in self.syncmodel:
            for storage in syncmodel.storage:
                if isinstance(storage, klass):
                    result.append(storage)
        return result

    def add_task(self, task, expire=0):
        "add a new pending task to be executed by a bot that match the profile"
        func = task[FUNC_KEY]

        assert isinstance(
            func, str
        ), f"'func' must be a function name, not {func}"

        # overlap(kw, self._app_uri)
        candidates = self.round_robin
        for _ in range(len(candidates)):
            candidates.rotate(-1)
            bot = candidates[-1]
            if call := getattr(bot, func):
                if bot.can_handle(task):
                    # replace for a direct callable
                    task[CALLABLE_KEY] = call
                    bot.add_task(task, expire=expire)
                    break
        else:
            log.warning(
                "can't find a callable for `%s` in (%s) bots",
                len(candidates),
            )

    def remain_tasks(self):
        "compute how many pending tasks still remains"
        n = super().remain_tasks()
        for bot in self.bot.values():
            n += bot.remain_tasks()
        return n


class iAsyncCrawler(iCrawler):
    """A crawler that uses asyncio"""

    DEFAULT_APP_URL = ""
    DEFAULT_PREFIX = ""  # TODO: define a placement for these data

    # need to be redefined by subclass
    MODEL = None
    BOTS = [HTTPBot]

    # governance data
    MAPPERS = {}
    RESTRUCT_DATA = {}
    RETAG_DATA = {}
    REFERENCE_MATCHES = []
    KINDS_UID = {}

    def __init__(
        self,
        *args,
        app_url=None,
        prefix=None,
        fibers=1,
        restart=None,
        cycles=1,
        cache_timeout=600,
        **kw,
    ):
        super().__init__(
            app_url=app_url or self.DEFAULT_APP_URL,
            prefix=prefix or self.DEFAULT_PREFIX,
            *args,
            **kw,
        )
        self.fibers = fibers

        self.restart = restart
        self.cycles = cycles
        self.cache_timeout = cache_timeout

        self.model = self.MODEL() if self.MODEL else None

    def _get_mapper_from_uri(self, uri):
        _uri = parse_duri(uri)
        for key in ("uri", "thing", "path", "basename", "table"):
            candidate = _uri.get(key)
            klass = self.MAPPERS.get(candidate)
            if klass:
                return key, candidate, klass
        raise RuntimeError(f"uri: {uri} hasn't any associated mapper")

    async def _get_initial_wave(self, task):
        """Get the initial waves from storage"""
        waves = []
        storage = None
        task[ORG_URL] = self.app_url
        # task[PREFIX_URL] = self.prefix

        # have sense to require the initial wave for this uri
        # as they have a mapper to handle it
        for storage in self._storages(klass=WaveStorage):
            # last_waves(self, sources: List, uid: UID) -> Dict[str, WAVE]:
            waves.extend(await storage.last_wave(task))
            # must break here as only one wave storage
            # should be used, but just in case ...
            if waves:
                break
        else:
            log.warning("can't find initial wave for [%s]", task)

        if not storage:
            log.warning(
                "[%s] doesn't use any WaveStorage (needed for getting initial waves)",
                self,
            )
        waves.sort(key=lambda x: x.get(MONOTONIC_KEY, 0))
        return waves and waves[0]

    async def hide_run(self) -> bool:
        """Execute a full crawling loop"""
        result = True

        while self.cycles != 0:
            self.cycles -= 1

            await super().run()
            await self.start()
            await self._bootstrap()

            # wait until all work is done
            while remain := self.remain_tasks():
                try:
                    result = await asyncio.wait_for(
                        self.input_queue.get(), timeout=2
                    )
                    res = await self.dispatch(*result)
                    if not res:
                        # log.warning(
                        # "Can't save item in storage: %s", result[0][2]
                        # )
                        # log.warning("%s", pformat(result[1]))
                        self.stats["failed"] = (
                            self.stats.get("failed", 0) + 1
                        )
                        self.progress.closer()
                except queue.Empty:
                    pass
                except asyncio.exceptions.TimeoutError:
                    pass
                except Exception as why:  # pragma: nocover
                    log.error(why)
                    log.error(
                        "".join(traceback.format_exception(*sys.exc_info()))
                    )

                self.progress.update(
                    remain=remain,
                    stats=self.stats,
                    force=False,
                )

            await self.stop()

            # end of the cycle
            if self.cycles != 0:
                restart = self.restart or 1
                log.info(
                    "remaining cycles: [%s] : restart crawling in [%s] secs",
                    self.cycles,
                    restart,
                )
                await asyncio.sleep(restart)

        # result = all([await sync.save(wait=True) for sync in self.syncmodel])
        result = await self.save()
        if result:
            log.info("all storages have been saved")
        else:
            log.error("some storages have NOT been SAVED")

        return result

    async def start(self):
        "start runner"
        await super().start()
        await self._bootstrap()

    async def idle(self):
        "default implementation when loop has nothing to do"
        # check running bots
        await asyncio.sleep(0.1)
        for bot in self.bot.values():
            if not bot.remain_tasks():
                # wait until bot exit loop
                # TODO: decide where to add and remove bots
                if bot.fiber.done():
                    pass
                else:
                    log.info(
                        "from [%s]: [%s] has not remaining tasks, request stopping",
                        self,
                        bot,
                    )
                    # direct low level put, to overpass bot.add_task() checkings
                    bot.input_queue.push(None)
                    break
        else:
            if self.remain_tasks():
                # check if having not bots,
                # we have something in the input_queue
                await super().idle()
            else:
                log.info(
                    "[%s] hasn't more pending tasks, request stopping myself",
                    self,
                )
                self.input_queue.push(None)

    async def run(self) -> bool:
        """Execute a full crawling loop"""
        result = True

        while self.cycles != 0:
            self.cycles -= 1

            await super().run()

            # wait until all work is done
            while remain := self.remain_tasks():
                try:
                    result = await asyncio.wait_for(
                        self.input_queue.get(), timeout=2
                    )
                    res = await self.dispatch(*result)
                    if not res:
                        # log.warning(
                        # "Can't save item in storage: %s", result[0][2]
                        # )
                        # log.warning("%s", pformat(result[1]))
                        self.stats["failed"] = (
                            self.stats.get("failed", 0) + 1
                        )
                        self.progress.closer()
                except queue.Empty:
                    pass
                except asyncio.exceptions.TimeoutError:
                    pass
                except Exception as why:  # pragma: nocover
                    log.error(why)
                    log.error(
                        "".join(traceback.format_exception(*sys.exc_info()))
                    )

                self.progress.update(
                    remain=remain,
                    stats=self.stats,
                    force=False,
                )

            # await self.stop()

            # end of the cycle
            if self.cycles != 0:
                restart = self.restart or 1
                log.info(
                    "remaining cycles: [%s] : restart crawling in [%s] secs",
                    self.cycles,
                    restart,
                )
                await asyncio.sleep(restart)

        # result = all([await sync.save(wait=True) for sync in self.syncmodel])
        result = await self.save()
        if result:
            log.info("all storages have been saved")
        else:
            log.error("some storages have NOT been SAVED")

        return result

    async def inject(self, task, data, *args, **kw):
        "create an item from data and try to update into storage"
        # func, _args, _kw = task
        # _kw: {'kind': 'groups', 'path': '/groups?statistics=true'}
        # data:  {'id': 104, ... }

        # processed data, (execution context, original data)
        data, (context, org) = data
        kind = task[KIND_KEY]
        # task.pop(CALLABLE_KEY)  # don't propagate
        # kind = context[KIND_KEY] # equivalent

        # inject item into models
        item = self.new(kind, data, **context)
        if item is None:
            result = False
        else:
            # result = await self.syncmodel.put(item)
            result = all(
                [await sync.put(item, **task) for sync in self.syncmodel]
            )

            # save original item if a raw storage has been specified
            if self.raw_storage:
                fqid = item.id
                await self.raw_storage.put(fqid, org)

            # check if we need to do something from time to time
            t1 = time.time()
            if t1 > self.t1:
                self.t1 = t1 + self.nice
                await self.save(nice=True)

        return result

    async def update_meta(self, tube, meta: Dict) -> bool:
        log.info("Updating Meta")
        result = all(
            [
                await sync.update_meta(tube=tube, meta=meta)
                for sync in self.syncmodel
            ]
        )
        return result

    async def save(self, nice=False, wait=False):
        log.info("Saving models")
        result = all(
            [
                await sync.save(nice=nice, wait=wait)
                for sync in self.syncmodel
            ]
        )
        if self.raw_storage:
            res = await self.raw_storage.save(nice=nice, wait=wait)
            result = result and res
        return result

    async def _create_resources(self):
        """Try to adjust needed resources in every restart"""
        BOTS = deque(self.BOTS)

        for n in range(self.fibers):
            BOTS.rotate()
            klass = BOTS[-1]
            name = f"{klass.__name__.lower()}-{n}"

            klass.clean()
            if name not in self.bot:
                bot = klass(
                    output_queue=self.input_queue,
                    name=name,
                    parent=self,
                    context=self.__dict__,
                )
                await self.add_bot(bot)

    async def _stop_resources(self):
        # Add sentinel values to signal worker threads to exit
        while self.bot:
            for bot in self.bot.values():
                await self.remove_bot(bot)
                break

    async def add_bot(self, bot: iBot):
        self.bot[bot.name] = bot
        self.round_robin.append(bot)
        loop = asyncio.get_running_loop()
        bot.fiber = loop.create_task(bot.run())

    async def remove_bot(self, bot: iBot):
        assert bot.name in self.bot

        # request bot to finish
        # bot.input_queue.put_nowait(None)

        # remove bot for more assignations
        self.round_robin.remove(bot)
        self.bot.pop(bot.name)

    def remain_tasks(self):
        "compute how many pending tasks still remains"
        n = sum([sync.running() for sync in self.syncmodel])
        if self.raw_storage:
            n += self.raw_storage.running()
        n += super().remain_tasks()
        # x = 1
        # n += x
        return n

    def _clean(self, kind, data):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        return data

    # Transformer

    def convert_into_references(self, data):
        """Search for nested objects in `value` and convert them into references"""
        if self.REFERENCE_MATCHES:
            id_keys = list(
                walk(
                    data,
                    keys_included=self.REFERENCE_MATCHES,
                    include_struct=False,
                )
            )
            for idkey, idval in id_keys:
                # myassign(value, myget(value, idkey), idkey[:-1])
                myassign(data, idval, idkey[:-1])

        return data

    def new(self, kind, data, **context):
        """Try to create / update an item of `type_` class from raw data

        - convert nested data into references
        - convert data to suit pydantic schema
        - get the pydantic item

        """
        if not data:
            return
        d = re.match(REG_KIND, kind).groupdict()
        real_kind = d["parent"]
        klass = self.MAPPERS.get(real_kind)
        if not klass:
            log.warning(
                "missing MAPPERS[%s] class!", kind
            )  # TODO: remove debug
            return

        data2 = self.convert_into_references(data)
        context.update(data2)
        item = klass.pydantic(context)

        if item:
            assert (
                item.id
            ), "items must provide an `id` member. Maybe you need to set an `id` attribute in Pytantic or create a SetIDPlugin plugin?"

            # check if fquid is well formed
            # TODO: check if I must force `id` existence
            _id = item.id

            # Note:
            # parse_duri("/foo/dadad:213")['xhost'] == 'test'
            # parse_duri("foo/dadad:213")['xhost'] == 'foo'

            # parse_duri("/foo/dadad:213")['path'] == '/foo/dadad:213'
            # parse_duri(/foo/dadad:213")['path'] == '/dadad:213'

            prefix = self.prefix or kind  #  or klass.PYDANTIC.__name__
            _prefix = parse_duri(prefix)
            sid = str(_id)
            _uri = parse_xuri(sid)
            if not _uri["host"]:
                _uri = {"id": sid}
            _fquid = combine_uri(
                _prefix,
                _uri,
                context,
            )
            fquid = build_uri(**_fquid)
            item.id = fquid

        return item

    def _restruct(self, kind, data, reveal):
        """Restructure internal data according to `RESTRUCT_DATA` structure info.

        Finally the result is the overlay of the original `data` and the restructured one.
        """
        restruct = {}
        info = self.RESTRUCT_DATA.get("default", {})
        info.update(self.RESTRUCT_DATA.get(kind, {}))
        for path, value in reveal.items():
            for pattern, (new_path, new_value) in info.items():
                m = re.match(pattern, path)
                if m:
                    d = m.groupdict()
                    d["value"] = value
                    key = tuple(new_path.format_map(d).split(SEP))
                    _value = (
                        value
                        if new_value == COPY
                        else new_value.format_map(d)
                    )
                    restruct[key] = _value

        # build the restructured data
        restruct = rebuild(restruct, result={})
        # create the overlay of both data to be used (possibly) by pydantic
        data = {**data, **restruct}

        return data

    def _transform(self, kind, data):
        return data
