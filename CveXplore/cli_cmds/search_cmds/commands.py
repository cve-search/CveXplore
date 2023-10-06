from pprint import pformat

import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.cli_cmds.mutex_options.mutex import Mutex


@click.group(
    "search",
    invoke_without_command=True,
    help="Perform search queries on a single collection",
)
@click.option(
    "-c",
    "--collection",
    required=True,
    type=click.Choice(["capec", "cpe", "cwe", "via4", "cves"], case_sensitive=False),
    help="Collection to query",
)
@click.option("-f", "--field", required=True, help="Field to query")
@click.option("-v", "--value", required=True, help="Value to query")
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
def search_cmd(ctx, collection, field, value, limit, pretty, output):
    ret_list = ctx.obj["data_source"].get_single_store_entries(
        (collection, {field: value.upper()}), limit=limit
    )

    result = [result.to_dict() for result in ret_list]

    if ctx.invoked_subcommand is None:
        printer(input_data=result, pretty=pretty, output=output)
    else:
        if pretty:
            ctx.obj["RESULT"] = pformat(result, indent=4)
        else:
            ctx.obj["RESULT"] = result


@search_cmd.command("less", help="Lets you scroll through the returned results")
@click.pass_context
def less_cmd(ctx):
    click.echo_via_pager(ctx.obj["RESULT"])
