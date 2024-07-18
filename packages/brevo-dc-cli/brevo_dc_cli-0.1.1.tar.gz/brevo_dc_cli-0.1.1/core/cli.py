import click
from core import cli_datacontract_cmd
from core.common import log


@click.group(name="cli")
def cli() -> None:
    """Data CLI for data deployments"""


@cli.command()
@click.option("-m", "--module", "module", required=True, help="Module Name")
@click.option(
    "-s",
    "--service",
    "service",
    required=False,
    help="Service name",
)
@click.option(
    "-v", "--verbose", "verbose", required=False, help="Verbose mode", type=bool
)
@click.argument(
    "args",
    nargs=-1,
    required=False,
    type=str,
)
@click.pass_context
def datacontract(
    ctx, module: str, service: str, verbose: bool = False, args: str = None
):
    module_name = f"datacontract_{module}"
    log.header(f"Datacontract : {module}")

    cli_handler = getattr(cli_datacontract_cmd, module_name)
    cli_handler(module, service, verbose, args)
