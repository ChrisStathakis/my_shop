LOCAL_CACHE = True
CACHES = ''

if LOCAL_CACHE:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'TIMEOUT': 60*60*24*30,
        }
    }