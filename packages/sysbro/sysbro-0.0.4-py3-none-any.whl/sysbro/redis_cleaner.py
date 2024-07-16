import redis
from tqdm import tqdm


def clean_idle_redis_keys(redis_host='localhost', redis_port=6379, db=0, startswithkey=None, idletime=604800):
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=db)
    for key in tqdm(r.scan_iter("*")):
        idle = r.object("idletime", key)
        if idle > idletime and (startswithkey is None or key.startswith(startswithkey)):
            print("Deleting {}".format(key))
            r.delete(key)
