# -*- coding: utf-8 -*-
# @Project        : Apartment-partner-server
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : __init__.py.py
# @desc           : 主配置文件
from core.exception import register_exception
from core.logger import get_logger

__all__ = [get_logger,register_exception]

