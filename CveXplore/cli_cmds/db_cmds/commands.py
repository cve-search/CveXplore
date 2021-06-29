import click


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


@db_cmd.group("populate", invoke_without_command=True, help="Populate the database")
@click.pass_context
def populate_cmd(ctx):
    ctx.obj["data_source"].database.populate()
