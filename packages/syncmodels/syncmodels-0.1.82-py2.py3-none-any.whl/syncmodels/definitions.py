import re
from enum import Enum
from typing import NewType

# from .models import (
#     BudgetTypeEnum,
#     TravelPartyCompositionEnum,
# )

DEFAULT_LANGUAGE = "es"

MODEL_TABLE = "model"

UID_TYPE = str

# TODO: reallocate
UID = NewType("UID", str)
QUERY = NewType("QUERY", dict)

URI = NewType("URI", str)
DURI = NewType("DURI", dict)

WAVE = NewType("WAVE", int)
JSON = NewType("JSON", dict)
QUERY = NewType("QUERY", dict)


# ----------------------------------------------------------
# common keys
# ----------------------------------------------------------
# crawler factory keys
APP_URL = "app_url"

# bootstrap keys
KIND_KEY = "kind__"
METHOD_KEY = "method__"
PREFIX_URL = "prefix__"


# other call_kw | data keys

GRACE_PERIOD_KEY = "grace__"
ORDER_KEY = "order__"
LIMIT_KEY = "limit__"
LIMIT_KEY_VALUE = "limit_value__"
DIRECTION_KEY = "direction__"
WHERE_KEY = "where__"
TABLE_KEY = "table__"
BODY_KEY = "body"
PATH_KEY = "path__"

# reserved and private keys
FUNC_KEY = "func__"
CALLABLE_KEY = "call__"
FILTERS_KEY = "filters__"

CRAWLER_KEY = "crawler__"
BOT_KEY = "bot__"

MONOTONIC_KEY = "wave__"
MONOTONIC_SINCE = "since__"
MONOTONIC_SINCE_KEY = "since_key__"
MONOTONIC_SINCE_VALUE = "since_value__"
MONOTONIC_SINCE_OPERATOR = "since_operator__"
ID_KEY = "id"
ORG_KEY = "id__"
ORG_URL = "url__"
FORCE_SAVE = "__save"
REG_PRIVATE_KEY = r".*__$"


# ----------------------------------------------------------
# fqid helpers
# ----------------------------------------------------------

# split table:uid from fqid
# TODO: get until ":"
REG_FQID = r"((?P<table>\w+):)?(?P<uid>\w+)$"

REG_SPLIT_ID = re.compile(
    """(?imsx)
    ^
    (?P<thing>[^:]+)(:(?P<id>[^:]+))?$
    """
)
REG_SPLIT_PATH2 = re.compile(
    """(?imsx)
    ^
    (?P<head>.*?)(:(?P<id>[^:]+))$
    """
)
REG_SPLIT_PATH = re.compile(
    """(?imsx)
^
(?P<xpath>
 (?P<path>
  (?P<_path>
    (?P<basename>
      (?P<table>[^/:]+)
      [/:]
      (?P<id>[^/:?#]*)
    )
  )
 )
)
(
  \?
  (?P<query>[^#]*)
)?
  (\#(?P<fragment>.*))?
$
"""
)


def build_fqid(fqid, table=""):
    m = re.match(REG_FQID, str(fqid))
    if m:
        d = m.groupdict(default=table)
        return "{table}:{uid}".format_map(d)
    # return table, fqid
    return fqid


def filter_4_compare(data, table=""):
    """Filter data to be used for comparison"""
    if data:
        result = {
            key: value
            for key, value in data.items()
            if not re.match(REG_PRIVATE_KEY, key)
        }
        # check id:
        uid = result.get("id")
        if uid is not None:
            result["id"] = build_fqid(str(uid))
    else:
        result = {}

    return result
