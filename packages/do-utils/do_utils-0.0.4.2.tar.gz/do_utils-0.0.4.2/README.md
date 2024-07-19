# do_utils
Utils write for common usage.

## do_time

Func timer - count func time with decorator

- Usage:

```python
from do_utils import do_time
from time import sleep

@do_time()
def do_print():
    sleep(0.01)

class A(object):
    @do_time(func=False)
    def do_print(self):
        sleep(0.01)
```

## do_cache

Do cache for GET request url handler in Tornado server

```text
do_cache:
    do cahche for request with uri & user & params
    cache_key include (protocol, host_name, path, md5(current_user, params))
    cache_expire depend on kwargs expire, the default is 5*60s
    cache from write_buffer that have not flushed wrote by self.write() and will be flush
    if cache is none:
        get data & return data & do cache
    else:
        return cache
do_api_cache:
    do cache for api handler
    if status_code == 200:
        do_cache
do_temp_cache:
    do cache for template handler
```

- Usage:

```python
from do_utils import do_api_cache, do_temp_cache

class ApiHandler(object):
    @do_api_cache(10)
    def get(self):
        print 'get api'

    @do_temp_cache(10, with_user=False)
    def get(self):
        print 'get template'
```

## Change History

- v0.0.1

```text
do utils
do api/template cache for tornado server with redis
```

- v0.0.2

```text
bugfix for install_requires cannot using 'requirements.txt'
add prefix for cache_key: 'cache:'
```

- v0.0.3

```text
bugfix for Python3 and dependence
```

- v0.0.4.2

```text
bugfix for Python3 and update dependence
```
