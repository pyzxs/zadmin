# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/7
# @File           : development.py
# @desc           : 测试服配置

"""
Mysql 数据库配置项
连接引擎官方文档：https://www.osgeo.cn/sqlalchemy/core/engines.html
数据库链接配置说明：mysql+asyncmy://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称
"""
ASYNC_SQLALCHEMY_DATABASE_URL = "mysql+asyncmy://root:123456@127.0.0.1:3306/zadmin?charset=utf8mb4"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/zadmin?charset=utf8mb4"


"""
阿里云对象存储OSS配置
阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
 *  [accessKeyId] {String}：通过阿里云控制台创建的AccessKey。
 *  [accessKeySecret] {String}：通过阿里云控制台创建的AccessSecret。
 *  [bucket] {String}：通过控制台或PutBucket创建的bucket。
 *  [endpoint] {String}：bucket所在的区域， 默认oss-cn-hangzhou。
"""
ALIYUN_OSS = {
    "accessKeyId": "accessKeyId",
    "accessKeySecret": "accessKeySecret",
    "endpoint": "endpoint",
    "bucket": "bucket",
    "baseUrl": "baseUrl"
}


"""
redis作为缓存使用
格式："redis://:密码@地址:端口/数据库名称"
"""

CACHE_DB_ENABLE = True
CACHE_DB_URL = "redis://:123456@127.0.0.1:6379/0"
CACHE_EXPIRE = 60 * 60 * 24 * 7


"""
消息队列及定时任务处理,需要以下安装包
redis 地址 https://github.com/redis/redis-py
celery https://docs.celeryq.dev/

安装方式
pip install redis
pip install celery
pip install eventlet
"""
SCHEDULE_ENABLE = True
SCHEDULE_BROKER_URL = 'redis://:123456@127.0.0.1:6379/0'
SCHEDULE_RESULT_URL = 'redis://:123456@127.0.0.1:6379/1'
SCHEDULE_RESULT_EXPIRE = 60 * 60 * 24

"""
获取IP地址归属地
文档：https://user.ip138.com/ip/doc
"""
IP_PARSE_ENABLE = False
IP_PARSE_TOKEN = "IP_PARSE_TOKEN"