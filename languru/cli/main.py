from typing import Optional

import click


@click.group()
def languru_cli():
    pass


@click.group()
def server():
    pass


@click.command("version")
@click.option("--short", "-s", default=False, help="Action to run", is_flag=True)
def pkg_version(short: bool = False):
    from languru.version import VERSION

    if short is True:
        click.echo(VERSION)
    else:
        click.echo(f"languru {VERSION}")


@click.command("run")
@click.option("--port", "-p", default=None, help="Port to run the server")
def server_run(port: Optional[int] = None):
    from languru.server.build import run_app
    from languru.server.config import ServerBaseSettings

    settings = ServerBaseSettings()
    if port is not None:
        settings.PORT = port

    # Run the app
    click.echo("Running server")
    run_app(settings=settings)


server.add_command(server_run)

languru_cli.add_command(server)
languru_cli.add_command(pkg_version)


if __name__ == "__main__":
    languru_cli()
