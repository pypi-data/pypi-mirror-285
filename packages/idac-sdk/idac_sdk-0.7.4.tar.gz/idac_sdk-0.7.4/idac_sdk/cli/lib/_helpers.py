import json
import platform
from typing import List
import asyncclick as click
import logging
from httpx import URL

from idac_sdk.log import logger
from idac_sdk import SessionData
from idac_sdk.models.request_state import RequestState

_debug_options = [
    click.option("--debug", default=False, is_flag=True, help="Enable debug", hidden=True)
]


def set_logger_level(debug: bool) -> None:
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug level enabled")
    else:
        logger.setLevel(logging.WARN)


def add_options(options):

    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def filter_dict(dictObj, callback):
    newDict = dict()
    # Iterate over all the items in dictionary
    for (key, value) in dictObj.items():
        # Check if item satisfies the given condition then add to new dict
        if callback((key, value)):
            newDict[key] = value
    return newDict


def parse_data(ctx, param, raw: List[str]):
    parsed = dict()
    if raw is not None and len(raw) > 0:
        for v in raw:
            if "=" not in v:
                raise click.BadParameter(message="Data should have format `KEY=VALUE`",
                                         ctx=ctx,
                                         param=param)
            key, value = v.split("=")
            parsed[key] = value if value else ""
        return parsed

    return None


def parse_json(ctx, param, raw: str):
    if raw is not None:
        return json.loads(raw)


DEFAULT_OUTPUT_UNIX = r"/dcloud/idac_sdk.out"
DEFAULT_OUTPUT_WIN = r"c:\dcloud\idac_sdk.out"


def default_output(ctx, param, raw: str):
    if raw:
        return raw

    if platform.system().lower() == "windows":
        return DEFAULT_OUTPUT_WIN
    else:
        return DEFAULT_OUTPUT_UNIX


def update_url_with_creds(url: str, data: SessionData) -> str:
    u = URL(url)
    qp = u.params
    qp = qp.set("dcloudCreds", data.get("creds"))
    if data.has("datacenter"):
        qp = qp.set("datacenter", data.get("datacenter"))
    u = u.copy_merge_params(qp)
    return f"{u}"


URL_ATTRS = ["loaderUrl", "outputUrl", "mLoaderUrl", "errorUrl"]


def append_creds(state: RequestState, data: SessionData) -> RequestState:
    d = state.dict(exclude_unset=True)
    for attr in URL_ATTRS:
        if attr in d and d[attr]:
            d[attr] = update_url_with_creds(d[attr], data)

    return RequestState(**d)