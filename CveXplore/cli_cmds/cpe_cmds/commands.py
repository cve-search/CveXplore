from pprint import pformat

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
    help="Search for cpe entries by name or title. Results are sorted ASCENDING by default",
)
@click.option(
    "-n",
    "--name",
    default=False,
    is_flag=True,
    help="Search by name",
    cls=Mutex,
    not_required_if=["title", "vendor"],
)
@click.option(
    "-t",
    "--title",
    default=True,
    is_flag=True,
    help="Search by title (default)",
    cls=Mutex,
    not_required_if=["name", "vendor"],
)
@click.option(
    "-v",
    "--vendor",
    default=False,
    is_flag=True,
    help="Search by vendor",
    cls=Mutex,
    not_required_if=["name", "title"],
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
@click.option("-c", "--cve", is_flag=True, help="Add related CVE's")
@click.option(
    "-p",
    "--product_search",
    default=False,
    is_flag=True,
    help="If adding CVE's search for vulnerable products and not for vulnerable configurations",
)
@click.option("-l", "--limit", default=10, help="Search limit")
@click.option("-s", "--sort", is_flag=True, help="Sort DESCENDING")
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
    name,
    title,
    vendor,
    match,
    regex,
    deprecated,
    cve,
    product_search,
    limit,
    sort,
    pretty,
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
    else:
        click.echo(search_cmd.get_help(ctx))
        return

    if cve:
        result = [result.to_cve_summary(product_search) for result in ret_list]
    else:
        result = [result.to_dict() for result in ret_list]

    if ctx.invoked_subcommand is None:
        printer(input_data=result, pretty=pretty, output=output)
    else:
        if pretty:
            ctx.obj["RESULT"] = pformat(result, indent=4)
        else:
            ctx.obj["RESULT"] = result
