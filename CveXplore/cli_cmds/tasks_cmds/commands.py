import click
from tabulate import tabulate

from CveXplore.core.general.constants import task_status_rev_types
from CveXplore.core.general.utils import (
    datetimeToTimestring,
    set_ansi_color_red,
    set_ansi_color_green,
    set_ansi_color_magenta,
    set_ansi_color_yellow,
)


@click.group(
    "tasks",
    invoke_without_command=True,
    help="Perform task related operations.",
)
@click.pass_context
def tasks_cmd(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(tasks_cmd.get_help(ctx))


@tasks_cmd.group(
    "list",
    invoke_without_command=True,
    help="List the available tasks that can be scheduled.",
)
@click.pass_context
def list_cmd(ctx):
    header_list = ["#", "Task name", "Task description"]
    x = 1
    table_list = [header_list]
    for k, v in ctx.obj["data_source"].task_handler.show_available_tasks().items():
        table_list.append([x, k, v])
        x += 1
    click.echo(tabulate(table_list, headers="firstrow", tablefmt="fancy_grid"))


@tasks_cmd.group(
    "scheduled",
    invoke_without_command=True,
    help="Perform action on tasks that are currently scheduled.",
)
@click.option(
    "-l",
    "--list",
    is_flag=True,
    help="List tasks that are scheduled.",
)
@click.pass_context
def scheduled_cmd(ctx, list):

    if list:
        header_list = [
            "#",
            "Task slug",
            "Task name",
            "Task description",
            "Type",
            "Schedule",
            "Args/Kwargs",
            "Enabled",
            "Last run at [Result] [Total]",
            "Next run at",
        ]
        x = 1
        table_list = [header_list]
        scheduled_tasks = ctx.obj["data_source"].task_handler.show_scheduled_tasks()
        for each in scheduled_tasks:
            task = each.to_dict()
            table_list.append(
                [
                    x,
                    task["name"],
                    task["task"].replace("CveXplore.celery_app.", ""),
                    task["description"],
                    "Crontab" if task["crontab"] else "Interval",
                    task["run"],
                    f"{task['args']} / {task['kwargs']}",
                    (
                        set_ansi_color_green(task["enabled"])
                        if task["enabled"]
                        else set_ansi_color_red(task["enabled"])
                    ),
                    f"{set_ansi_color_magenta(datetimeToTimestring(task['last_run_at']))} "
                    f"[{set_ansi_color_red(task_status_rev_types[task['last_run_result']].upper()) if task['last_run_result'] == ctx.obj['data_source'].config.CELERY_TASK_FAILED_ERROR_CODE else set_ansi_color_green(task_status_rev_types[task['last_run_result']].upper())}] "
                    f"[{set_ansi_color_yellow(task['total_run_count'])}]",
                    set_ansi_color_magenta(datetimeToTimestring(task["next_run_at"])),
                ]
            )
            x += 1

        click.echo(tabulate(table_list, headers="firstrow", tablefmt="fancy_grid"))

    else:
        if ctx.invoked_subcommand is None:
            click.echo(tasks_cmd.get_help(ctx))
