import json
import pathlib
import logging

import click
import click_log
import requests

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


def data_sender(loader, host):
    for e in loader():
        r = requests.post(host, json=e)
        logger.debug(r.status_code)


def find_files(directory, extensions):
    patterns = tuple(('*.%s' % ext for ext in extensions.split(',')))

    def files():
        for pattern in patterns:
            for fn in pathlib.Path(directory).glob(pattern):
                yield fn
    return files


def load_json(files_finder):
    def load():
        for fn in files_finder():
            with open(fn) as f:
                for line in f:
                    yield json.loads(line)
    return load


def data_loader(directory, extensions):
    return load_json(find_files(directory, extensions))


@click.command()
@click.option(
    '--host', '-h',
    type=click.STRING,
    required=True,
    help='path to the directory cotaining the files'
)
@click.option(
    '--directory', '-d', required=True,
    type=click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    help='path to the directory cotaining the files',
)
@click.option(
    '--extensions', '-e', 'extensions',
    type=click.STRING,
    default='json,jsonl',
    help='file extensions'
)
@click_log.simple_verbosity_option(logger)
def cli(host, directory, extensions):
    loader = data_loader(directory, extensions)
    logger.info("Sending ...")
    data_sender(loader, host)
    logger.info("Done")


if __name__ == '__main__':
    cli()
