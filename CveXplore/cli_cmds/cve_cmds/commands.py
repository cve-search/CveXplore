from pprint import pformat

import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.cli_cmds.mutex_options.mutex import Mutex


@click.group("cve", invoke_without_command=True, help="Query for cve specific data")
@click.pass_context
def cve_cmd(ctx):
    pass


@cve_cmd.group(
    "last", invoke_without_command=True, help="Query the last N amount of cve entries"
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
    help="Set the desired output format",
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


@last_cmd.command("less", help="Lets you scroll through the returned results")
@click.pass_context
def less_cmd(ctx):
    click.echo_via_pager(ctx.obj["RESULT"])
