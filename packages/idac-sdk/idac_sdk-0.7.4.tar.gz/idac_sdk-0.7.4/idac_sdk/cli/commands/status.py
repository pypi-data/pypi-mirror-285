import asyncclick as click
from jsonpath_ng import parse

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


@commands.command(short_help="get state of a request")
@add_options(_controller_options)
@add_options(_debug_options)
@click.option(
    "--out-path",
    multiple=True,
    help="Extract value from response by JSON path, Multiple allowed",
    type=str,
    default=None,
)
@click.argument("request_id")
@with_controller
async def state(controller, request_id, out_path, **kwargs):
    """Get JSON state object of a request

    REQUEST_ID - id/uuid of the request"""
    set_logger_level(kwargs.get("debug", False))

    req = IDACRequestAsync(uuid=request_id, controller=controller)
    state = await req.get_state()
    if out_path:
        state_dict = state.dict()
        for o in out_path:
            jsonpath_expr = parse(o)
            for match in jsonpath_expr.find(state_dict):
                click.echo(match.value)
    else:
        click.echo(state.json())


@commands.command(short_help="get status of a request")
@add_options(_controller_options)
@add_options(_debug_options)
@click.argument("request_id")
@with_controller
async def status(controller, request_id, **kwargs):
    """Get current status of a request

    REQUEST_ID - id/uuid of the request"""
    set_logger_level(kwargs.get("debug", False))

    req = IDACRequestAsync(uuid=request_id, controller=controller)
    state = await req.get_state()
    click.echo(state.status)
