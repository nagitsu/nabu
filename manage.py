import click

from nabu import scrape as scrape_, webapp


@click.group()
def cli():
    pass


@cli.command()
def scrape():
    scrape_()


@cli.command()
@click.option('--debug', default=True)
def serve(debug):
    webapp.run(debug=debug)


if __name__ == '__main__':
    cli()
