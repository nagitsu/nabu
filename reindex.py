import click

from corpus.indexing import reindex_documents


@click.command()
@click.option('--limit', default=None)
@click.option('--force', default=False)
def main(limit, force):
    reindex_documents(limit, force)


if __name__ == '__main__':
    main()
