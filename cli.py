import click
from app.main import main


@click.group()
def cli():
    pass


@cli.command()
@click.option('--interval', type=int, required=True)
@click.option('--filepath', type=str, required=True)
@click.option('--source-format', type=click.Choice(['csv']), required=True)
def run_service(interval, filepath, source_format):
    if source_format == 'csv':
        main(interval, filepath)


if __name__ == '__main__':
    cli()
