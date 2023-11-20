import logging

import click
import click_completion.core

from CveXplore.cli_cmds.capec_cmds import commands as group6
from CveXplore.cli_cmds.cpe_cmds import commands as group5
from CveXplore.cli_cmds.cve_cmds import commands as group2
from CveXplore.cli_cmds.cwe_cmds import commands as group7
from CveXplore.cli_cmds.db_cmds import commands as group4
from CveXplore.cli_cmds.find_cmds import commands as group1
from CveXplore.cli_cmds.stats_cmds import commands as group3
from CveXplore.main import CveXplore

click_completion.init()

logging.getLogger("dicttoxml").setLevel("ERROR")


@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Show the current version and exit")
@click.pass_context
def main(ctx, version):
    ctx.obj = {"data_source": CveXplore()}
    if version:
        click.echo(ctx.obj["data_source"].version)
        exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


main.add_command(group1.find_cmd)
main.add_command(group2.cve_cmd)
main.add_command(group3.stats_cmd)
main.add_command(group4.db_cmd)
main.add_command(group5.cpe_cmd)
main.add_command(group6.capec_cmd)
main.add_command(group7.cwe_cmd)
