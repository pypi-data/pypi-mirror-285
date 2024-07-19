import random
from typing import Dict, List

from agptools.helpers import build_uri, parse_xuri


from .definitions import (
    UID,
    WAVE,
    JSON,
    MONOTONIC_KEY,
    URI,
    ORDER_KEY,
    DIRECTION_KEY,
    PREFIX_URL,
)
from .crud import iStorage, parse_duri, tf

# TODO: check https://pypi.org/project/speedict/
# TODO: check https://github.com/speedb-io/python-speedb
# TODO: check https://github.com/grantjenks/python-diskcache/tree/master
# TODO: check https://github.com/unum-cloud/ustore

TUBE_NS = "system"
TUBE_DB = "swarmtube"
TUBE_META = "TubeMeta"
TUBE_WAVE = "TubeWave"
TUBE_SYNC = "TubeSync"
TUBE_SNAPSHOT = "TubeSnap"


def get_tube_name(klass):
    if isinstance(klass, str):
        tube_name = klass.split(":")[-1]
    else:
        tube_name = f"{klass.__module__.replace('.', '_')}_{klass.__name__}"
    return tube_name


class iWaves:
    """Swarm Flows / Waves storage.
    Base implementation is for Surreal, but can be
    overridden by sub-classing
    """

    MODE_SNAPSHOT = "snap"
    MODE_TUBE = "tube"

    MAX_HARD_CACHE = 120
    MAX_SOFT_CACHE = 100

    TUBE_SYNC_WAVES = {}

    AVOID_KEYS = (
        PREFIX_URL,
        MONOTONIC_KEY,
    )

    def __init__(self, storage: iStorage, *args, **kw):
        super().__init__(*args, **kw)
        self.cache = {}
        self.storage = storage

    async def last_wave(self, task: Dict) -> WAVE:
        """Returns all objects from that belongs
        to the last wave from tge ns/db coded by prefix
        """
        prefix = task[PREFIX_URL]
        _prefix = parse_duri(prefix)
        namespace = _prefix["fscheme"]
        database = _prefix["host"]
        # use tr(target) instead letting storage use a PK
        # and adding a column with id (more space)
        # thing = tf(target)
        # query = (
        #     f'{namespace}://{database}/{TUBE_WAVE}?id={TUBE_WAVE}:{thing}'
        # )
        query = f'{namespace}://{database}/{TUBE_WAVE}'
        params = {k: v for k, v in task.items() if k not in self.AVOID_KEYS}
        params[ORDER_KEY] = MONOTONIC_KEY
        params[DIRECTION_KEY] = "DESC"
        wave = await self.storage.query(query, **params)

        waves = []
        # assert (
        #     len(wave) <= 1
        # ), f"This query: {query} must return just 0-1 results ¿sharing wave?"

        # return all objects that belongs to this *last* wave
        for w in wave:
            query = f'{namespace}://{database}/{TUBE_SNAPSHOT}'
            params = {MONOTONIC_KEY: w[MONOTONIC_KEY]}
            items = await self.storage.query(query, **params)
            waves.extend(items)

        return waves

    async def update_sync_wave(
        self, prefix: URI, sources: List[URI], target: URI, wave: WAVE
    ):
        """Update the synchronization wave
        of some sources for a particular target
        """
        _prefix = parse_duri(prefix)
        namespace = _prefix["fscheme"]
        database = _prefix["host"]

        wave = int(wave)
        record = {
            "target": target,
            MONOTONIC_KEY: wave,
        }

        results = []
        query = f'{namespace}://{database}/{TUBE_WAVE}'
        for source in sources:
            # query = f'{TUBE_NS}://{TUBE_DB}/{TUBE_SYNC}?source={source}&target={target}'
            # Note that record hasn't `id`, we need to find if the
            # record already exist or is new one

            params = {
                "source": source,
                "target": target,
            }
            _results = await self.storage.query(query, **params)
            if _results:
                record = _results[0]
                record[MONOTONIC_KEY] = wave
                result = await self.storage.update(query, record)
            else:
                record['source'] = source
                result = await self.storage.put(query, record)

            results.append(result)
        return all(results)

    async def last_waves(
        self, prefix: URI, sources: List[URI], target: URI
    ) -> Dict[URI, WAVE]:
        "return the last wave of an object"
        _prefix = parse_duri(prefix)
        namespace = _prefix["fscheme"]
        database = _prefix["host"]

        # _uri = parse_duri(target)
        # just for clarity
        # namespace = _uri["fscheme"]
        # database = _uri["host"]

        waves = {}
        query = f'{namespace}://{database}/{TUBE_SYNC}'
        for source in sources:
            # query = f'{namespace}://{database}/{TUBE_SYNC}?source={source}&target={target}'
            params = {
                "source": source,
                "target": target,
            }
            result = await self.storage.query(query, **params)
            if result:
                waves[source] = result[0][MONOTONIC_KEY]
            else:
                waves[source] = 0
        return waves

    def _has_change(self, uri: UID, **data: JSON):
        # TODO: ask to TUBE_WAVE instead (direct check by id)
        _uri = parse_duri(uri)
        if data:
            root = self.cache
            for key in _uri['_path'].split('/'):
                root = root.setdefault(key, {})
            current = root.get(uid := _uri['id'])
            if current != data:
                # check cache size
                if len(root) > self.MAX_HARD_CACHE:
                    keys = list(root.keys())
                    while (l := len(keys)) > self.MAX_SOFT_CACHE:
                        k = random.randint(0, l - 1)
                        root.pop(keys.pop(k))

                root[uid] = data
                return True
        return False

    async def start(self):
        "any action related to start storage operations"

    async def stop(self):
        "any action related to stop storage operations"

    async def update_meta(self, tube, meta, merge=True):
        """Update the tube metadata.
        If merge is True, meta-data will me merge
        If merge is False, meta-data will be replace
        """

    async def find_meta(self, tube, meta):
        """Find tubes that match the specified meta"""
        return []

    async def save(self, nice=False, wait=False):
        return await self.storage.save(nice=nice, wait=wait)
