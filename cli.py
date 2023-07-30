import click
from app.main import main


@click.group()
def cli():
    pass


@cli.command()
@click.option("--interval", type=int, required=True)
@click.option("--server-address", type=str, required=True)
def run_service(interval, server_address):
    main(interval, server_address)


if __name__ == "__main__":
    cli()
