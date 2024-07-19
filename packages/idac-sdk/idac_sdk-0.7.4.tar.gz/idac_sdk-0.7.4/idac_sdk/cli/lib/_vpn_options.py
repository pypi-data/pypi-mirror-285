import asyncclick as click
from functools import wraps
from os import path

from idac_sdk.cli.lib._helpers import filter_dict
from idac_sdk import VPNConfig, VPNType

_vpn_options = [
    click.option(
        "--vpn",
        type=click.Choice([e.name for e in VPNType], case_sensitive=False),
        default=None,
        help="Enables VPN",
    ),
    # for explicit
    click.option(
        "--vpn-host", type=str, default=None, help="VPN host (for explicit/request VPN type)"
    ),
    click.option(
        "--vpn-username",
        type=str,
        default=None,
        help="VPN username (for explicit/request VPN type)",
    ),
    click.option(
        "--vpn-password",
        type=str,
        default=None,
        help="VPN password (for explicit/request VPN type)",
    ),
    # for secure repo
    click.option("--vpn-file", type=str, default=None, help="VPN file (for secure_repo VPN type)"),
    click.option(
        "--vpn-block", type=str, default=None, help="Block in VPN file (for secure_repo VPN type)"
    ),
    click.option(
        "--vpn-key", type=str, default=None, help="Key in the VPN block (for secure_repo VPN type)"
    ),
]


def with_vpn(func):
    @wraps(func)
    def wrapper(
        *args, vpn, vpn_host, vpn_username, vpn_password, vpn_file, vpn_block, vpn_key, **kwargs
    ):
        if vpn_file:
            secure_repo_space = f"{path.dirname(vpn_file)}/"
            secure_repo_file = path.basename(vpn_file)
        else:
            secure_repo_space = None
            secure_repo_file = None

        vpn_config = (
            None
            if not vpn
            else VPNConfig(
                **filter_dict(
                    {
                        "type": vpn or VPNType.none.name,
                        "params": filter_dict(
                            {
                                "host": vpn_host,
                                "username": vpn_username,
                                "password": vpn_password,
                                "secure_repo_space": secure_repo_space,
                                "secure_repo_file": secure_repo_file,
                                "secure_repo_block": vpn_block,
                                "secure_repo_key": vpn_key,
                            },
                            lambda elem: bool(elem[1]),
                        ),
                    },
                    lambda elem: bool(elem[1]),
                )
            )
        )
        return func(*args, vpn=vpn_config, **kwargs)

    return wrapper
