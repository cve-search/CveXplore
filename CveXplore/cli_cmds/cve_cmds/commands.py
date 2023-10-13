from pprint import pformat

import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.cli_cmds.mutex_options.mutex import Mutex


@click.group("cve", invoke_without_command=True, help="Query for cve specific data")
@click.pass_context
def cve_cmd(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(cve_cmd.get_help(ctx))


@cve_cmd.group(
    "search",
    invoke_without_command=True,
    help="Search for cve entries by id",
)
@click.option(
    "-c",
    "--cve",
    help="Add related CVE's (could be multiple)",
    multiple=True,
)
@click.option(
    "-f",
    "--field",
    help="Field to return (could be multiple)",
    multiple=True,
)
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty print the output",
    cls=Mutex,
    not_required_if=["output"],
)
@click.option(
    "-o",
    "--output",
    default="json",
    help="Set the desired output format (defaults to json)",
    type=click.Choice(["json", "csv", "xml", "html"], case_sensitive=False),
    cls=Mutex,
    not_required_if=["pretty"],
)
@click.pass_context
def search_cmd(
    ctx,
    cve,
    field,
    pretty,
    output,
):

    if cve:
        ret_list = ctx.obj["data_source"].cves_by_id(*cve)
    else:
        click.echo(search_cmd.get_help(ctx))
        return

    if isinstance(ret_list, list):
        result = [result.to_dict(*field) for result in ret_list]
    else:
        result = []

    if ctx.invoked_subcommand is None:
        printer(input_data=result, pretty=pretty, output=output)
    else:
        if pretty:
            ctx.obj["RESULT"] = pformat(result, indent=4)
        else:
            ctx.obj["RESULT"] = result


@cve_cmd.group(
    "last",
    invoke_without_command=True,
    help="Query the last L (-l) amount of cve entries",
)
@click.option("-l", "--limit", default=10, help="Query limit")
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty print the output",
    cls=Mutex,
    not_required_if=["output"],
)
@click.option(
    "-o",
    "--output",
    default="json",
    help="Set the desired output format (defaults to json)",
    type=click.Choice(["json", "csv", "xml", "html"], case_sensitive=False),
    cls=Mutex,
    not_required_if=["pretty"],
)
@click.pass_context
def last_cmd(ctx, limit, pretty, output):
    ret_list = ctx.obj["data_source"].last_cves(limit=limit)

    result = [result.to_dict() for result in ret_list]

    if ctx.invoked_subcommand is None:
        printer(input_data=result, pretty=pretty, output=output)
    else:
        if pretty:
            ctx.obj["RESULT"] = pformat(result, indent=4)
        else:
            ctx.obj["RESULT"] = result
