import asyncio
import json
import pathlib
import logging
from os import path
from aiohttp import ClientSession

import click
import click_log


logger = logging.getLogger(__name__)
click_log.basic_config(logger)


def find_files(directory, extensions):
    patterns = tuple(('*.%s' % ext for ext in extensions.split(',')))

    def files():
        for pattern in patterns:
            for fn in pathlib.Path(directory).glob(pattern):
                yield fn
    return files


def load_json(filename):
    with open(filename) as f:
        for line in f:
            yield json.loads(line)


async def fetch(url, session):
    async with session.get(url) as response:
        delay = response.headers.get("DELAY")
        date = response.headers.get("DATE")
        print("{}:{} with delay {}".format(date, response.url, delay))
        return await response.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def post_record(url, session, data):
    async with session.post(url, json=data) as response:
        # delay = response.headers.get("DELAY")
        # date = response.headers.get("DATE")
        # print("{}:{} with delay {}".format(date, response.url, delay))
        return await response.read()


async def bound_post(sem, url, session, r):
    # Getter function with semaphore.
    async with sem:
        await post_record(url, session, r)


async def send_file(sem, session, f, url):
    with open(f, 'rb') as file:
        await session.post(url, data=file)


async def run(r, files, url):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(r)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for f in files():
            # pass Semaphore and session to every GET request
            # task = asyncio.ensure_future(bound_fetch(sem, url.format(i), session))

            for r in load_json(f):
                task = asyncio.ensure_future(
                    bound_post(sem, url, session, r)
                )
                tasks.append(task)
            # task = asyncio.ensure_future(
            #     send_file(sem, session, f, url)
            # )
            # tasks.append(task)

            # task = asyncio.ensure_future(
            #     send_file(sem, session, f, url)
            # )
            # tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses


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
    # logger.info("Sending ...")
    # count = data_sender(file_loader, url)
    # logger.info(f"Done: {count} records sent")

    number = 10000
    loop = asyncio.get_event_loop()

    future = asyncio.ensure_future(run(number, file_loader, url))
    loop.run_until_complete(future)


if __name__ == '__main__':
    cli()
