"""
Mappers transform plain dict to another dict
converting key and values.

Classes definition are inspired on pydantic

"""

import re
import sys
import traceback
import inspect
import itertools
from typing import Dict, Union, _GenericAlias

from math import isnan
from datetime import timedelta
from dateutil.parser import parse

from pydantic import ValidationError

# ------------------------------------------------
# Converter functions
# ------------------------------------------------
from agptools.helpers import (
    BOOL,
    DATE,
    DURATION,
    FLOAT,
    I,
    INT,
    STRIP,
    TEXT,
)

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger


# ------------------------------------------------
# model support
# ------------------------------------------------
from ..model.model import *


log = logger(__name__)

# =========================================================
# Mappers Support
# =========================================================


def BASIC_ID(x):
    if isinstance(x, str):
        return x.split(":")[-1]
    return x


def VALID(x):
    try:
        if isnan(x):
            return False
    except Exception:
        pass
    return True


ANNOTATION_FACTORY = {
    "List": list,
    "Dict": dict,
}


class Mapper:
    PYDANTIC = None

    @classmethod
    def _populate(cls):
        cls.MAPPING = {}
        for key in dir(cls):
            value = getattr(cls, key)
            if isinstance(value, tuple):
                l = len(value)
                if l == 2:
                    # is an attribute
                    cls.MAPPING[key] = *value, None
                elif l == 3:
                    cls.MAPPING[key] = value

        return cls.MAPPING

    @classmethod
    def transform_hide(cls, org: Dict, only_defined=False):
        """Not used
        # TODO: Delete
        """
        assert isinstance(org, dict)
        result = {} if only_defined else dict(org)
        MAP = getattr(cls, "MAPPING", None) or cls._populate()
        try:
            for k in set(org).intersection(MAP):
                v = org[k]
                t_name, t_value, t_default = MAP[k]
                if isinstance(t_name, str):
                    m = re.match(t_name, k)
                    if m:
                        name = m.group(0)
                    else:
                        name = t_name
                else:
                    name = t_name(k)
                value = t_value(v)
                result[name] = value
        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error(f"key: {k} : value: {value}")

        return result

    @classmethod
    def transform(cls, org: Dict, only_defined=False):
        assert isinstance(org, dict)
        result = {} if only_defined else dict(org)
        MAP = getattr(cls, "MAPPING", None) or cls._populate()

        def parse(value, t_value, t_default):
            if VALID(value):
                if inspect.isfunction(t_value):
                    value = t_value(value)
                # is a typing anotation?
                elif isinstance(t_value, _GenericAlias):
                    if t_value._name in ANNOTATION_FACTORY:
                        # example
                        # data = (r"Data", List[StatisticData], )
                        new_value = {
                            klass: [
                                parse(v, klass, t_default) for v in value
                            ]
                            for klass in t_value.__args__
                        }
                        # create the value from Generic specification
                        factory = ANNOTATION_FACTORY[t_value._name]
                        value = factory(
                            itertools.zip_longest(
                                new_value.values(),
                                fillvalue=None,
                            )
                        )
                        value = value[0][0]  # TODO: review
                    else:
                        raise f"don't know how to deal with `{t_value}` typing yet!"
                elif inspect.isclass(t_value) and issubclass(
                    t_value, Mapper
                ):
                    # is another mapper?
                    value = t_value.pydantic(value)
                else:
                    value = t_value(value)
            else:
                value = t_default
            return value

        try:
            for key, (t_name, t_value, t_default) in MAP.items():
                name = None
                if isinstance(t_name, str):
                    for k, v in org.items():
                        m = re.match(t_name, k)
                        if m:
                            name = m.group(0)
                            break
                else:
                    name = t_name(key)

                if name:  # and name in org:
                    value = org.get(name, t_default)
                    value = parse(value, t_value, t_default)
                    result[key] = value
        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error(f"key: {k} : value: {value}")

        return result

    @classmethod
    def pydantic(cls, org, **extra):
        """Create a pydantic object as well"""
        klass = getattr(cls, "PYDANTIC", None)
        if klass:
            if klass != IgnoreMapper:
                org.update(extra)
                norm = cls.transform(org)
                try:
                    item = klass(**norm)
                except ValidationError as why:
                    log.warning(
                        "FAILED Pydatic Validation: klass: [%s] : [%s]",
                        klass,
                        norm,
                    )
                    log.warning(f"{why}")
                    item = None
                return item
            # ignore due data
            # return None
        else:
            log.warning("[%s] has not defined a PYDANTIC class", cls)


class IgnoreMapper(Mapper):
    """A specific mapper to indicate we don't want to
    create any pydantic class explicity
    (it not forgotten or a mistake)
    """
