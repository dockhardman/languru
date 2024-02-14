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
def llm_run(action: Optional[Text]):
    if action is not None and action.strip() != "":
        os.environ["ACTION"] = action.strip()

    from languru.llm.app import run_app

    click.echo("Running llm server")
    run_app()


app.add_command(server)
app.add_command(llm)
server.add_command(server_run)
llm.add_command(llm_run)


if __name__ == "__main__":
    app()
