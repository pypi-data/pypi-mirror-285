# -*- coding: utf-8 -*-
# -*- author: Jiangtao -*-

"""Do cache for GET request url handler in Tornado server
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

Usage:
    from do_cache import do_api_cache, do_temp_cache
    class ApiHandler(object):
        @do_api_cache(10)
        def get(self):
            return 'get api'

        @do_temp_cache(10, with_user=False)
        def get(self):
            return 'get template'
"""


import traceback
try:
    import ujson as json
except ImportError:
    import json
from logging import warning, info
from functools import wraps
# from time import time
from hashlib import md5
from datetime import date


def cache_count(redis_instance, count_type):
    log_key = 'url_handler_cache_count_{}_{}'.format(count_type, date.today())
    redis_instance.incr(name=log_key, amount=1)
    redis_instance.expire(name=log_key, time=86400*3)


def generate_key(req_handler, with_user=True):
    """generate redis key
    :param req_handler: current tornado request handler
    :param with_user: different cache data to single user if with_user, default True
    :return: key=protocol:host_name:path:md5((current_user, params))
    """
    current_user = req_handler.current_user if with_user else 0
    request = req_handler.request
    protocol = request.protocol
    host_name = request.host_name
    path = request.path
    params = request.query_arguments
    key = json.dumps((current_user, params))
    values = (
        protocol,
        host_name,
        path,
        md5(key).hexdigest())
    return ':'.join(values)


def do_cache(cache_type, expire=60 * 5, with_user=True):
    """do get request cache with expire(seconds)
    :param cache_type: interface type, must one of ('api', 'temp')
    :param expire: expiration, default 5*60s
    :param with_user: cache data to single user if with_user else to all, default True
    :return: decorator return
    """
    def decorator(method):
        """Decorator the class func"""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # start_time = time()
            try:
                # Deal with only GET method, return method while not GET method
                if self.request.method != 'GET':
                    return method(self, *args, **kwargs)

                r_cache = self.r_cache
                cache_count(r_cache, 'total')
                # get cached data, return cached data if not none
                redis_key = 'cache:' + generate_key(req_handler=self, with_user=with_user)
                cache_data = r_cache.get(redis_key)
                if cache_data is not None:
                    info('return cached data: key=%s, data_length=%s' %(redis_key, len(cache_data)))
                    cache_count(r_cache, 'cached')
                    return self.write(cache_data)

                # exec the method with none return of method
                method(self, *args, **kwargs)

                # get data to be cached from self._write_buffer for (api, temp)
                cache_data = b"".join(self._write_buffer)
                if cache_data:
                    if cache_type == 'api':
                        cache_data_dict = json.loads(cache_data)
                        status_code = cache_data_dict.get('code', 0) if isinstance(cache_data_dict, dict) else 0
                        # cached only when success(status_code == 200)
                        if status_code and status_code in [200]:
                            # cache only str or json data
                            if not isinstance(cache_data, (str, unicode)):
                                cache_data = json.dumps(cache_data)
                            r_cache.setex(redis_key, expire, cache_data)
                            # info('api cached data: key=%s, data=%s' % (redis_key, cache_data))
                            info('api cached data: key=%s, data_length=%s' % (redis_key, len(cache_data)))
                    elif cache_type == 'temp':
                        # cache only str or json data
                        if not isinstance(cache_data, (str, unicode)):
                            cache_data = json.dumps(cache_data)
                        r_cache.setex(redis_key, expire, cache_data)
                        # info('temp cached data: key=%s, data=%s'%(redis_key, cache_data))
                        info('temp cached data: key=%s, data_length=%s' % (redis_key, len(cache_data)))
                return
            except Exception as e:
                warning(traceback.format_exc())
            finally:
                # spend = round(1000 * (time() - start_time), 3)
                # warning('方法: {_class}.{func}, 消耗: {spend} ms'.format(
                #     _class=self.__class__.__name__, func=method.__name__, spend=spend))
                # return none when do not use gen.coroutine and return gen.Return(data) when gen.coroutine
                # refer tornado/web.py func:_execute() line:1540-1543
                return

        return wrapper
    return decorator


def do_api_cache(expire=60 * 5, with_user=True):
    """do cache for api handler"""
    return do_cache('api', expire=expire, with_user=with_user)


def do_temp_cache(expire=60 * 5, with_user=True):
    """do cache for template handler"""
    return do_cache('temp', expire=expire, with_user=with_user)


__all__ = ['do_api_cache', 'do_temp_cache']
