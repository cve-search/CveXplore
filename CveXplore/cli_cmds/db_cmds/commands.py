import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.database.maintenance.Config import Configuration


@click.group(
    "database", invoke_without_command=True, help="Database update / populate commands"
)
@click.pass_context
def db_cmd(ctx):
    pass


@db_cmd.group("update", invoke_without_command=True, help="Update the database")
@click.pass_context
def update_cmd(ctx):
    ctx.obj["data_source"].database.update()


@db_cmd.group("initialize", invoke_without_command=True, help="Initialize the database")
@click.pass_context
def initialize_cmd(ctx):
    ctx.obj["data_source"].database.initialize()


@db_cmd.group("sources", invoke_without_command=True, help="Database source management")
@click.option("--pretty", is_flag=True, help="Pretty print the output")
@click.pass_context
def sources_cmd(ctx, pretty):

    config = Configuration()

    if ctx.invoked_subcommand is None:
        printer(
            input_data=config.SOURCES,
            pretty=pretty,
        )
    else:
        printer(
            input_data=config.SOURCES,
            pretty=pretty,
        )
