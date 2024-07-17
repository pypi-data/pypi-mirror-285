import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

REQUEST_QUEUE = os.getenv("AIOHTTP_RQ_REQUEST_QUEUE", "aiohttp_rq_request")
RESPONSE_QUEUE = os.getenv("AIOHTTP_RQ_RESPONSE_QUEUE", "aiohttp_rq_response")
REQUEST_EXCEPTION_QUEUE = os.getenv("AIOHTTP_RQ_REQUEST_EXCEPTION_QUEUE", "aiohttp_rq_request_exception")
