# -*- coding: utf-8 -*-
# @Project        : zadmin
# @version        : 1.0
# @Create Time    : 2024/12/7
# @File           : datatype.py
# @desc           : 数据类型

import datetime
from typing import Annotated, Union
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

from core.validator import vali_telephone, vali_email, datetime_str_vali, date_str_vali

# 实现自定义一个日期时间字符串的数据类型
DatetimeStr = Annotated[
    Union[str, datetime.datetime],
    AfterValidator(datetime_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

# 实现自定义一个手机号类型
Telephone = Annotated[
    str,
    AfterValidator(lambda x: vali_telephone(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

# 实现自定义一个邮箱类型
Email = Annotated[
    str,
    AfterValidator(lambda x: vali_email(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

# 实现自定义一个日期字符串的数据类型
DateStr = Annotated[
    Union[str, datetime.date],
    AfterValidator(date_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]
