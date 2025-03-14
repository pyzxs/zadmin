# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2025/1/27
# @File           : main.py
# @desc           : 主配置文件
import os

from sqlalchemy import insert, text

from config.settings import BASE_DIR
from core.database import get_sync_db


class Migration:
    SCRIPT_DIR = os.path.join(BASE_DIR, 'scripts', 'initialize')

    def __get_data(self, table_name):
        """
        获取sql内容
        :param table_name：表名
        """
        filename = os.path.join(self.SCRIPT_DIR,'sql',table_name, '.sql')
        with open(filename, 'r') as f:
            return f.read()

    async def __generate_data(self, table_name: str):
        """
        生成数据

        :param table_name: 表名
        :param model: 数据表模型
        """
        async_session = get_sync_db()
        db = await async_session.__anext__()
        sql = self.__get_data(table_name)
        await db.execute(text(sql))
        await db.flush()
        await db.commit()
        print(f"{table_name} 表数据已生成")

    async def run(self):
        await self.__generate_data('roles')
        await self.__generate_data('casbin_runs')
        print('数据表迁移完成')