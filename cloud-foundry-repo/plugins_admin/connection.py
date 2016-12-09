import os
import redis
import json
from plugin_exceptions import RedisNotAvailable

# Get Redis credentials
if 'VCAP_SERVICES' in os.environ:
    services = json.loads(os.getenv('VCAP_SERVICES'))
    redis_env = services['rediscloud'][0]['credentials']
else:
    redis_env = dict(hostname='localhost', port=6379, password='')
redis_env['host'] = redis_env['hostname']
del redis_env['hostname']
redis_env['port'] = int(redis_env['port'])

# Connect to redis
try:
    db = redis.StrictRedis(**redis_env)
    db.info()
except redis.ConnectionError:
    raise RedisNotAvailable
