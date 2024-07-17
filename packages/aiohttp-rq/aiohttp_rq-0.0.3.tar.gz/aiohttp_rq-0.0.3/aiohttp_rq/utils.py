import io
import json
import logging
import os
import sys
import uuid

import aiohttp

from .redis_client import REDIS, REQUEST_EXCEPTION_QUEUE, RESPONSE_QUEUE


AIOHTTP_RQ_DIR = os.environ['AIOHTTP_RQ_DIR']
if not os.path.exists(AIOHTTP_RQ_DIR):
    os.makedirs(AIOHTTP_RQ_DIR)
CONNECTOR_LIMIT = int(os.getenv("AIOHTTP_RQ_CONNECTOR_LIMIT", 100))
CONNECTOR_LIMIT_PER_HOST = int(os.getenv("AIOHTTP_RQ_CONNECTOR_LIMIT_PER_HOST", 0))
CHUNK_SIZE = 8 * 1024  # 8 KB
# https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.request
REQUEST_KEYS = ['method','url','params','data','json','headers','cookies','allow_redirects','compress','chunked','expect100','raise_for_status',]

def get_aiohttp_connector():
    # https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.TCPConnector
    return aiohttp.TCPConnector(
        limit=CONNECTOR_LIMIT,  # default 100
        limit_per_host=CONNECTOR_LIMIT_PER_HOST,  # default 0
        #ttl_dns_cache=300,  # default 10
        #enable_cleanup_closed=True,
    )

def get_aiohttp_timeout():
    # https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientTimeout
    return aiohttp.ClientTimeout(
        # total=60, # timeout for the whole request
        # connect=30, # timeout for acquiring a connection from pool
        #sock_connect=10,  # timeout for connecting to a peer for a new connection
        # sock_read=10,  # timeout for reading a portion of data from a peer
    )

def get_client_session_kwargs():
    return dict(
        connector=get_aiohttp_connector(),
        timeout=get_aiohttp_timeout()
    )

def get_content_path():
    return os.path.join(AIOHTTP_RQ_DIR,uuid.uuid4().hex)

def get_request_kwargs(data):
    kwargs = {}
    for k,v in data.items():
        if k in REQUEST_KEYS:
            kwargs[k] = v
    return kwargs


async def write_content(response,content_path):
    f = io.BytesIO()
    try:
        while True:  # known-issue: empty response
            chunk = await response.content.read(CHUNK_SIZE)
            if not chunk:
                break
            f.write(chunk)
        content_dir = os.path.dirname(content_path)
        if not os.path.exists(content_dir):
            os.makedirs(content_dir)
        with open(str(content_path), "wb") as fd:
            fd.write(f.getbuffer())
    finally:
        f.close()

async def process_response(redis_data,response):
    content_path = get_content_path()
    await write_content(response,content_path)
    push(RESPONSE_QUEUE, dict(
        request=redis_data,
        url=str(response.url),
        status=int(response.status),
        headers = dict(response.headers),
        content_path=content_path
    ))

def push(queue,data):
    try:
        REDIS.rpush(queue, json.dumps(data))
    except Exception as e:
        logging.error(e)
        time.sleep(1)

def process_request_exception(redis_data,e):
    push(REQUEST_EXCEPTION_QUEUE, dict(
        url=redis_datap['url'],
        exc_class="%s.%s" % (type(e).__module__, type(e).__name__),
        exc_message=str(e)
    ))
