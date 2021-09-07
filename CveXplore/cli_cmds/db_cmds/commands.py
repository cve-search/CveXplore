import json
import os

import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.database.maintenance.Config import Configuration, runPath


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
@click.pass_context
def sources_cmd(ctx):
    pass


@sources_cmd.group("show", invoke_without_command=True, help="Show sources")
@click.option("--pretty", is_flag=True, help="Pretty print the output")
@click.pass_context
def show_cmd(ctx, pretty):
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


@sources_cmd.group("set", invoke_without_command=True, help="Set sources")
@click.option(
    "-k",
    "--key",
    help="Set the source key",
    type=click.Choice(["capec", "cpe", "cwe", "via4", "cves"], case_sensitive=False),
)
@click.option(
    "-v",
    "--value",
    help="Set the source key value",
)
@click.pass_context
def set_cmd(ctx, key, value):
    config = Configuration()

    sources = config.SOURCES

    sources[key] = value

    with open(os.path.join(runPath, "../../.sources.ini"), "w") as f:
        f.write(json.dumps(sources))

    printer(input_data={"SOURCES SET TO": sources}, pretty=True)


@sources_cmd.group("reset", invoke_without_command=True, help="Set sources")
@click.pass_context
def reset_cmd(ctx):
    config = Configuration()

    sources = config.DEFAULT_SOURCES

    with open(os.path.join(runPath, "../../.sources.ini"), "w") as f:
        f.write(json.dumps(sources))

    printer(input_data={"SOURCES RESET TO": sources}, pretty=True)
