import asyncio
import json
import logging
import os
import sys
import time

import aiohttp
import click

from .redis_client import REDIS, REQUEST_QUEUE
from .utils import get_client_session_kwargs, get_request_kwargs, process_request_exception, process_response


AIOHTTP_RQ_DEBUG = bool(os.environ.get('AIOHTTP_RQ_DEBUG',None))

async def worker(session):
    while True:
        try:
            redis_value = REDIS.lpop(REQUEST_QUEUE)
            if not redis_value:
                await asyncio.sleep(0.1)
                continue
        except Exception as e: # redis exception
            logging.error(e)
            time.sleep(10) # slowdown restarts and logging spam
            sys.exit(1)
        try:
            redis_data = json.loads(redis_value.decode("utf-8"))
            request_kwargs = get_request_kwargs(redis_data)
        except Exception as e:
            logging.error(e)
            sys.exit(1)
        try:
            if AIOHTTP_RQ_DEBUG:
                print('%s %s' % (request_kwargs['method'],request_kwargs['url']))
            async with session.request(**request_kwargs) as response:
                if AIOHTTP_RQ_DEBUG:
                    print('%s %s' % (request_kwargs['url'],response.status))
                await process_response(redis_data,response)
        except Exception as e: # session.request() exception
            if AIOHTTP_RQ_DEBUG:
                print('%s\n%s: %s' % (request_kwargs['url'],type(e),str(e)))
            process_request_exception(redis_data,e)


async def asyncio_main(loop, workers_count):
    async with aiohttp.ClientSession(**get_client_session_kwargs()) as session:
        task_list = list(map(lambda i:worker(session),[None]*workers_count))
        await asyncio.gather(*task_list, return_exceptions=True)


@click.command()
@click.argument('workers_count', required=True)
def main(workers_count):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(asyncio_main(loop, int(workers_count)))

if __name__ == '__main__':
    main(prog_name='python -m aiohttp_rq')
