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
    # from languru.server.app_agent import run_app

    # click.echo("Running server")
    # run_app()
    pass  # TODO: Implement


@click.command("run")
@click.option("--action", default=None, help="Action to run")
@click.option("--port", "-p", default=None, help="Port to run the server")
@click.option("--auto-port", default=True, help="Port to run the server")
def llm_run(action: Optional[Text], port: Optional[int], auto_port: bool = True):
    from languru.server.config import AppType, LlmSettings
    from languru.server.main import run_app
    from languru.utils.socket import check_port, get_available_port

    settings = LlmSettings()
    settings.APP_TYPE = os.environ["APP_TYPE"] = AppType.llm

    # Parse action parameter
    if action is not None and action.strip() != "":
        os.environ["ACTION"] = settings.action = action.strip()

    # Parse port parameter
    if port is None and auto_port is True:
        port = get_available_port(settings.DEFAULT_PORT)  # Search for available port
    elif port is None:
        port = settings.DEFAULT_PORT
    if check_port(port) is False:
        raise ValueError(f"The port '{settings.PORT}' is already in use")
    if port != settings.DEFAULT_PORT:
        click.echo(f"Using port {port} instead of default port {settings.DEFAULT_PORT}")
    settings.PORT, os.environ["PORT"] = port, str(port)

    # Run the app
    click.echo("Running llm server")
    run_app(settings=settings)


app.add_command(server)
app.add_command(llm)
server.add_command(server_run)
llm.add_command(llm_run)


if __name__ == "__main__":
    app()
