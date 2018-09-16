import asyncio
import json
import pathlib
import logging
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


async def post_record(url, session, data):
    async with session.post(url, json=data) as response:
        return await response.read()


async def newsProducer(queue, files):
    for f in files():
        for r in load_json(f):
            # print("putting", r)
            await queue.put(r)
    await queue.put(None)
    print("feito")


async def newsConsumer(id, queue, url):
    async with ClientSession() as session:
        while True:
            item = await queue.get()
            if item is None:
                # the producer emits None to indicate that it is done
                print(f"finishing {id}")
                break
            await post_record(url, session, item)
            queue.task_done()


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

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop, maxsize=20)

    try:

        loop.run_until_complete(asyncio.gather(
            newsProducer(queue, file_loader),
            newsConsumer(1, queue, url),
            # newsConsumer(2, queue, url),
            # newsConsumer(3, queue, url),
            # newsConsumer(4, queue, url),
            # newsConsumer(5, queue, url),
            # newsConsumer(6, queue, url),
            # newsConsumer(7, queue, url),
            # newsConsumer(8, queue, url),
            # newsConsumer(9, queue, url),
            # newsConsumer(10, queue, url),
            # newsConsumer(11, queue, url),
            # newsConsumer(12, queue, url),
            # newsConsumer(13, queue, url),
            # newsConsumer(14, queue, url),
            # newsConsumer(16, queue, url),
            # newsConsumer(17, queue, url),
            # newsConsumer(18, queue, url),
            # newsConsumer(19, queue, url),
            # newsConsumer(20, queue, url),
            # newsConsumer(21, queue, url),
            # newsConsumer(22, queue, url),
            # newsConsumer(23, queue, url),
            # newsConsumer(24, queue, url),
            # newsConsumer(25, queue, url),
            # newsConsumer(26, queue, url),
            # newsConsumer(27, queue, url),
            # newsConsumer(28, queue, url),
            # newsConsumer(29, queue, url),
        ))

    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    cli()
