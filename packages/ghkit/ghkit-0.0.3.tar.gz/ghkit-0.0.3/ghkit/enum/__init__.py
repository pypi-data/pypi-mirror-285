from enum import Enum
from typing import Any


class GEnum(Enum):
    """枚举基类"""

    def __new__(cls, value: Any, desc: Any = None):
        """

        :param value: 枚举成员的值
        :param desc: 枚举成员的描述信息
        """
        if issubclass(cls, str):
            obj = str.__new__(cls, value)
        elif issubclass(cls, int):
            obj = int.__new__(cls, value)
        else:
            obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj
