import click


@click.command("version")
@click.pass_obj
def version_cmd(cvex):
    click.echo(cvex.version)
