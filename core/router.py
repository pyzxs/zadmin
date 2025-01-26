# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/1/25
# @File           : router.py
# @desc           : 主配置文件
from fastapi import FastAPI


def get_all_routes(app: FastAPI):
    @app.get("/system/routes", name="获取系统路由",include_in_schema=False)
    async def get_routes():

        grouped_routes = {}
        for route in app.routes:
            if exclude_routes(route.path):
                continue
            methods = list(route.methods) if hasattr(route, 'methods') else ['*']
            tags = getattr(route.endpoint, '__fastapi__tags__', getattr(route, 'tags', []))

            for tag in tags:
                if tag not in grouped_routes:
                    # 如果该标签还没有在字典中出现，则初始化一个空列表
                    grouped_routes[tag] = []
                # 将当前路由添加到对应标签的列表中
                for method in methods:
                    grouped_routes[tag].append({
                        "path": route.path,
                        "name": route.name,
                        "method": method
                    })
        return grouped_routes


def exclude_routes(path: str):
    exclued_routes = ['/openapi.json', '/docs', '/redoc', '/docs/oauth2-redirect', '/routes', '/media',
                      '/user/api/login', '/user/login', '/']
    if path in exclued_routes:
        return True
    return False
