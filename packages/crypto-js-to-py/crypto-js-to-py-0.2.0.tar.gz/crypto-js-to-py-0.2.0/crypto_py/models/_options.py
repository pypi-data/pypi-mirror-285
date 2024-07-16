 # -*- coding: utf-8 -*-
# -------------------------------

# @IDE：PyCharm
# @Python：3.1x
# @Project：DP

# -------------------------------

# @fileName：_aes_options.py
# @createTime：2024/7/3 9:52
# @author：Primice

# -------------------------------
from pydantic import BaseModel, Field
from typing import Optional, Type
from ..pad.pad import Pad


class Options(BaseModel):
    mode: int
    padding: Type[Pad]
    iv: Optional[bytes | str] = Field(default=None)
