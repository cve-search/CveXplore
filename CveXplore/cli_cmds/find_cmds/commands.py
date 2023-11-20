import click
import pymongo

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.cli_cmds.mutex_options.mutex import Mutex


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
@click.option(
    "-m",
    "--match",
    is_flag=True,
    help="Use match for searching (default)",
    cls=Mutex,
    not_required_if=["regex"],
)
@click.option(
    "-r",
    "--regex",
    is_flag=True,
    help="Use regex for searching",
    cls=Mutex,
    not_required_if=["match"],
)
@click.option("-l", "--limit", default=10, help="Query limit")
@click.option(
    "-lf",
    "--limit-field",
    help="Limit the return the this field(s) (could be multiple)",
    multiple=True,
)
@click.option(
    "-s", "--sort", is_flag=True, help="Sort DESCENDING (for match and regex only)"
)
@click.option(
    "-o",
    "--output",
    default="json",
    help="Set the desired output format (defaults to json)",
    type=click.Choice(["json", "csv", "xml", "html"], case_sensitive=False),
)
@click.pass_context
def find_cmd(
    ctx, collection, field, value, match, regex, limit, limit_field, sort, output
):
    if not sort:
        sorting = pymongo.ASCENDING
    else:
        sorting = pymongo.DESCENDING
    try:
        if regex:
            ret_list = (
                getattr(getattr(ctx.obj["data_source"], collection), field)
                .search(value)
                .limit(limit)
                .sort(field, sorting)
            )
        elif match:
            ret_list = (
                getattr(getattr(ctx.obj["data_source"], collection), field)
                .find(value)
                .limit(limit)
                .sort(field, sorting)
            )
        else:
            ret_list = ctx.obj["data_source"].get_single_store_entries(
                (collection, {field: value}), limit=limit
            )
    except AttributeError:
        click.echo(
            f"Field: {field} is not mapped for the collection: {collection}; you can choose "
            f"from: {getattr(ctx.obj['data_source'], collection).mapped_fields(collection=collection)}"
        )
        return

    print(len(limit_field))

    try:
        if len(limit_field) != 0:
            result = [result.to_dict(*limit_field, field) for result in ret_list]
        else:
            result = [result.to_dict() for result in ret_list]
    except TypeError:
        result = []

    if ctx.invoked_subcommand is None:
        printer(input_data=result, output=output)
    else:
        ctx.obj["RESULT"] = result
