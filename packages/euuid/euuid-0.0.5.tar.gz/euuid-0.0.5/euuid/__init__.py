# -*- coding: UTF-8 -*-
# @Time : 2023/9/26 10:52 
# @Author : 刘洪波
from euuid.generate_id import generate_unique_id, generate_unique_id_of_mark

euuid = generate_unique_id
euuid3 = generate_unique_id_of_mark


def euuid2(namespace, euid_path: str = None, str_len: int = None):
    from euuid.generate_id import EUID
    return EUID(namespace, euid_path, str_len)
