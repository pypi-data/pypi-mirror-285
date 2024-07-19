from base64 import b64encode
from email.policy import default
import yaml
import asyncclick as click
import idac_sdk
import idac_sdk.config
from idac_sdk.cli.lib._controller_options import _controller_options
from idac_sdk.cli.lib._vpn_options import _vpn_options
from idac_sdk.cli.lib._helpers import add_options
from idac_sdk.models.vpn_config import VPNType


@click.group()
def commands():
    pass


@commands.command(short_help="configure iDAC SDK")
@add_options(_controller_options)
@click.option(
    "--vpn",
    type=click.Choice([VPNType.none.name, VPNType.vpod.name], case_sensitive=False),
    default=None,
    help="Sets default VPN type",
)
async def config(
    controller_url,
    controller_proto,
    auth_type,
    auth,
    worker_id,
    worker_secret,
    api_version,
    vpn,
):
    current_config = idac_sdk.config.load_config(raise_error=False)
    if not controller_url:
        controller_url = click.prompt(
            "Enter default iDAC URL",
            type=str,
            default=current_config.defaults.idac_fqdn,
        )

    if not controller_proto:
        controller_proto = click.prompt(
            "Enter default iDAC controller proto",
            type=click.Choice(["http", "https"], case_sensitive=False),
            show_choices=True,
            default=current_config.defaults.idac_proto,
        )

    if not api_version:
        api_version = click.prompt(
            "Enter default iDAC controller API version",
            type=str,
            default=current_config.defaults.api_version,
        )

    if not auth_type:
        auth_type = click.prompt(
            "Enter default iDAC auth type",
            type=click.Choice([e.name for e in idac_sdk.IDACAuthType], case_sensitive=False),
            show_choices=True,
            default=current_config.defaults.auth.type,
        )
    if auth and auth_type not in [
        idac_sdk.IDACAuthType.DCLOUD_SESSION.name,
        idac_sdk.IDACAuthType.NONE.name,
    ]:
        params = {"token": auth}
    elif auth_type == idac_sdk.IDACAuthType.BASIC.name:
        username = click.prompt(
            "Enter username for BASIC auth",
            type=str,
            hide_input=False,
            default="",
            value_proc=lambda val: val if val else "",
        )
        password = click.prompt(
            "Enter password for BASIC auth",
            type=str,
            hide_input=True,
            default="",
            value_proc=lambda val: val if val else "",
        )
        params = {"token": b64encode(bytes(f"{username}:{password}", "utf-8")).decode("utf-8")}
    elif auth_type == idac_sdk.IDACAuthType.BEARER.name:
        if not auth:
            auth = click.prompt(
                "Enter default API token for BEARER auth",
                type=str,
                hide_input=True,
                default="",
                value_proc=lambda val: val if val else "",
            )
        params = {"token": auth}
    elif auth_type == idac_sdk.IDACAuthType.WORKER.name:
        params = {}
        if not worker_id:
            worker_id = click.prompt(
                "Enter client id for WORKER auth",
                type=str,
                hide_input=False,
                default="",
                value_proc=lambda val: val if val else "",
            )
        params["client_id"] = worker_id
        if not worker_secret:
            worker_secret = click.prompt(
                "Enter secret for WORKER auth",
                type=str,
                hide_input=True,
                default="",
                value_proc=lambda val: val if val else "",
            )
        params["secret"] = worker_secret
    else:
        params = {}
    auth = {"type": auth_type, "params": params}

    # VPN settings
    if not vpn:
        vpn = click.prompt(
            "Default VPN type (Only 'none' and 'vpod' can be stored in config)",
            type=click.Choice([VPNType.none.name, VPNType.vpod.name], case_sensitive=False),
            default=current_config.defaults.vpn.type.name,
        )
    vpn_config = {"type": vpn, "params": {}}

    with open(idac_sdk.config.IDAC_CONFIG_FILE, "w") as file:
        file.write(
            yaml.dump(
                {
                    "version": idac_sdk.config.IDAC_CONFIG_VERSION,
                    "defaults": {
                        "idac_fqdn": controller_url,
                        "idac_proto": controller_proto,
                        "auth": auth,
                        "api_version": api_version,
                        "vpn": vpn_config,
                    },
                }
            )
        )

    click.echo("Done")
