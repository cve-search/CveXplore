import json
import os

import click

from CveXplore.cli_cmds.cli_utils.utils import printer
from CveXplore.common.config import Configuration


@click.group(
    "database", invoke_without_command=True, help="Database update / populate commands"
)
@click.pass_context
def db_cmd(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(db_cmd.get_help(ctx))


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
    if ctx.invoked_subcommand is None:
        click.echo(sources_cmd.get_help(ctx))


@sources_cmd.group("show", invoke_without_command=True, help="Show sources")
@click.pass_context
def show_cmd(ctx):
    config = Configuration

    if ctx.invoked_subcommand is None:
        printer(input_data=[config.SOURCES])
    else:
        printer(input_data=[config.SOURCES])


@sources_cmd.group("set", invoke_without_command=True, help="Set sources")
@click.option(
    "-k",
    "--key",
    help="Set the source key",
    type=click.Choice(["capec", "cpe", "cwe", "via4", "cves"], case_sensitive=False),
)
@click.option("-v", "--value", help="Set the source key value")
@click.pass_context
def set_cmd(ctx, key, value):
    config = Configuration

    sources = config.SOURCES

    sources[key] = value

    with open(os.path.join(config.USER_HOME_DIR, ".sources.ini"), "w") as f:
        f.write(json.dumps(sources))

    printer(input_data=[{"SOURCES SET TO": sources}])


@sources_cmd.group("reset", invoke_without_command=True, help="Set sources")
@click.pass_context
def reset_cmd(ctx):
    config = Configuration

    sources = config.DEFAULT_SOURCES

    with open(os.path.join(config.USER_HOME_DIR, ".sources.ini"), "w") as f:
        f.write(json.dumps(sources))

    printer(input_data=[{"SOURCES RESET TO": sources}])
