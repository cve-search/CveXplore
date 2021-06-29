import click

from CveXplore.cli_cmds.single_collection import commands as group1
from CveXplore.cli_cmds.cve_cmds import commands as group2
from CveXplore.cli_cmds.stats import commands as group3
from CveXplore.cli_cmds.db_cmds import commands as group4
from CveXplore.main import CveXplore


@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Show the current version and exit")
@click.pass_context
def main(ctx, version):
    ctx.obj = {"data_source": CveXplore()}
    if version:
        click.echo(ctx.obj["data_source"].version)
        exit(0)


main.add_command(group1.single_collection_cmd)
main.add_command(group2.cve_cmd)
main.add_command(group3.stats_cmd)
main.add_command(group4.db_cmd)
