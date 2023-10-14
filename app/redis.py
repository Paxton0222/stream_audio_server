import redis
import time
import json

redis_conn: redis.StrictRedis = redis.StrictRedis(host="localhost",port=6379,db=0)

class RedisQueue:
    def add(self, room: str, data: dict):
        redis_conn.rpush(room, json.dumps(data))
    def pop(self, room: str, count: int | None = None):
        return redis_conn.lpop(room, count)
    def range(self, room: str, start: int = 0, end: int = -1) -> dict:
        return redis_conn.lrange(room, start, end)

class LockNotAcquiredError(Exception):
    pass

class RedisLock:
    def __init__(self, expire=1800, acquire_timeout=2):
        self.redis_conn: redis.StrictRedis = redis_conn
        self.expire = expire
        self.acquire_timeout = acquire_timeout

    def acquire(self, lock_name: str):
        end_time = time.time() + self.acquire_timeout
        while time.time() < end_time:
            lock = self.redis_conn.set(lock_name, 'locked', self.expire,nx=True)
            if lock:
                return True
            time.sleep(0.1)
        return False

    def release(self, lock_name: str):
        self.redis_conn.delete(lock_name)

    def extend(self, lock_name: str, additional_time: int):
        self.redis_conn.pexpire(lock_name, additional_time)

def get_redis_queue():
    return RedisQueue()

def get_redis_lock():
    return RedisLock()