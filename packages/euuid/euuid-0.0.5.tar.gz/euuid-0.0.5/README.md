[ 中文 | [English](README_EN.md) ]

# euuid

python生成uuid(通用唯一识别码)总共有5种方法。这个包提供了另外三个方法生成uuid，是对uuid的python包补充。

## 安装

    pip install euuid


## 原理
- 第一种方法 euuid ： uuid = 随机字符串 + 时间戳， 有可以被忽略不计的概率生成重复的id
  - 随机字符串是从英文字母和数字里随机抽取n个组成的字符串，数字n默认为12，也可自定义。数字n默认为12时每毫秒会出现重复的概率为 1/4738381338321616896，由于概率极小可认为每次生成的id是不重复的。
  - 时间戳取毫秒
- 第二种方法 euuid2 ： uuid = 自增数字id + 随机字符串 + 时间戳， 可以生成完全不重复的id
  - 自增数字id : 0, 1, 2, 3, ... , n
  - 随机字符串是从英文字母里随机抽取的字符串，其长度等于输入的数量减自增数字id的字符长度。随着自增数字id的字符长度变大，随机字符串的长度会变成0

- 第三种方法 euuid3 ： uuid = 自定义标记字符串 + # + 随机字符串 + 时间戳， 可以生成完全不重复的id
  - 随机字符串是从英文字母和数字里随机抽取n个组成的字符串，若自定义标记字符串的长度大于等于12则随机字符串为空，反之随机字符串的长度等于12减自定义标记字符串的长度
  - 默认返回base64编码后的数据

## 使用
### euuid
```python3
from euuid import euuid

print(euuid())
```

### euuid2
```python3
from euuid import euuid2

# 初始化类，输入自增数字的namespace
# 默认自增数字id的保存位置是当前目录，文件名euuid.pkl, 也可以自定义
# 自定义：   euid = euuid2('test', './test.pkl') 
euid = euuid2('test')
# 打印开始的自增数字id
print(euid.number_id)

# 打印自增数字id 加上 随机生成str的长度, 默认是12，也可以自定义
print(euid.str_len)

# 输出10个uuid
for i in range(10):
    print(euid.generate_unique_id())
# 保存自增后的数字id
euid.change_number_id()
```
### euuid3
```python3
from euuid import euuid3

# 默认返回base64编码后的数据
print(euuid3('panda'))

# 返回未经base64编码后的数据
print(euuid3('panda', is_base64=False))
```


