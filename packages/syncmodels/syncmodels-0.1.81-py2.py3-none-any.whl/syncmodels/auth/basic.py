# ---------------------------------------------------------
# Authenticator Helpers
# ---------------------------------------------------------
from agptools.logs import logger
from agptools.containers import expand_expression
import base64

import requests
from . import iAuthenticator

from ..http import (
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
    BASIC_HEADERS,
)

log = logger(__name__)


def score(item):
    "score by counting how many uri values are not None"
    info, m = item
    sc = len(m.groups())
    return sc, info


class BasicAuthenticator(iAuthenticator):
    """"""

    @classmethod
    async def _auth(cls, url, params, session: "iSession"):
        "resolve authentication (i.e 401/404/407 alike situations)"
        session.headers.update(params)
        return True


class EndPointAuthenticator(iAuthenticator):
    """"""

    @classmethod
    async def _auth(cls, url, params, session: "iSession"):
        "resolve authentication (i.e 401/404/407 alike situations)"

        auth_url = params.get(AUTH_URL, url)
        # depending of the auth EP method ...

        if (meth := params.get(AUTH_METHOD)) in (METHOD_BASIC, None):
            # get basic credentials
            concatenated = params[AUTH_USER] + ":" + params[AUTH_SECRET]
            encoded = base64.b64encode(concatenated.encode("utf-8"))
            headers = {
                **BASIC_HEADERS,
                # CONTENT_LENGTH: '0',
                # 'Authorization': 'Basic MkpNaWZnS0RrbTliRXB2ZjV4RWRPOFJMWlZvYTpISzU2MWZrd1U1NEIxNDhuMnFTdnJHREFYMEFh',
                AUTHORIZATION: f"Basic {encoded.decode('utf-8')}",
            }

            response = requests.post(auth_url, headers=headers, verify=True)
        elif meth in (METHOD_JSON,):
            headers = {
                **BASIC_HEADERS,
                # CONTENT_TYPE: APPLICATION_JSON,
                # CONTENT_LENGTH: '0',
                # 'Authorization': 'Basic MkpNaWZnS0RrbTliRXB2ZjV4RWRPOFJMWlZvYTpISzU2MWZrd1U1NEIxNDhuMnFTdnJHREFYMEFh',
                # AUTHORIZATION: f"Basic {encoded.decode('utf-8')}",
            }
            #  TODO: use asyncio (faster)
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         auth_url, headers=headers, data=params[AUTH_PAYLOAD]
            #     ) as response:
            #         response_text = await response.text()
            #         print(f"Status: {response.status}")
            #         print(f"Response: {response_text}")

            response = requests.post(
                auth_url,
                headers=headers,
                data=params[AUTH_PAYLOAD],
                verify=True,
            )
        else:
            raise RuntimeError(f"Unknown method: {meth}")

        if response.status_code in (200,):
            result = response.json()
            # expires_in = result.get("expires_in")  # secs

            key = params.get(AUTH_KEY)
            if key:
                template = params[AUTH_VALUE]
                #  i.e. "Bearer {access_token}"
                # allow expressions such:
                # "Bearer {access_token}" or
                # "Bearer {data.access_token}"
                rendered = expand_expression(result, template)
                session.headers[key] = rendered
                # session.headers[key] = template.format_map(
                #     result
                # )
            else:
                session.headers.update(result)
            return result
        else:
            log.error(
                "%s: %s: %s",
                response.status,
            )
            result = await response.text()
            log.error(result)
            log.error("Status: %s", response.status)

        session.headers.update(params)
