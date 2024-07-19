import asyncclick as click
import json
from jsonpath_ng import parse

from idac_sdk import (
    IDACRequestAsync,
    IDACRequestType,
    SessionData,
)
from idac_sdk.log import logger
from idac_sdk.cli.lib._controller_options import _controller_options, with_controller
from idac_sdk.cli.lib._vpn_options import _vpn_options, with_vpn
from idac_sdk.cli.lib._helpers import (
    add_options,
    filter_dict,
    parse_data,
    parse_json,
    default_output,
    _debug_options,
    set_logger_level,
    append_creds,
)


@click.group()
def commands():
    pass


@commands.command(short_help="execute a recipe")
@add_options(_controller_options)
@add_options(_debug_options)
@click.option(
    "--no-session-xml",
    is_flag=True,
    default=False,
    help="Won't try load session.xml file",
)
@click.option(
    "-s",
    "--session-xml-path",
    default=None,
    type=str,
    help="Path to session.xml file (if non-default should be used)",
)
@click.option(
    "-p",
    "--param",
    help="Additional param to be sent, multiple allowed. Format: KEY=VALUE",
    multiple=True,
    callback=parse_data,
)
@click.option(
    "--skip",
    help="Skip parameter from session.xml, multiple allowed. Format: KEY",
    multiple=True,
)
@click.option(
    "-j",
    "--json",
    help="JSON object to be sent",
    callback=parse_json,
)
@click.option(
    "-t",
    "--type",
    type=click.Choice([e.name for e in IDACRequestType], case_sensitive=False),
    help="Type of the request",
)
@click.option("-o", "--owner", help="Owner", type=str, default=None)
@click.option("-n", "--name", help="Request name (demo name)", type=str, default=None)
@click.option("-d", "--datacenter", help="Datacenter", type=str, default=None)
@click.option(
    "--out-path",
    multiple=True,
    help="Extract value from response by JSON path, Multiple allowed",
    type=str,
    default=None,
)
@click.option(
    "-O",
    "--output",
    help="Would write result to a file.",
    is_flag=True,
    default=False,
)
@click.option(
    "--output-file",
    help=
    r"Sets output file. Default ('C:\dcloud\idac_sdk.out' or '/dcloud/idac_sdk.out') would be used if omitted.",
    type=str,
    default=None,
    callback=default_output)
@click.option(
    "--creds/--no-creds",
    default=True,
    help="Should add dCloud creds to received URL or not. Default: TRUE",
)
@click.option("-k", "--kitchen", help="iDAC Kitchen sandbox location", type=str, default=None)
@add_options(_vpn_options)
@click.argument("recipe_path")
@click.argument("recipe_name")
@with_controller
@with_vpn
async def create(controller, recipe_path, recipe_name, out_path, vpn, creds, **kwargs):
    """Create new automation request (execute a recipe on iDAC)

    \b
    RECIPE_PATH - path to the recipe
    RECIPE_NAME - name of the recipe
    """
    set_logger_level(kwargs.get("debug", False))

    # remove empty params
    filtered = filter_dict(kwargs, lambda el: el[1] is not None)

    # create dict with initial data
    initial = None
    if "json" in filtered or "param" in filtered:
        initial = dict()
        initial.update(filtered.get("param", {}))
        initial.update(filtered.get("json", {}))

    sd_kwargs = {
        "session_xml_path":
            filtered.get("session_xml_path", None) if not filtered["no_session_xml"] else False,
        "recipePath":
            recipe_path,
        "recipeName":
            recipe_name,
    }

    if initial:
        sd_kwargs["initial_data"] = initial

    # create SessionData
    sd = SessionData(**sd_kwargs)

    if "skip" in filtered and (isinstance(filtered["skip"],
                                          (list, tuple)) or isinstance(filtered["skip"], str)):
        skip = filtered["skip"] if isinstance(filtered["skip"],
                                              (list, tuple)) else [filtered["skip"]]
        logger.debug(f"Skipping fields: {skip}")
        for sk in skip:
            if sd.has(sk):
                sd.delete(sk)

    if "owner" in filtered:
        sd.set("owner", filtered["owner"])

    if "name" in filtered:
        sd.set("demo", filtered["name"])

    if "datacenter" in filtered:
        sd.set("datacenter", filtered["datacenter"])

    if "kitchen" in filtered:
        # user would like to execute recipe in a Kitchen sandbox
        sd.set("location", filtered["kitchen"])
        sd.set("recipeMode", "worker")

    req = IDACRequestAsync(session_data=sd, controller=controller, vpn=vpn)
    state, redirect = await req.create(request_type=IDACRequestType[filtered.get("type", "SIMPLE")])

    if creds and sd.has("creds"):
        state = append_creds(state=state, data=sd)

    state_dict = state.dict()
    if redirect:
        state_dict["original_redirect"] = redirect

    file = "-"
    if filtered.get("output", False):
        file = filtered["output_file"]

    with click.open_file(file, "w") as f:
        if out_path:
            for o in out_path:
                jsonpath_expr = parse(o)
                for match in jsonpath_expr.find(state_dict):
                    f.write(f"{match.value}\n")
        else:
            f.write(json.dumps(state_dict))
