import asyncclick as click
from functools import wraps

from idac_sdk.cli.lib._helpers import filter_dict
from idac_sdk import IDACAuthType, IDACControllerAsync

_controller_options = [
    click.option("-U", "--controller-url", default=None, type=str, help="URL of iDAC controller"),
    click.option(
        "-P",
        "--controller-proto",
        type=click.Choice(["http", "https"], case_sensitive=False),
        default="https",
        help="Which protocol should be used to connect to controller",
    ),
    click.option(
        "-T",
        "--auth-type",
        type=click.Choice([e.name for e in IDACAuthType], case_sensitive=False),
        help="Type of authentication",
    ),
    click.option(
        "-A",
        "--auth",
        type=str,
        help=(
            "Token if Auth Type is BEARER or WORKER, base64 string if BASIC. Ignored for other auth"
            " types"
        ),
    ),
    click.option(
        "--worker-id",
        type=str,
        help="Worker id for the Worker auth type",
    ),
    click.option(
        "--worker-secret",
        type=str,
        help="Worker secret for the Worker auth type",
    ),
    click.option("-V", "--api-version", default=None, help="API version to use"),
]


def with_controller(func):
    @wraps(func)
    def wrapper(
        *args,
        controller_url,
        controller_proto,
        auth_type,
        auth,
        worker_id,
        worker_secret,
        api_version,
        **kwargs
    ):
        controller = IDACControllerAsync(
            **filter_dict(
                {
                    "proto": controller_proto,
                    "url": controller_url,
                    "auth_type": IDACAuthType[auth_type] if auth_type else None,
                    "auth": auth,
                    "worker_id": worker_id,
                    "worker_secret": worker_secret,
                    "api_version": api_version,
                },
                lambda elem: bool(elem[1]),
            )
        )
        return func(*args, controller=controller, **kwargs)

    return wrapper
