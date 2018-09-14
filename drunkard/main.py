import json
import pathlib
import logging
from os import path

import click
import click_log
import requests

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

_INDEX_FILE_NAME = ".drunkard.index"


def _save_index_file(index_info, posix_file, index, success):
    index_info[posix_file.name] = {"index": index, "success": success}
    with open(path.join(posix_file.parent, _INDEX_FILE_NAME), 'w') as f:
        f.write(json.dumps(index_info))


def _load_index_file(posix_file):
        filepath = path.join(posix_file.parent, _INDEX_FILE_NAME)
        if not path.isfile(filepath):
            return {}

        with open(filepath, "r") as f:
            content = f.read()
            if len(content) > 2:
                return json.loads(content)
            return {}


def data_sender(files, url):
    count = 0

    session = requests.Session()

    for f in files():
        dir_info = _load_index_file(f)
        if f.name in dir_info and dir_info[f.name].get("success", False):
            continue

        current_index = 0
        sent_index = dir_info.get(f.name, {"index": 0}).get("index", 0)

        for r in load_json(f):
            if sent_index > current_index:
                current_index += 1
                continue

            try:
                r = session.post(url, json=r)
                logger.debug(r.status_code)
                if r.status_code < 300:
                    count += 1

            except requests.exceptions.RequestException as e:
                logger.error(e)
                _save_index_file(dir_info, f, current_index, False)
                return count

            current_index += 1

        _save_index_file(dir_info, f, current_index, True)

    return count


def load_json(filename):
    with open(filename) as f:
        for line in f:
            yield json.loads(line)


def find_files(directory, extensions):
    patterns = tuple(('*.%s' % ext for ext in extensions.split(',')))

    def files():
        for pattern in patterns:
            for fn in pathlib.Path(directory).glob(pattern):
                yield fn
    return files


@click.command()
@click.option(
    '--url', '-u',
    type=click.STRING,
    required=True,
    help='server url where to send records'
)
@click.option(
    '--directory', '-d', required=True,
    type=click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    help='path to the directory cotaining the files',
)
@click.option(
    '--extensions', '-e',
    type=click.STRING,
    default='json,jsonl',
    help='file extensions'
)
@click.option(
    '--force', '-f',
    type=click.BOOL,
    default=False,
    help='force send all data again'
)
@click_log.simple_verbosity_option(logger)
def cli(url, directory, extensions, force):
    file_loader = find_files(directory, extensions)
    logger.info("Sending ...")
    count = data_sender(file_loader, url)
    logger.info(f"Done: {count} records sent")


if __name__ == '__main__':
    cli()
