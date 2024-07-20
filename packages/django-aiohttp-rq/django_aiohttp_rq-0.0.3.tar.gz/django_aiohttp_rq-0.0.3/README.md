### Installation
```bash
$ pip install django-aiohttp-rq
```

#### `settings.py`
```python
INSTALLED_APPS+=['django_aiohttp_rq']

# optional
AIOHTTP_RQ_BRIDGE_RESTART_INTERVAL=1 # 0.1 default
AIOHTTP_RQ_BRIDGE_SLEEP_INTERVAL=1 # 0.1 default
AIOHTTP_RQ_BRIDGE_QUERY="CALL schema.procedure()"
```
#### `migrate`
```bash
$ python manage.py migrate
```

### Environment variables
[aiohttp-rq](https://pypi.org/project/aiohttp-rq) env variables required

Variable|default
-|-
`AIOHTTP_RQ_DIR`|`None`
`AIOHTTP_RQ_REQUEST_QUEUE`|`aiohttp-rq-request`
`AIOHTTP_RQ_RESPONSE_QUEUE`|`aiohttp-rq-response`
`AIOHTTP_RQ_REQUEST_EXCEPTION_QUEUE`|`aiohttp-rq-request-exception`

### Features
+   based on [aiohttp-rq](https://pypi.org/project/aiohttp-rq)
+   admin interface
+   management commands
+   debug messages if `setting.DEBUG` enabled

### Management commands
name|description
-|-
`aiohttp_rq_bridge`|redis bridge worker
`aiohttp_rq_pull`|pull
`aiohttp_rq_push`|push

### Examples
```bash
$ python manage.py aiohttp_rq_bridge
```

