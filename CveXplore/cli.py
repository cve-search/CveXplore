import click

from CveXplore.cli_cmds.version import commands as group1
from CveXplore.main import CveXplore


@click.group()
@click.option('--version', help='Show the current version and exit')
@click.pass_context
def main(ctx):
    ctx.obj = CveXplore()


main.add_command(group1.version_cmd)
