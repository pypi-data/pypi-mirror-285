# -*- coding: UTF-8 -*-
# @Time : 2023/9/26 10:52 
# @Author : 刘洪波
import random
import time
import os
import base64
import pandas as pd

en = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
      'X', 'Y', 'Z']

numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

char_list = en + numbers


def generate_unique_id(random_str_len: int = 12):
    """
    生成伪unique_id，有极小的概率会生成相同的unique_id。不过这个概率很小可以忽略。
    :param random_str_len: 随机字符串的长度，默认值为12，不能小于8，该值过小会增大生成相同unique_id的概率，
                           也不建议过大，过大生成的unique_id的长度过长并且耗时增加
    :return:
    """
    if random_str_len > 8:
        random_str = ''.join(random.choices(char_list, k=random_str_len))
        return random_str + str(int(time.time() * 1000))
    else:
        raise ValueError('random_str_len is small, the probability of generating the same id is relatively high. '
                         'So random_str_len must be greater than 8')


class EUID(object):
    def __init__(self, namespace, euid_path: str = None, str_len: int = None):
        """
        初始化变量并获取number_id
        :param namespace: number_id 的 key
        :param euid_path: 保存number_id的文件，默认保存位置在工作目录下euuid.pkl，格式 { namespace: number_id }
        :param str_len: number_id 加上 随机生成str的长度，必须大于0，默认设置是12，不推荐设置过小，
                        过小会导致number_id的长度很快超过str_len，导致后续生成的unique_id长度变长
        """
        self.namespace = namespace
        self.number_id = 0
        self.data_dict = {}
        if str_len is None:
            self.str_len = 12
        elif str_len > 0:
            self.str_len = str_len
        else:
            raise ValueError('str_len must be greater than 0, it is set to 12 by default.')
        if euid_path:
            self.euid_path = euid_path
        else:
            self.euid_path = './euuid.pkl'
        if os.path.exists(self.euid_path):
            self.data_dict = pd.read_pickle(self.euid_path)
            n_id = self.data_dict.get(self.namespace)
            if n_id:
                self.number_id = n_id['number_id']
                if str_len is None:
                    self.str_len = n_id['str_len']

    def generate_unique_id(self):
        """ 生成unique_id """
        self.number_id += 1
        k = self.str_len - len(str(self.number_id))
        random_str = ''
        if k > 0:
            random_str = ''.join(random.choices(en, k=k))
        return str(self.number_id) + random_str + str(int(time.time() * 1000))

    def change_number_id(self, number_id: int = None):
        """
        更改并保存新的number_id
        :param number_id: 数字id，必须大于或等于 0
        :return:
        """
        one_dict = {'str_len': self.str_len}
        if number_id is None:
            one_dict['number_id'] = self.number_id
        elif number_id >= 0:
            one_dict['number_id'] = number_id
        else:
            raise ValueError('number_id must be greater than or equal to 0')
        self.data_dict[self.namespace] = one_dict
        pd.to_pickle(self.data_dict, self.euid_path)


def generate_unique_id_of_mark(mark: str or int = '', is_base64: bool = True):
    """
    生成带标记的unique_id，用于标识已知事物,
    :param mark: 标记信息
    :param is_base64: 结果是否经过base64编码
    :return:
    """
    mark = str(mark)
    random_str_len = 0 if len(mark) > 12 else 12 - len(mark)
    if random_str_len:
        random_str = ''.join(random.choices(char_list, k=random_str_len))
        res = mark + '#' + random_str + str(int(time.time() * 1000))
    else:
        res = mark + '#' + str(int(time.time() * 1000))
    if is_base64:
        return base64.b64encode(res.encode('utf-8')).decode('utf-8')
    return res
