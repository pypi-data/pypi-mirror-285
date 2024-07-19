# -*- coding: utf-8 -*-
import time

try:
    from collections import Iterable
except:
    from collections.abc import Iterable

from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider, CrawlSpider

from . import connection
from .utils import *

import json
from iaar_scrapy_redis_sentinel.utils import make_md5
from iaar_scrapy_redis_sentinel import inner_ip

import requests
import traceback


class RedisMixin(object):
    """Mixin class to implement reading urls from a redis queue."""
    tracker = ''
    queue_name = None  # rocket mq name
    rq_name = None  # rq, will be inited from rq_reaper crawler, has nothing to with none-reaper crawlers
    redis_key = None
    latest_queue = None
    redis_batch_size = None
    redis_encoding = None
    server = None  # 不可以改名，其他地方在用
    logger = iaar_log
    crawler_settings = None

    # Idle start time
    spider_idle_start_time = int(time.time())

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        return self.next_requests()

    def setup_redis(self, crawler=None):
        if self.server is not None:
            return

        if crawler is None:
            crawler = getattr(self, "crawler", None)

        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings
        self.crawler_settings = settings

        if self.redis_key is None:
            self.redis_key = settings.get("REDIS_START_URLS_KEY")

        self.redis_key = self.redis_key % {"name": self.name}

        # 使用了mq, 区分和生产队列名称
        if settings.getbool("MQ_USED"):
            self.redis_key = self.name
            self.queue_name = settings.get("QUEUE_NAME_PREFIX").format(self.name)
            self.logger.info(f"mq queue_name: {self.queue_name}, redis_key: {self.redis_key}").tracker()

        if not self.redis_key.strip():
            raise ValueError("redis_key must not be empty")

        if self.latest_queue is None:
            self.latest_queue = settings.get("LATEST_QUEUE_KEY")
        self.latest_queue = self.latest_queue % {"name": self.name}

        if self.redis_batch_size is None:
            # TODO: Deprecate this setting (REDIS_START_URLS_BATCH_SIZE).
            self.redis_batch_size = settings.getint("REDIS_START_URLS_BATCH_SIZE", settings.getint("CONCURRENT_REQUESTS"))

        try:
            self.redis_batch_size = int(self.redis_batch_size)
        except (TypeError, ValueError):
            raise ValueError("redis_batch_size must be an integer")

        if self.redis_encoding is None:
            self.redis_encoding = settings.get("REDIS_ENCODING")

        self.logger.info(f"Reading start URLs from redis {self.__dict__} ").tracker()

        self.server = connection.from_settings(crawler.settings)

        if self.crawler_settings.getbool("REDIS_START_URLS_AS_SET"):
            self.fetch_data = self.server.spop
            self.count_size = self.server.scard
        elif self.crawler_settings.getbool("REDIS_START_URLS_AS_ZSET"):
            self.fetch_data = self.pop_priority_queue
            self.count_size = self.server.zcard
        elif self.crawler_settings.getbool("MQ_USED"):  # 使用MQ
            if self.rq_name:
                self.count_size = self.get_queue_size
                self.logger.info(f'rq name: {self.rq_name} exists, not use uq any more. uq name {self.queue_name}.').tracker(self.tracker)
                crawler.signals.connect(self.check_queue, signal=signals.spider_opened)
            else:
                self.fetch_data = self.pop_batch_mq
                self.count_size = self.get_queue_size
                # 爬虫启动时，检查队列是否存在,不存在则创建
                crawler.signals.connect(self.check_queue, signal=signals.spider_opened)
        else:
            self.fetch_data = self.pop_list_queue
            self.count_size = self.server.llen

        # 爬虫启动时，会先从备份队列，取出任务(丢到队列中)
        crawler.signals.connect(self.spider_opened_latest_pop, signal=signals.spider_opened)

        # The idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)

    def check_queue(self):
        if not self.get_queue_size(self.queue_name):
            create_queue(self.queue_name)

    def check_redis(self):
        if not self.server or not self.server.ping():
            # 因长时间无操作等原因，中途可能链接中断
            self.server = connection.from_settings(self.crawler_settings)

    def pop_list_queue(self, redis_key, batch_size):
        with self.server.pipeline() as pipe:
            pipe.lrange(redis_key, 0, batch_size - 1)
            pipe.ltrim(redis_key, batch_size, -1)
            datas, _ = pipe.execute()
        return datas

    def get_queue_size(self, redis_key):
        try:
            msg_name = self.queue_name
            if self.rq_name:
                msg_name = self.rq_name
            r = requests.get(self.crawler_settings.get("GET_QUEUE_SIZE").format(queueName=msg_name), timeout=5)
            return int(r.json()['data']['queueSize'])
        except:
            self.logger.error(f"crawler: {self.name}, inner ip: {inner_ip}, get mq queue size error: {traceback.format_exc()}").tracker()

    def pop_batch_mq(self, redis_key, batch_size):
        datas = []
        for i in range(batch_size):
            queue_data = pop_mq(self.queue_name)
            if queue_data:
                datas.append(queue_data)
        return datas

    def pop_priority_queue(self, redis_key, batch_size):
        with self.server.pipeline() as pipe:
            pipe.zrevrange(redis_key, 0, batch_size - 1)
            pipe.zremrangebyrank(redis_key, -batch_size, -1)
            datas, _ = pipe.execute()
        return datas

    def latest_queue_mark(self, datas):
        # 删除之前存的消息， 再把pop出来的消息，存到redis中（reaper除外）
        self.server.hdel(self.latest_queue, inner_ip)
        latest_datas = []
        for data in datas:
            latest_datas.append(bytes_to_str(data))
        self.server.hset(self.latest_queue, inner_ip, json.dumps(latest_datas))
        self.logger.info(f"crawler: {self.name}, latest_queue_mark, inner_ip: {inner_ip}, latest_datas: {latest_datas}").tracker()

    def spider_opened_latest_pop(self):
        """绑定spider open信号； 取出 stop spider前，最后1次datas"""
        if self.server.hexists(self.latest_queue, inner_ip):
            latest_datas = self.server.hget(self.latest_queue, inner_ip)
            self.server.hdel(self.latest_queue, inner_ip)
            for data in json.loads(bytes_to_str(latest_datas)):
                if self.crawler_settings.getbool("MQ_USED"):
                    if self.rq_name:
                        send_message2mq(self.rq_name, queue_data=str(data), priority=1)
                    else:
                        send_message2mq(queue_name=self.queue_name, queue_data=str(data), priority=1)
                else:
                    self.server.lpush(self.redis_key, json.dumps(data, ensure_ascii=False))

    def next_requests(self):
        """Returns a request to be scheduled or none."""
        if self.rq_name:
            rq_size = self.get_queue_size(self.rq_name)
            if rq_size > 0:
                # 模拟爬虫 make_request 的过程, 用 uuid 防止被认为是重复消息
                datas = [item for item in range(self.redis_batch_size)]
            else:
                datas = []
                time.sleep(1)
                self.logger.info(f'result queue size is 0, waiting for crawler, queue name: {self.rq_name}, crawler name: {self.name}').tracker()
        else:
            datas = self.fetch_data(self.redis_key, self.redis_batch_size)
            self.latest_queue_mark(datas)

        for data in datas:
            self.tracker = make_md5(str(data))
            # 处理 mq 并发重复(不处理rq)
            if not self.rq_name:
                if self.crawler_settings.getbool("MQ_USED"):
                    if self.server.exists(self.tracker):
                        self.logger.info(f"crawler: {self.name}, mq repetition, track_id: {str(data)[:50]}").tracker(self.tracker)
                        continue
                    else:
                        # 所有消息放到redis中，设置失效时间为 1 分钟
                        # （1分钟内不能重复消费同一个md5值的数据）
                        self.server.set(str(data), "1", ex=60 * 1)

            reqs = self.make_request_from_data(data)
            if not self.rq_name:
                # not print log when processing reaper data (reaper data here is fake )
                self.logger.info(f"crawler: {self.name}, make request from data, queue_data: {str(data)}").tracker(self.tracker)

            if isinstance(reqs, Iterable):
                for req in reqs:
                    yield req
            elif reqs:
                yield reqs
            else:
                self.logger.info(f"request was not made, crawler: {self.name}").tracker()

    def make_request_from_data(self, data):
        url = bytes_to_str(data, self.redis_encoding)
        return self.make_requests_from_url(url)

    def schedule_next_requests(self):
        """Schedules a request if available"""
        # TODO: While there is capacity, schedule a batch of redis requests.
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        """
        Schedules a request if available, otherwise waits.
        or close spider when waiting seconds > MAX_IDLE_TIME_BEFORE_CLOSE.
        MAX_IDLE_TIME_BEFORE_CLOSE will not affect SCHEDULER_IDLE_BEFORE_CLOSE.
        """
        if self.server is not None and self.count_size(self.redis_key) > 0:
            self.spider_idle_start_time = int(time.time())

        self.schedule_next_requests()

        max_idle_time = self.crawler_settings.getint("MAX_IDLE_TIME_BEFORE_CLOSE")
        idle_time = int(time.time()) - self.spider_idle_start_time
        if max_idle_time != 0 and idle_time >= max_idle_time:
            return
        raise DontCloseSpider


class RedisSpider(RedisMixin, Spider):
    """    notes in git history, not show     """

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj


class RedisCrawlSpider(RedisMixin, CrawlSpider):
    """    notes in git history, not show     """

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisCrawlSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj
