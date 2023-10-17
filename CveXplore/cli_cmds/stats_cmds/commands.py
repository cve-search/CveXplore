import click

from CveXplore.cli_cmds.cli_utils.utils import printer


@click.group(
    "stats",
    invoke_without_command=True,
    help="Show datasource statistics",
)
@click.pass_context
def stats_cmd(ctx, output="json"):
    if ctx.invoked_subcommand is None:
        printer(
            input_data=[ctx.obj["data_source"].get_db_content_stats()],
            output=output,
        )
