import click

from CveXplore.cli_cmds.cli_utils.utils import printer


@click.group("stats", invoke_without_command=True)
@click.option("-d", "--datasource", is_flag=True, help="Show the datasource statistics")
@click.option("--pretty", is_flag=True, help="Pretty print the output")
@click.pass_context
def stats_cmd(ctx, datasource, pretty, output="json"):
    if ctx.invoked_subcommand is None:
        printer(
            input_data=ctx.obj["data_source"].get_db_content_stats(),
            pretty=pretty,
            output=output,
        )
    else:
        printer(
            input_data=ctx.obj["data_source"].get_db_content_stats(),
            pretty=pretty,
            output=output,
        )
