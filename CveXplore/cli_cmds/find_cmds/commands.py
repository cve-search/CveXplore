import click

from CveXplore.cli_cmds.cli_utils.utils import printer


@click.group(
    "find",
    invoke_without_command=True,
    help="Perform find queries on a single collection",
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
    "-o",
    "--output",
    default="json",
    help="Set the desired output format (defaults to json)",
    type=click.Choice(["json", "csv", "xml", "html"], case_sensitive=False),
)
@click.pass_context
def search_cmd(ctx, collection, field, value, limit, output):
    ret_list = ctx.obj["data_source"].get_single_store_entries(
        (collection, {field: value.upper()}), limit=limit
    )
    try:
        result = [result.to_dict() for result in ret_list]
    except TypeError:
        result = []

    if ctx.invoked_subcommand is None:
        printer(input_data=result, output=output)
    else:
        ctx.obj["RESULT"] = result
