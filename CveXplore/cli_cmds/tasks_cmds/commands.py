import click
from tabulate import tabulate

from CveXplore.cli_cmds.mutex_options.mutex import Mutex
from CveXplore.core.general.constants import task_status_rev_types
from CveXplore.core.general.utils import (
    datetimeToTimestring,
    set_ansi_color_red,
    set_ansi_color_green,
    set_ansi_color_magenta,
    set_ansi_color_yellow,
    timestampTOdatetimestring,
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
    header_list = ["ID", "Task name", "Task description"]
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
@click.option(
    "-d",
    "--delete",
    type=int,
    help="Delete scheduled tasks by task id (id taken from -l / --list command).",
)
@click.option(
    "-t",
    "--toggle",
    type=int,
    help="Toggle scheduled tasks by task id (id taken from -l / --list command) between the enabled and disabled states.",
)
@click.option(
    "-p",
    "--purge",
    type=int,
    help="Purge the scheduled tasks results by task id (id taken from -l / --list command).",
)
@click.option(
    "-r",
    "--results",
    type=int,
    help="Show the (last 10) scheduled task results by task id (id taken from -l / --list command).",
)
@click.pass_context
def scheduled_cmd(ctx, list, delete, toggle, purge, results):

    if list:
        header_list = [
            "ID",
            "Task slug",
            "Task name",
            "Task description",
            "Schedule",
            "Enabled",
            "Last run at [Result] [Total]",
            "Next run at",
        ]
        x = 1
        table_list = [header_list]
        scheduled_tasks = ctx.obj["data_source"].task_handler.show_scheduled_tasks()
        for each in scheduled_tasks:
            task = each.to_dict()

            try:
                result = task_status_rev_types[task["last_run_result"]].upper()
                if result == "OK":
                    last_run_result = f"[{set_ansi_color_green(result)}]"
                else:
                    last_run_result = f"[{set_ansi_color_red(result)}]"
            except KeyError:
                last_run_result = "N/A"

            table_list.append(
                [
                    x,
                    task["name"],
                    task["task"].replace("CveXplore.celery_app.", ""),
                    task["description"],
                    task["run"],
                    (
                        set_ansi_color_green(task["enabled"])
                        if task["enabled"]
                        else set_ansi_color_red(task["enabled"])
                    ),
                    f"{set_ansi_color_magenta(datetimeToTimestring(task['last_run_at']))} "
                    f"{last_run_result} "
                    f"[{set_ansi_color_yellow(task['total_run_count'])}]",
                    set_ansi_color_magenta(datetimeToTimestring(task["next_run_at"])),
                ]
            )
            x += 1

        click.echo(tabulate(table_list, headers="firstrow", tablefmt="fancy_grid"))
    elif delete:
        click.echo(ctx.obj["data_source"].task_handler.delete_scheduled_task(delete))
    elif toggle:
        click.echo(ctx.obj["data_source"].task_handler.toggle_scheduled_task(toggle))
    elif purge:
        click.echo(ctx.obj["data_source"].task_handler.purge_scheduled_task(purge))
    elif results:
        header_list = [
            "ID",
            "Executed at",
            "Task id",
            "Task state",
            "Returned",
            "Task cost",
        ]
        x = 1
        table_list = [header_list]
        task_results = ctx.obj["data_source"].task_handler.get_scheduled_tasks_results(
            results
        )
        for each in task_results:
            table_list.append(
                [
                    x,
                    set_ansi_color_magenta(timestampTOdatetimestring(each["inserted"])),
                    each["task_id"],
                    each["state"],
                    each["returns"],
                    set_ansi_color_yellow(each["cost"]),
                ]
            )
            x += 1

        click.echo(tabulate(table_list, headers="firstrow", tablefmt="fancy_grid"))
    else:
        if ctx.invoked_subcommand is None:
            click.echo(tasks_cmd.get_help(ctx))


@tasks_cmd.group(
    "create",
    invoke_without_command=True,
    help="Perform action on tasks that are currently scheduled.",
)
@click.option(
    "-n",
    "--number",
    type=int,
    required=True,
    help="Create new task of type referred to by task id (id taken from 'cvexplore tasks list' command).",
)
@click.option(
    "-s",
    "--slug",
    required=True,
    help="Slug of the task to create.",
)
@click.option(
    "-i",
    "--interval",
    help="Use interval as tasks schedule; interval is in seconds.",
    type=int,
    cls=Mutex,
    not_required_if=["crontab"],
)
@click.option(
    "-c",
    "--crontab",
    help="Use crontab as tasks schedule; use csv value in format 'minute,hour,day_of_week,day_of_month,month_of_year'"
    "The crontab entry will be processed from left to right (from minute to month_of_year) with a '*' as a "
    "default entry. That means that is you only need to set the minute value to every minute -c */1 will suffice.",
    cls=Mutex,
    not_required_if=["interval"],
)
@click.pass_context
def scheduled_cmd(ctx, number, slug, interval, crontab):
    if interval:
        click.echo(
            ctx.obj["data_source"].task_handler.create_task_by_number(
                task_number=number, task_slug=slug, task_interval=interval
            )
        )
    elif crontab:

        the_crontab = {
            "minute": "*",
            "hour": "*",
            "day_of_week": "*",
            "day_of_month": "*",
            "month_of_year": "*",
        }

        crontab_list = crontab.split(",")
        try:
            i = 0
            for each in crontab_list:
                the_crontab[list(the_crontab.keys())[i]] = each
                i += 1

            click.echo(
                ctx.obj["data_source"].task_handler.create_task_by_number(
                    task_number=number, task_slug=slug, task_crontab=the_crontab
                )
            )
        except Exception as err:
            click.echo(
                f"Could not insert crontab; error: {err}",
            )
    else:
        if ctx.invoked_subcommand is None:
            click.echo(tasks_cmd.get_help(ctx))
