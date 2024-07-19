import asyncclick as click

from idac_sdk import IDACRequestAsync
from idac_sdk.cli.lib._controller_options import _controller_options, with_controller
from idac_sdk.cli.lib._helpers import (
    add_options,
    _debug_options,
    set_logger_level,
)


@click.group()
def commands():
    pass


@commands.command(short_help="extend a request")
@add_options(_controller_options)
@add_options(_debug_options)
@click.option("-m", "--minutes", type=click.INT, help="Amount of minutes", required=True)
@click.argument("request_id")
@with_controller
async def extend(controller, request_id, minutes, **kwargs):
    """Extend request

    \b
    REQUEST_ID - id/uuid of the request"""
    set_logger_level(kwargs.get("debug", False))

    req = IDACRequestAsync(uuid=request_id, controller=controller)
    await req.extend(minutes)
    click.echo("Extended")
