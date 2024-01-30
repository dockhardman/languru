import click


@click.group()
def app():
    pass


@click.group()
def server():
    pass


@click.command("run")
def server_run():
    from languru.server.app import run_app

    click.echo("Running server")
    run_app()


app.add_command(server)
server.add_command(server_run)


if __name__ == "__main__":
    app()
