import asyncclick as click

import idac_sdk.cli.commands.status as status_set
import idac_sdk.cli.commands.restart as restart_set
import idac_sdk.cli.commands.cleanup as cleanup_set
import idac_sdk.cli.commands.create as create_set
import idac_sdk.cli.commands.extend as extend_set
import idac_sdk.cli.commands.config as config_set
from idac_sdk._version import __version__ as sdk_version


@click.group()
async def cli():
    """Group for CLI commands"""
    pass


@cli.command(short_help="show version")
async def version():
    click.echo(f"iDAC SDK v{sdk_version}")


def main():
    m = click.CommandCollection(
        sources=[
            cli,
            create_set.commands,
            cleanup_set.commands,
            status_set.commands,
            restart_set.commands,
            extend_set.commands,
            config_set.commands,
        ]
    )
    m(_anyio_backend="asyncio")


if __name__ == "__main__":
    main()
