import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.cli_cmds.mutex_options.mutex import Mutex


@click.group("capec", invoke_without_command=True, help="Query for capec specific data")
@click.pass_context
def capec_cmd(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(capec_cmd.get_help(ctx))


@capec_cmd.group(
    "search",
    invoke_without_command=True,
    help="Search for capec entries by id",
)
@click.option(
    "-c",
    "--capec",
    help="Search for CAPEC's (could be multiple)",
    multiple=True,
    cls=Mutex,
    not_required_if=["field_list"],
)
@click.option(
    "-f",
    "--field",
    help="Field to return (could be multiple)",
    multiple=True,
    cls=Mutex,
    not_required_if=["field_list"],
)
@click.option(
    "-fl",
    "--field_list",
    help="Return a field list for this collection",
    multiple=True,
    is_flag=True,
    cls=Mutex,
    not_required_if=["field", "capec"],
)
@click.option(
    "-o",
    "--output",
    default="json",
    help="Set the desired output format (defaults to json)",
    type=click.Choice(["json", "csv", "xml", "html"], case_sensitive=False),
)
@click.pass_context
def search_cmd(
    ctx,
    capec,
    field,
    field_list,
    output,
):
    if capec:
        ret_list = getattr(ctx.obj["data_source"], "capec").mget_by_id(*capec)
    elif field_list:
        ret_list = getattr(ctx.obj["data_source"], "capec").field_list()
    else:
        click.echo(search_cmd.get_help(ctx))
        return

    if isinstance(ret_list, list):
        result = [result.to_dict(*field) for result in ret_list]
    elif isinstance(ret_list, set):
        result = sorted([result for result in ret_list])
    else:
        result = []

    if ctx.invoked_subcommand is None:
        printer(input_data=result, output=output)
    else:
        ctx.obj["RESULT"] = result
