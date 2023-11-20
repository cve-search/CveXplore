import click
import pymongo

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.cli_cmds.mutex_options.mutex import Mutex


@click.group("cpe", invoke_without_command=True, help="Query for cpe specific data")
@click.pass_context
def cpe_cmd(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(cpe_cmd.get_help(ctx))


@cpe_cmd.group(
    "search",
    invoke_without_command=True,
    help="Search for cpe entries by name, vendor or title. Results are sorted ASCENDING by default",
)
@click.option(
    "-n",
    "--name",
    default=False,
    is_flag=True,
    help="Search by name",
    cls=Mutex,
    not_required_if=["field", "cpe", "title", "vendor", "field_list"],
)
@click.option(
    "-t",
    "--title",
    default=True,
    is_flag=True,
    help="Search by title (default)",
    cls=Mutex,
    not_required_if=["field", "cpe", "name", "vendor", "field_list"],
)
@click.option(
    "-v",
    "--vendor",
    default=False,
    is_flag=True,
    help="Search by vendor",
    cls=Mutex,
    not_required_if=["field", "cpe", "name", "title", "field_list"],
)
@click.option(
    "-c",
    "--cpe",
    help="Search for CPE's (could be multiple) by id",
    multiple=True,
    cls=Mutex,
    not_required_if=["name", "title", "vendor"],
)
@click.option(
    "-f",
    "--field",
    help="Field to return (could be multiple)",
    multiple=True,
    cls=Mutex,
    not_required_if=["field_list", "name", "title", "vendor"],
)
@click.option(
    "-fl",
    "--field_list",
    help="Return a field list for this collection",
    is_flag=True,
    cls=Mutex,
    not_required_if=["field", "name", "title", "vendor"],
)
@click.option(
    "-m",
    "--match",
    help="Use match for searching",
    cls=Mutex,
    not_required_if=["regex"],
)
@click.option(
    "-r",
    "--regex",
    help="Use regex for searching",
    cls=Mutex,
    not_required_if=["match"],
)
@click.option("-d", "--deprecated", is_flag=True, help="Filter deprecated cpe's")
@click.option("-rc", "--related_cve", is_flag=True, help="Add related CVE's")
@click.option(
    "-p",
    "--product_search",
    default=False,
    is_flag=True,
    help="Let CveXplore search for vulnerable products and not for vulnerable configurations",
)
@click.option("-l", "--limit", default=10, help="Search limit")
@click.option("-s", "--sort", is_flag=True, help="Sort DESCENDING")
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
    name,
    title,
    vendor,
    cpe,
    field,
    field_list,
    match,
    regex,
    deprecated,
    related_cve,
    product_search,
    limit,
    sort,
    output,
):
    if not name and not vendor and title:
        search_by = "title"
    elif name and not vendor and title:
        search_by = "cpeName"
    else:
        search_by = "vendor"

    if not sort:
        sorting = pymongo.ASCENDING
    else:
        sorting = pymongo.DESCENDING

    if regex:
        if deprecated:
            ret_list = getattr(ctx.obj["data_source"], "cpe").search_active_cpes(
                search_by, regex, limit, sorting
            )
        else:
            ret_list = (
                getattr(getattr(ctx.obj["data_source"], "cpe"), search_by)
                .search(regex)
                .limit(limit)
                .sort(search_by, sorting)
            )
    elif match:
        if deprecated:
            ret_list = getattr(ctx.obj["data_source"], "cpe").find_active_cpes(
                search_by, match, limit, sorting
            )
        else:
            ret_list = (
                getattr(getattr(ctx.obj["data_source"], "cpe"), search_by)
                .find(match)
                .limit(limit)
                .sort(search_by, sorting)
            )
    elif cpe and not field_list:
        ret_list = getattr(ctx.obj["data_source"], "cpe").mget_by_id(*cpe)
    elif cpe and field_list:
        ret_list = getattr(ctx.obj["data_source"], "cpe").field_list(*cpe)
    else:
        click.echo(search_cmd.get_help(ctx))
        return

    if related_cve:
        result = [result.to_cve_summary(product_search) for result in ret_list]
    elif cpe and not field_list:
        result = [result.to_dict(*field) for result in ret_list]
    elif field_list:
        result = [result for result in ret_list]
    else:
        result = [result.to_dict() for result in ret_list]

    if ctx.invoked_subcommand is None:
        printer(input_data=result, output=output)
    else:
        ctx.obj["RESULT"] = result
