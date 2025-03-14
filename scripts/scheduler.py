# -*- coding: utf-8 -*-
# @Project        : Apartment-partner-server
# @version        : 1.0
# @Create Time    : 2025/2/15
# @File           : initialize.py
# @desc           : 主配置文件
import os
import subprocess

from config.settings import BASE_DIR

VIRTUAL_ENV_PATH = BASE_DIR + '/.venv/bin'


def queue():
    # 启动消息队列
    queue_args = [VIRTUAL_ENV_PATH + 'celery', '--app', 'schedule', 'worker', '-l', 'INFO', '-E', '-P', 'eventlet']
    subprocess.check_call(queue_args, cwd=BASE_DIR)


def crontab():
    # 启动定时任务
    cron_args = [VIRTUAL_ENV_PATH + 'celery', '--app', 'schedule', 'beat', "-l", "INFO"]
    subprocess.check_call(cron_args, cwd=BASE_DIR)
