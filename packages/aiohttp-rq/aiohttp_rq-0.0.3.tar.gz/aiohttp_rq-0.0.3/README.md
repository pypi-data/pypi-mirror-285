### Installation
```bash
$ pip install aiohttp-rq
```

### Environment variables
Variable|default
-|-
`AIOHTTP_RQ_DIR`|`None`
`AIOHTTP_RQ_REQUEST_QUEUE`|`aiohttp-rq-request`
`AIOHTTP_RQ_RESPONSE_QUEUE`|`aiohttp-rq-response`
`AIOHTTP_RQ_EXCEPTION_QUEUE`|`aiohttp-rq-exception`

optional
Variable|default
-|-
`AIOHTTP_RQ_DEBUG`|`None`
`AIOHTTP_RQ_DIR`|`None`
`REDIS_HOST`|`localhost`
`REDIS_PORT`|`6379`
`REDIS_DB`|`0`

### Examples
```bash
$ export AIOHTTP_RQ_REQUEST_QUEUE="aiohttp-rq-request"
$ export AIOHTTP_RQ_RESPONSE_QUEUE="aiohttp-rq-response"
$ export AIOHTTP_RQ_EXCEPTION_QUEUE="aiohttp-rq-exception"
$ python3 -m aiohttp_rq 100 # 100 workers
```

### Redis
```python
import redis

REDIS = redis.Redis(host='localhost', port=6379, db=0)
```

#### Redis push

```python
value=json.dumps(dict(
    url='https://domain.com',
    method="GET",
    headers=None,
    data=None,
    allow_redirects=True
))
REDIS.rpush('aiohttp-rq-request',*values)
```

#### Redis pull

```python
item_list = REDIS.lrange('aiohttp-rq-response',0,-1)
for item in item_list:
    data = json.loads(item.encode('utf-8'))

item_list = REDIS.lrange('aiohttp-rq-exception',0,-1)
for item in item_list:
    data = json.loads(item.encode('utf-8'))
```

### DEBUG

```bash
$ export AIOHTTP_RQ_DEBUG=1
```

