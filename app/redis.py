from app.env import env_vars
import redis
import time
import json

redis_conn: redis.StrictRedis = redis.StrictRedis(
    host=env_vars["REDIS_HOST"], port=env_vars["REDIS_PORT"], db=0)


class RedisQueue:
    def add(self, room: str, data: dict):
        redis_conn.rpush(room, json.dumps(data))

    def pop(self, room: str, count: int | None = None):
        return redis_conn.lpop(room, count)

    def first(self, room: str):
        return redis_conn.lindex(room, 0)

    def range(self, room: str, start: int = 0, end: int = -1) -> dict:
        return redis_conn.lrange(room, start, end)

    def length(self, room: str) -> int:
        return redis_conn.llen(room)

    def clean(self, room: str) -> None:
        redis_conn.ltrim(room, 1, 0)
        redis_conn.delete(room)


class RedisLock:
    def __init__(self, acquire_timeout=1):
        self.redis_conn: redis.StrictRedis = redis_conn
        self.acquire_timeout = acquire_timeout

    def acquire(self, lock_name: str, expire: int):
        end_time = time.time() + self.acquire_timeout
        while time.time() < end_time:
            lock = self.redis_conn.set(lock_name, 'locked', expire, nx=True)
            if lock:
                return True
            time.sleep(0.1)
        return False

    def release(self, lock_name: str):
        self.redis_conn.delete(lock_name)

    def extend(self, lock_name: str, additional_time: int):
        self.redis_conn.pexpire(lock_name, additional_time)


class RedisMap:
    def __init__(self):
        self.redis_client: redis.StrictRedis = redis_conn

    def set(self, key, field, value):
        self.redis_client.hset(key, field, value)

    def get(self, key, field):
        return self.redis_client.hget(key, field)

    def get_all(self, key):
        return self.redis_client.hgetall(key)

    def exists(self, key, field):
        return self.redis_client.hexists(key, field)

    def delete(self, key, field):
        self.redis_client.hdel(key, field)

    def keys(self, key):
        return self.redis_client.hkeys(key)

    def values(self, key):
        return self.redis_client.hvals(key)

    def length(self, key):
        return self.redis_client.hlen(key)


def get_redis_queue():
    return RedisQueue()


def get_redis_lock():
    return RedisLock()


def get_redis_map():
    return RedisMap()
