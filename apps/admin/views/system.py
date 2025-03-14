# -*- coding: utf-8 -*-
# @Project        : Apartment-partner-server
# @version        : 1.0
# @Create Time    : 2025/2/12
# @File           : views.py
# @desc           : 主配置文件
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from apps.admin.logics import system

systemAPI = APIRouter()