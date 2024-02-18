import os
from typing import Optional, Text

import click


@click.group()
def app():
    pass


@click.group()
def server():
    pass


@click.group()
def llm():
    pass


@click.command("run")
def server_run():
    from languru.server.app import run_app

    click.echo("Running server")
    run_app()


@click.command("run")
@click.option("--action", default=None, help="Action to run")
@click.option("--port", "-p", default=None, help="Port to run the server")
def llm_run(action: Optional[Text], port: Optional[int]):
    from yarl import URL

    from languru.llm.app import run_app
    from languru.llm.config import settings
    from languru.utils.socket import check_port, get_available_port

    # Parse action parameter
    if action is not None and action.strip() != "":
        os.environ["ACTION"] = settings.action = action.strip()
    # Parse port parameter
    if port is None:
        port = get_available_port(settings.DEFAULT_PORT)  # Determine port
    else:
        if check_port(port) is False:
            raise ValueError(f"The port '{settings.PORT}' is already in use")
    if port != settings.DEFAULT_PORT:
        click.echo(f"Using port {port} instead of default port {settings.DEFAULT_PORT}")
    settings.PORT = port
    os.environ["PORT"] = str(port)
    # Parse action base url
    os.environ["ACTION_BASE_URL"] = settings.ACTION_BASE_URL = str(
        URL(settings.ACTION_BASE_URL).with_port(port)
    )

    # Run the app
    click.echo("Running llm server")
    run_app()


app.add_command(server)
app.add_command(llm)
server.add_command(server_run)
llm.add_command(llm_run)


if __name__ == "__main__":
    app()
