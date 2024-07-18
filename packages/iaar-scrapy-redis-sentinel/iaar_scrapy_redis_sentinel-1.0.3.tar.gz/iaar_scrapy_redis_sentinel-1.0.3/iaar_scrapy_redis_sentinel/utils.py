# -*- coding: utf-8 -*-
import base64
import traceback
from hashlib import md5

import requests
import six
from iaar_scrapy_redis_sentinel import defaults, inner_ip, iaar_log


def bytes_to_str(s, encoding="utf-8"):
    """Returns a str if a bytes object is given."""
    if six.PY3 and isinstance(s, bytes):
        return s.decode(encoding)
    return s


def make_md5(text):
    """
    make text to md5
    """

    return md5(str(text).encode('utf-8')).hexdigest()


def get_track_id(request):
    track_id = ''
    try:
        track_id = request.meta.get("track_id")
    except Exception:
        pass
    return track_id


def send_message2mq(queue_name, queue_data, priority=0, delay_seconds=""):
    """
    发送消息到指定队列
    """
    try:
        message = (base64.b64encode(queue_data.encode())).decode()
        form_data = {
            "message": message,
            "queueName": queue_name,
            "priority": priority,
            "delaySeconds": delay_seconds
        }
        r = requests.post(f"{defaults.MQ_HOST}/rest/ms/GemMQ/sendMessage", json=form_data)
    except:
        iaar_log.error(
            f"send message to mq error, queue_name: {queue_name}, inner ip: {inner_ip}, : {traceback.format_exc()}").tracker()


def pop_mq(queue_name):
    try:
        r = requests.get(defaults.POP_MESSAGE.format(queueName=queue_name), timeout=5)
        resp = r.json()
        if resp.get("error_code") == 0 and resp.get("data"):
            message = resp["data"]["message"]
            queue_data = base64.b64decode(message)
            return queue_data
    except:
        iaar_log.error(
            f"pop mq error, queue_name: {queue_name}, inner_ip: {inner_ip}, : {traceback.format_exc()}").tracker()


def create_queue(queue_name):
    try:
        r = requests.get(defaults.CREATE_QUEUE.format(queueName=queue_name), timeout=5)
        return r.json()
    except:
        iaar_log.error(
            f"create mq error, queue_name: {queue_name}, inner ip: {inner_ip},: {traceback.format_exc()}").tracker()
