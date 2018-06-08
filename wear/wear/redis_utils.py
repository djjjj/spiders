import redis


r_server = redis.Redis(host="qq-dev", password="kgl321``")


class RedisQueue(object):

    def __init__(self, spider_name, queue_name):
        self._spider = spider_name
        self._queue = queue_name

    @property
    def queue_name(self):
        return self._spider + ":" + self._queue

    def sadd(self, *values):
        r_server.sadd(self.queue_name, *values)

    def spop(self):
        return r_server.spop(self.queue_name)


user_queue = RedisQueue("www_wear_tw", "user_queue")
look_ids_queue = RedisQueue("www_wear_tw", "look_ids")
