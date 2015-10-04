import click

from nabu import scrape as scrape_, webapp


@click.group()
def cli():
    pass


@cli.command()
def scrape():
    scrape_()


@cli.command()
def serve():
    webapp.run()


if __name__ == '__main__':
    cli()
