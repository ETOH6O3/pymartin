r"""

管道运算工具 (Pipe Operator Implementation)
===================

提供一种优雅的函数链式调用方式，解决传统管道库的三大痛点：
1. 难以自动处理单元素 / 多元素返回值
2. 支持自动解包传参和参数包动态修改
3. 无需手动封装标准库函数

快速入门
--------
基础使用：
>>> from pipe import pipe
>>>
>>> # 数值处理流水线
>>> (pipe (10)
...  | (lambda x: x * 2)
...  | (lambda x: x + 5)
...  | print)  # 输出 25
25
>>>
>>> # 字符串处理链
>>> text = "HELLO, World!"
>>> clean_text = (pipe (text)
...              | str.strip
...              | str.lower
...              | str.capitalize
...              ).get ()
>>> print (clean_text)  # "Hello, world!"
Hello, world!

多参数处理：
>>> import operator
>>>
>>> # 多参数传递
>>> (pipe (3, 5)
...  | operator.add     # 3+5=8
...  | extend (2)        # 添加参数：8,2
...  | operator.sub     # 8-2=6
...  | print)           # 输出 6
6

核心功能
--------
管道入口：
- pipe (*pos_args, **kwargs): 创建管道起点
- .get (): 获取最终结果

参数包操作：
>>> # 开头添加参数
>>> (pipe (5)
...  | prepend (3)
...  | operator.sub
...  | print)  # 3-5=-2
-2
>>>
>>> # 删除位置参数
>>> (pipe (1, 2, 3)
...  | delete (1)
...  | print)  # 删除索引 1 的元素 (2)
(1, 3)

+----------------------+----------------------------------+---------------------------------------------+
| 函数                 | 描述                             | 示例                                        |
+----------------------+----------------------------------+---------------------------------------------+
| extend (*args, **kwargs) | 追加参数                         | pipe (1) | extend (2) | add → 3                 |
+----------------------+----------------------------------+---------------------------------------------+
| prepend (*values)     | 开头添加参数                     | pipe (5) | prepend (3) | sub → -2               |
+----------------------+----------------------------------+---------------------------------------------+
| insert (index, *values) | 指定位置插入参数                 | pipe (1,3) | insert (1,2) | print → 1 2 3     |
+----------------------+----------------------------------+---------------------------------------------+
| delete (index)        | 删除指定位置参数                 | pipe (1,2,3) | delete (1) | print → 1 3        |
+----------------------+----------------------------------+---------------------------------------------+
| set_kwarg (key, value) | 设置关键字参数                   | pipe (x=1) | set_kwarg ('y',2) | func               |
+----------------------+----------------------------------+---------------------------------------------+
| del_kwarg (key)       | 删除关键字参数                   | pipe (x=1,y=2) | del_kwarg ('x') | func              |
+----------------------+----------------------------------+---------------------------------------------+

解包控制：
>>> import os
>>> # 解包返回值示例
>>> (pipe ("/home/user/file.txt")
...  | unpack_return_values ()  # 启用解包
...  | os.path.split          # 返回 (dirname, filename) 并解包
...  | delete (0)              # 删除目录名
...  | print)                 # 打印文件名
'file.txt'

方法调用：
>>> (pipe ("test.txt")
...  | open
...  | get_mtd ("read")  # 调用 TextIOWrapper.read ()
...  | print)

管道迭代器适配器
------------
基础适配器：
>>> # 过滤偶数
>>> (pipe (range (10))
...  | pfilter (lambda x: x % 2 == 0)
...  | list
...  | print)
[0, 2, 4, 6, 8]
>>>
>>> # 元素平方
>>> (pipe (range (5))
...  | ptransform (lambda x: x**2)
...  | list
...  | print)
[0, 1, 4, 9, 16]

+------------------------+---------------------------+---------------------------------+
| 适配器                 | 等效操作                  | 描述                            |
+------------------------+---------------------------+---------------------------------+
| pfilter (pred)           | pfilter (pred, iter)        | 过滤不符合条件的元素            |
+------------------------+---------------------------+---------------------------------+
| ptransform (func)        | map (func, iter)           | 对每个元素应用转换函数          |
+------------------------+---------------------------+---------------------------------+
| pslice (start, stop, step) | itertools.islice (iter, start, stop, step) | 迭代器切片操作      |
+------------------------+---------------------------+---------------------------------+
| ptake (n)                | itertools.islice (iter, n) | 取前 n 个元素                     |
+------------------------+---------------------------+---------------------------------+
| ptakewhile (pred)        | itertools.takewhile (pred, iter) | 取满足条件的连续元素      |
+------------------------+---------------------------+---------------------------------+
| pdrop (n)                | itertools.islice (iter, n, None) | 跳过前 n 个元素               |
+------------------------+---------------------------+---------------------------------+
| pdropwhile (pred)        | itertools.dropwhile (pred, iter) | 跳过满足条件的连续元素      |
+------------------------+---------------------------+---------------------------------+

高级适配器：
>>> # 相邻元素差值计算
>>> (pipe (range (5))
...  | padjacent_transform (lambda a,b: b-a)
...  | list
...  | print)
[1, 1, 1, 1]
>>> #
>>> # 分块处理
>>> (pipe (range (10))
...  | pchunk (3)
...  | list
...  | print)
[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
>>> #
>>> # 滑动窗口
>>> (pipe (range (5))
...  | pslide (3)
...  | list
...  | print)  # [[0,1,2], [1,2,3], [2,3,4]]
>>> #
>>> # 条件分组
>>> data = [1, 0, 0, 1, 1, 0]
>>> (pipe (data)
...  | pchunk_by (lambda x: x == 0)
...  | list
...  | print)  # [[1], [0,0], [1,1], [0]]

+------------------------+---------------------------------------+-----------------------------------------+
| 适配器                 | 等效操作                              | 描述                                    |
+------------------------+---------------------------------------+-----------------------------------------+
| padjacent               | itertools.pairwise (iter)              | 生成相邻元素的元组                      |
+------------------------+---------------------------------------+-----------------------------------------+
| padjacent_transform (func) | (func (a,b) for a,b in pairwise (iter)) | 对每对相邻元素应用转换函数               |
+------------------------+---------------------------------------+-----------------------------------------+
| pchunk (size)            | 分块生成器                            | 将可迭代对象分割为固定大小的块           |
+------------------------+---------------------------------------+-----------------------------------------+
| pchunk_by (pred)         | 条件分组生成器                        | 根据谓词函数对连续元素进行分组           |
+------------------------+---------------------------------------+-----------------------------------------+
| pcounted (count)         | 有限生成器                            | 从迭代器当前位置生成指定数量的元素       |
+------------------------+---------------------------------------+-----------------------------------------+
| lazy_psplit (delimiter)  | 惰性分割器                            | 按分隔符分割可迭代对象为子列表           |
+------------------------+---------------------------------------+-----------------------------------------+
| pslide (n)               | 滑动窗口生成器                        | 生成长度为 n 的滑动窗口（每次滑动 1 元素）   |
+------------------------+---------------------------------------+-----------------------------------------+
| pstride (step)           | itertools.islice (iter, None, None, step) | 以指定步长对可迭代对象进行切片           |
+------------------------+---------------------------------------+-----------------------------------------+

高级功能
--------
PipeAdapter 装饰器：
将多参数函数转换为单参数管道传递兼容的单参数函数
>>> @PipeAdapter (1)# 保留 iterable 参数位置
... def custom_filter (func, iterable):
...     return filter (func, iterable)
>>>
>>> (pipe (range (10))
...  | custom_filter (lambda x: x % 2 == 0)
...  | list
...  | print)
[0, 2, 4, 6, 8]

实际应用场景
--------

文件词频统计：
>>> import re
>>> from collections import Counter
>>>
>>> (pipe ("data.txt")
...  | open
...  | get_mtd ("read")  # 调用 TextIOWrapper.read ()
...  | str.lower
...  | prepend (r"\w+")  # 作为 re.findall 第一个参数
...  | re.findall
...  | Counter
...  | print)

作者
--------
孙鸣淼

更新日志
--------
- 1.0 版本 6/24 完成核心类_PipeWrapper，实现初步的参数包修改。
- 2.0 版本 6/25 支持关键词解包传参。
            加入操纵类_PipeManiper 和相关函数以实现精细操纵。
- 2.1 版本 6/27 完善管道操纵函数。完善注释。
- 2.2 版本 6/28 修改管道操纵函数使之更加方便。完善注释。
- 3.0 版本 7/1 管道适配器初步。函数修饰器 PipeAdapter。
- 3.1 版本 7/4 迭代器参数管道适配器
- 3.2 版本 7/14 更多迭代器参数管道适配器
- 3.3 版本 7/15 修 bug。完善文档。
- 3.4 版本 8/17 适配器统一前缀 'p'，解决命名污染问题。

"""

import typing
import enum
import builtins
import functools
import itertools

from . import buildin_signatures
class _PipeAttr(enum.StrEnum):
    """_PipeWrapper 的三个属性"""

    POS_ARGS = "_pos_args"
    KWARGS_DICT = "_kwargs_dict"
    UNPACK_RETURN_VALUE = "_unpack_return_values"

    def __repr__(self):
        return f"{self.name}"


class _BoolOperation(enum.Enum):
    """对单一布尔值的四种操作：
    不变、置位、复位、翻转
    """

    NO_CHANGE = lambda x, y, z: x
    RESET = lambda x, y, z: False
    SET = lambda x, y, z: True
    TOGGLE = lambda x, y, z: not x

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}.{self.name}"


class _ArgsOperation(enum.Enum):
    """对参数包的四种操作：
    不变、修改值、删除值、插入值
    """

    @typing.overload
    def __del_item(kargs: dict, key: any, not_enabled) -> dict: ...

    @typing.overload
    def __del_item(args, index, not_enabled) -> tuple: ...

    def __del_item(args, index_or_key, not_enabled) -> tuple:
        if isinstance(args, tuple):
            return args[:index_or_key] + args[index_or_key + 1 :]
        elif isinstance(args, dict):
            del args[index_or_key]
            return args
        else:
            raise TypeError(f"args 非参数包，实际类型：{type (args)}")

    @typing.overload
    def __set_item(kargs: dict, key: any, value) -> dict: ...

    @typing.overload
    def __set_item(args: tuple, index: int, *values) -> tuple: ...

    def __set_item(args, index_or_key, *values) -> tuple:
        if isinstance(args, tuple):
            return (
                args[:index_or_key] + tuple(*values) + args[index_or_key + len(args) :]
            )
        elif isinstance(args, dict):
            args[index_or_key] = values[0]

        else:
            raise TypeError(f"args 非参数包，实际类型：{type (args)}")

    @typing.overload
    def __insert_item(kargs: dict, key: any, value) -> dict: ...

    @typing.overload
    def __insert_item(args: tuple, index: int, *values) -> tuple: ...

    def __insert_item(args, index_or_key, *values) -> tuple:
        if isinstance(args, tuple):
            return args[:index_or_key] + tuple(*values) + args[index_or_key:]
        elif isinstance(args, dict):
            args.update({index_or_key: values[0]})
            return args
        else:
            raise TypeError(f"args 非参数包，实际类型：{type (args)}")

    NO_CHANGE = lambda args, not_enabled1, not_enabled2: args
    DEL_ITEM = __del_item
    SET_ITEM = __set_item
    INSERT_ITEM = __insert_item

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}.{self.name}"


class _PipeManiper:
    """
    管道操纵类，携带操纵方式等信息。

    设计风格一定程度的借鉴了汇编码。

    原理是 _PipeWrapper 对象 |_PipeManiper 对象 将会根据后者携带的信息更改前者的属性。

    Attributes:
        protected:
            _modify_target (_PipeAttr): 欲修改的属性名称 \n
            _modify_operation (_BoolOperation|_ArgsOperation): 修改方式 \n
            _index: 修改位置参数时：参数索引, 修改关键词参数时：关键词, 其它：未启用 \n
            _values：修改位置参数时：参数包, 修改关键词参数时：一个参数, 其它：未启用
        public:
            无
        private:
            无

    """

    @typing.overload
    def __init__(
        self,
        modify_target: typing.Literal[_PipeAttr.UNPACK_RETURN_VALUE],
        modify_operation: _BoolOperation,
        not_enabled1=0,
        *not_enabled2,
    ): ...

    @typing.overload
    def __init__(
        self,
        modify_target: typing.Literal[_PipeAttr.POS_ARGS],
        modify_operation: _ArgsOperation,
        index: int,
        *values,
    ): ...

    @typing.overload
    def __init__(
        self,
        modify_target: typing.Literal[_PipeAttr.KWARGS_DICT],
        modify_operation: _ArgsOperation,
        key: str,
        value: typing.Any = None,
    ): ...

    def __init__(
        self,
        modify_target: _PipeAttr,
        modify_operation: _BoolOperation | _ArgsOperation,
        index: int = 0,
        *values,
    ):
        """
        构造函数。

        Args:
            modify_target (_PipeAttr): 欲修改的属性名称
            modify_operation (_BoolOperation | _ArgsOperation): 修改方式
            index (int, optional): 修改位置参数时：参数索引, 修改关键词参数时：关键词, 其它：未启用
            *values: 修改位置参数时：参数包, 修改关键词参数时：一个参数, 其它：未启用

        """
        self._modify_target = modify_target
        self._modify_operation = modify_operation
        self._index = index
        if modify_target == _PipeAttr.KWARGS_DICT:
            self._values = values[0] if values else None
        else:
            self._values: tuple = values

    def __repr__(self):
        return f"_PipeManiper ({self._modify_target},{self._modify_operation.__repr__()},{self._index},{self._values})"


def unchange():
    r"""
    看上去什么用也没有的函数。<del > 实际上什么用也没有 </del>。
    也许你可以用它来水代码。

    Examples:

        >>> pipe ("阿富汗塔利班")|unchange ()|print #美国在阿富汗速通版
        阿富汗塔利班
        >>> #相当于：
        >>> pipe ("阿富汗塔利班")| setitem (0, "临时政府")| setitem (0, "民族团结政府") \
        ... | setitem (0, "阿富汗塔利班")| print #美国在阿富汗完整版
        阿富汗塔利班 
    """
    return _PipeManiper(_PipeAttr.POS_ARGS, _ArgsOperation.NO_CHANGE)


def insert(index: int, *values) -> _PipeManiper:
    r"""
    管道传递过程中在指定位置插入位置参数。

    Args:
        index (int): 要插入的位置索引。
        *values: 要插入的参数值，可以传入多个。

    Returns:
        _PipeManiper: 携带操纵信息。

    Examples:
        >>> (
        ...     pipe ("测试输出.txt")
        ...     | open
        ...     | get_mtd ("read")  # 相当于 TextIOWrapper.read ()
        ...     | str.lower
        ...     | insert (0, r"\w+") # 等同于 prepend (r"\w+")
        ...     | re.findall
        ...     | Counter
        ...     | print
        ... )

    """
    return _PipeManiper(_PipeAttr.POS_ARGS, _ArgsOperation.INSERT_ITEM, index, *values)


def set_args(index: int, *values):
    r"""
    管道传递过程中从指定位置开始替换若干位置参数。

    Args:
        index (int): 要修改的起始位置索引。
        *values: 修改后的参数值。

    Returns:
        _PipeManiper: 携带操纵信息。

    """
    return _PipeManiper(_PipeAttr.POS_ARGS, _ArgsOperation.SET_ITEM, index, *values)


def delete(index: int) -> _PipeManiper:
    """
    管道传递过程中删除指定位置的位置参数

    Args:
        index (int): 要删除的位置参数的索引。

    Returns:
        _PipeManiper: 携带操纵信息。

    Examples:
        >>> import os
        >>> (
        ...     pipe ('/home/user/file1.txt')
        ...     | pack_return_values () #启用返回值解包
        ...     | os.path.split
        ...     | delete (0) #丢弃目录名
        ...     | print #打印文件名
        ... )
        file1.txt
    """
    return _PipeManiper(_PipeAttr.POS_ARGS, _ArgsOperation.DEL_ITEM, index)


def del_kwarg(key: str) -> _PipeManiper:
    """管道传递过程中根据关键词删除关键词参数"""
    return _PipeManiper(_PipeAttr.KWARGS_DICT, _ArgsOperation.DEL_ITEM, key)


def set_kwarg(key: str, value: typing.Any) -> _PipeManiper:
    """管道传递过程中修改一个关键词参数"""
    return _PipeManiper(_PipeAttr.KWARGS_DICT, _ArgsOperation.SET_ITEM, key, value)


def unpack_return_values() -> _PipeManiper:
    """在下一次管道传递解包函数多返回值"""
    return _PipeManiper(_PipeAttr.UNPACK_RETURN_VALUE, _BoolOperation.SET)


def pack_return_values() -> _PipeManiper:
    """取消 unpack_return_values 的作用"""
    return _PipeManiper(_PipeAttr.UNPACK_RETURN_VALUE, _BoolOperation.RESET)


class _PipeWrapper:
    """
    管道运算核心类

    Attributes:
        protected:
            参数包：\n
            _pos_args (tuple): 将要位置传参给函数的参数包，以元组形式保存 \n
            _kwargs_dict (dict): 将要关键词传参给函数的参数包，以字典形式保存 \n
            解包控制：\n
            _unpack_return_values (bool): 控制函数返回元组时是否解包返回值 \n
            它将会在每次管道传递中的复原
        public:
            无
        private:
            无

    Methods:

        | 运算符 : 连接函数调用或追加参数
        get ()    : 获取处理结果

    Notes:
        1. 避免直接使用 _PipeWrapper 对象 以及 | _PipeManiper 对象
           来进行操纵，这样暴露了细节，而且降低了代码的可读性
           本模块提供的函数足以满足使用需求

        2. 直接使用该类创建管道入口暴露了细节，
           更好的办法是使用 pipe 函数。
    """

    def __init__(
        self,
        *pos_args,
        **kwargs,
    ):
        """

        Args:
            *pos_args (any): 任意数量的位置参数，这些参数打包给_PipeWrapper 对象存储的位置参数包。
            **kwargs (any): 任意数量的关键词参数，这些参数打包给_PipeWrapper 对象存储的关键字参数包。

        """

        self._pos_args: tuple = pos_args
        self._kwargs_dict: dict = kwargs
        # 控制属性复位
        self._unpack_return_values = False

    def __repr__(self) -> str:
        return f"_PipeWrapper {self._pos_args+(self._kwargs_dict,)}"

    def __or__(
        self, other: typing.Callable | "_PipeWrapper" | _PipeManiper
    ) -> "_PipeWrapper":
        """
        对参数包中的值位置参数解包给函数，并返回函数返回值的_PipeWrapper。
        或者修改参数包以及控制解包方式

        Args:
        \r
            other: 有三种允许的类型
            管道传递（由用户使用）：
            1. 要调用的函数或函数对象，该函数的参数应与实例中存储的参数数量相同，
            （根据__unpack_return_values 决定是否解包返回值）。
            管道操纵（不建议用户直接使用）：（应当由 extend () 等间接使用）
            2. 一个_PipeWrapper 对象，该对象的参数包将会追加给 self 的参数包
            （在关键词参数后不得追加位置参数）
            3. 一个_PipeManiper 对象，将根据它携带的信息修改_PipeWrapper 的属性

        Returns:
            调用后：一个新的_PipeWrapper（_PipeManiper 修改的属性复原）
            操纵后：修改后的_PipeWrapper（之前修改的属性保留）

        Raises:
            SyntaxError: 已经存在关键词参数的情况下追加位置参数
            TypeError: 不支持的操作类型

        Examples:

            >>> import operator
            >>> pipe (3) | operator.neg | (lambda x: x**2) | (lambda x: x // 2) | print
            4
            >>> text = "Hello, World!"
            >>> clean_text = (pipe (text) | str.strip | str.lower | str.capitalize).get ()
            >>> print (clean_text)
            Hello, world!
        """
        if isinstance(other, _PipeWrapper):
            # 合并两个_PipeWrapper 的参数包
            if bool(other._pos_args) and bool(self._kwargs_dict):
                raise SyntaxError("在关键词参数后不得追加位置参数")
            else:
                self._pos_args = self._pos_args + other._pos_args
                self._kwargs_dict.update(other._kwargs_dict)
                return self
        elif isinstance(other, typing.Callable):
            # 调用函数并包装结果
            if self._unpack_return_values:
                # 解包返回值
                return _PipeWrapper(
                    *other(*self._pos_args, **self._kwargs_dict),
                )
            else:
                # 不拆包返回值（作为单个参数）
                return _PipeWrapper(
                    other(*self._pos_args, **self._kwargs_dict),
                )
        elif isinstance(other, _PipeManiper):
            # 执行管道操纵
            setattr(
                self,
                other._modify_target.value,  # 被修改属性名
                other._modify_operation(  # 这是个 lambda，恒传入三个参数（可能用不上）
                    getattr(
                        self,
                        other._modify_target.value,
                    ),  # 获取属性，作为 lambda 表达式的参数
                    other._index,  # 若修改参数包则启用
                    other._values,  # 若修改参数包则启用
                ),
            )
            return self
        else:
            raise TypeError(
                f"other 必须是可调用对象、_PipeWrapper 对象或_PipeManiper，实际类型为 {type (other).__name__}"
            )

    def get(self) -> typing.Any:
        """
        获取存储的值。

        Returns:
            如果 参数包 为空，则返回 None。
            如果 参数包 中只有一个元素，则返回该元素。
            否则返回 参数包 本身，即一个元组。

        Examples:

            >>> Pipe1 = pipe (3,5)
            >>> print (Pipe1.get ())
            (3, 5)
            >>> pipe (5).get ()
            5
        """
        # 合并位置参数和关键词参数
        args = self._pos_args + tuple(self._kwargs_dict.items())

        if len(args) == 0:
            return None
        elif len(args) == 1:
            return args[0]
        else:
            return args


def pipe(*pos_args: any, **kargs: any) -> _PipeWrapper:
    """
    创建管道入口

    Args:
        *pos_args: 初始位置参数
        **kargs: 初始关键字参数

    Returns:
        _PipeWrapper: 管道包装对象

    Examples:
        >>> import operator
        >>> pipe (3) | operator.neg | (lambda x: x**2) | (lambda x: x // 2) | print
        4
    """
    return _PipeWrapper(*pos_args, **kargs)


def extend(*pos_args, **kargs) -> _PipeWrapper:
    """
    在管道运算中追加参数。已经存在关键词参数时不可追加位置参数。

    原理是当使用 `|` 操作符将两个 `_PipeWrapper` 对象连接时，
    后一个 `_PipeWrapper` 对象的参数包会被追加到前一个 `_PipeWrapper` 对象上。

    Args:
        *pos_args (any): 追加的位置参数。
        **kargs (any): 追加的关键字参数。

    Returns:
        _PipeWrapper: 将追加的参数打包成的_PipeWrapper 对象。


    示例：
        >>> import operator
        >>> pipe (3, 5) | operator.add | extend (8) | operator.sub | print
        0

    """
    return _PipeWrapper(*pos_args, **kargs)


def update_kwargs(**kwargs) -> _PipeManiper:
    """
    追加多个关键词参数。
    """
    return _PipeWrapper(**kwargs)


def prepend(*values) -> _PipeManiper:
    """
    用于在管道运算中在位置参数包开头添加位置参数。

    原理是 _PipeWrapper 对象 |_PipeManiper 对象 将根据后者携带的信息修改_PipeWrapper 的属性。

    Args:
        *values (any): 你要添加的参数

    Returns:
        _PipeManiper: 携带操纵信息

    Examples:
        >>> import operator
        >>> pipe (5,3)|operator.add|prepend (3)|operator.sub|print
        -5

    """
    return insert(0, *values)


def get_mtd(method_name: str, *values) -> typing.Callable[[typing.Any], typing.Any]:
    r"""
    动态调用对象方法
    即在管道传递中根据成员方法名自动调用对应的函数。

    没错，你根本不需要知道参数的类型，你只要知道它有这个成员方法就行了。

    <del>get_mtd 是这样的，用户只要知道成员方法名就行了，而作者考虑的可就多了 </del>

    Args:
        method_name (str): 需要调用的成员方法名。
        *values (tuple): 传递给成员方法的参数。

    Returns:
        function: 一个匿名函数，该函数接受一个对象作为参数，并调用该对象的指定方法。

    Examples:
        >>> (
        ...     pipe ("测试输出.txt")
        ...     | open
        ...     | get_mtd ("read")  # 相当于 TextIOWrapper.read ()
        ...     | str.lower
        ...     | prepend (r"\w+")  # 等同于 insert (0, r"\w+")
        ...     | re.findall
        ...     | Counter
        ...     | print
        ... )
    """
    return lambda obj: getattr(obj, method_name)(*values)


def PipeAdapter(index: int = -1, param: typing.Optional[str] = None):
    """
    函数修饰器工厂，返回一个函数修饰器，创建保留指定参数的 partial 函数。
    经过修饰后的函数将成为单参数管道适配器。

    Args:
        index (int, optional): 要被排除的参数位置索引，从 0 开始，负数表示从末尾计数。默认为 - 1。
        param (str, optional): 要被排除的参数名称。默认为 None。与 index 同时指定时，若 index 为默认值则以 param 为准，否则抛出异常。

    Returns:
        decorator: 返回用于修饰目标函数的修饰器函数。

    Raises:
        ValueError: 当同时指定了 index 和 param 时引发。
        ValueError: 当指定的 param 不在函数签名中时引发。
        IndexError: 当指定的 index 超出函数参数范围时引发。
        TypeError: 当向 wrapper 意外传入要排除的参数时引发。
        TypeError: 当应用 PipeAdapter 时缺少必需参数时引发。

    """
    if index != -1 and param is not None:
        raise ValueError("index 和 param 不能同时指定")

    # 使用闭包保存原始参数值
    _index = index
    _param = param

    def decorator(func: typing.Callable):
        # 安全获取函数签名
        sig = buildin_signatures.get_signature(func)
        params = list(sig.parameters.values())
        total_params = len(params)

        # 使用闭包中的值
        index = _index
        param = _param

        # 确定要保留的参数名称和位置
        if param is not None:
            # 通过参数名查找
            param_names = [p.name for p in params]
            if param not in param_names:
                raise ValueError(f"参数 '{param}' 不存在")
            exclude_param = param
            exclude_index = param_names.index(param)
        else:
            # 通过索引定位
            if index < 0:
                index = total_params + index
            if not 0 <= index < total_params:
                raise IndexError(
                    f"参数索引 {index} 超出范围，函数只接受 {total_params} 个参数"
                )
            exclude_index = index
            exclude_param = params[index].name

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查是否意外传入了要保留的参数
            if exclude_param in kwargs:
                raise TypeError(f"意外传入了被排除的参数 '{exclude_param}'")

            # 创建部分应用的函数
            def partial_func(excluded_arg):
                # 准备最终调用参数
                final_args = []
                final_kwargs = kwargs.copy()

                # 重建参数列表，插入被排除的参数
                arg_iter = iter(args)
                arg_count = 0

                for i, param_obj in enumerate(params):
                    if i == exclude_index:
                        # 插入被排除的参数
                        final_args.append(excluded_arg)
                        continue

                    param_name = param_obj.name

                    # 如果参数已通过关键字提供
                    if param_name in final_kwargs:
                        continue

                    # 尝试从位置参数获取
                    if arg_count < len(args):
                        try:
                            value = next(arg_iter)
                            final_args.append(value)
                            arg_count += 1
                            continue
                        except StopIteration:
                            pass

                    # 处理可变位置参数
                    if param_obj.kind == param_obj.VAR_POSITIONAL:
                        # 对于 * args 参数，不需要额外处理
                        continue

                    # 检查是否有默认值
                    if param_obj.default is not param_obj.empty:
                        # 有默认值，不需要提供
                        continue

                    # 必需的参数缺失
                    raise TypeError(
                        f"参数缺失: {param_name}，"
                        f"需要的参数为: {[p.name for p in params if p.default is p.empty and p.kind != p.VAR_POSITIONAL]}"
                    )

                # 添加剩余的关键字参数
                return func(*final_args, **final_kwargs)

            return partial_func

        return wrapper

    return decorator


pfilter = PipeAdapter(1)(builtins.filter)
"""
内置 filter 的管道适配器
对上一次管道传递的返回值（如果是可迭代对象）过滤

Args:
    pred (predicate): 过滤条件函数，符合则保留

Examples:
    >>> pipe1 = (
    ...     pipe (range (0, 1000))
    ...     | pfilter (lambda x: x % 4 == 0)
    ...     | pfilter (lambda x: x % 15 == 0)
    ...     | pfilter (lambda x: x % 40 == 0)
    ...     )
    >>> for num in pipe1.get ():
    ...    print (num, end=" ")
    0 120 240 360 480 600 720 840 960
"""

ptransform = PipeAdapter(1)(builtins.map)
"""
内置 map 的管道适配器
对上一次管道传递的返回值（如果是可迭代对象）的所有元素应用指定函数

Args:
    func (Callable [[any],any]): 对元素应用的指定函数

Examples:
    >>> pipe1 = (
    ...     pipe (range (0, 1000))
    ...     | pfilter (lambda x: x % 4 == 0)
    ...     | pfilter (lambda x: x % 15 == 0)
    ...     | ptransform (lambda x: x + 2)
    ...     )
    >>> for num in pipe1.get ():
    ...    print (num, end=" ")
    2 62 122 182 242 302 362 422 482 542 602 662 722 782 842 902 962
"""

pslice = PipeAdapter(0)(itertools.islice)
"""
内置 islice 的管道适配器
在管道传递中切片上一次管道传递的返回值（如果是可迭代对象）

Args:
    1. 一个参数:pslice (stop)
        stop: 终止值（不包含）
    2. 两 / 三个参数:pslice (start,stop [, step])
        start: 起始值，stop: 终止值 (None 代表取到结尾)，step: 步长（左闭右开）

Examples:
    >>> pipe1 = (
    ...     pipe (range (0, 1000))
    ...     | pfilter (lambda x: x % 4 == 0)
    ...     | pfilter (lambda x: x % 15 == 0)
    ...     | ptransform (lambda x: x + 2)
    ...     | pslice (3,8)
    ...     | list
    ...     | print
    ...     )
    [182, 242, 302, 362, 422]
"""


def ptake(n):
    """
    在管道传递中取上一次管道传递的返回值（如果是可迭代对象）的前 n 个元素 \n
    与 pslice (n) 作用完全相同

    Args:
        n (int):

    Examples:
    >>> pipe1 = (
    ...     pipe (range (0, 1000))
    ...     | pfilter (lambda x: x % 4 == 0)
    ...     | pfilter (lambda x: x % 15 == 0)
    ...     | ptransform (lambda x: x + 2)
    ...     | ptake (2)
    ...     | list
    ...     | print
    ...     )
    [2, 62]

    """
    return pslice(n)


ptakewhile = PipeAdapter()(itertools.takewhile)
"""
内置 takewhile 的管道适配器
在管道传递中取上一次管道传递的返回值（如果是可迭代对象）的前若干个元素，\n
直到谓词首次失败

Args:
    pred (predicate): 判断元素是否符合条件的谓词

Examples:
>>> pipe1 = (
...     pipe (range (0, 1000))
...     | pfilter (lambda x: x % 4 == 0)
...     | pfilter (lambda x: x % 15 == 0)
...     | ptransform (lambda x: x + 2)
...     | ptakewhile (lambda x: x<300)
...     | list
...     | print
...     )
[2, 62, 122, 182, 242]

"""


def pdrop(n):
    """
    跳过上一次管道传递的返回值（如果是可迭代对象）前 N 个元素 \n
    与 pslice (n,None) 作用完全相同

    Args:
        n (int):

    Returns:
        iterator: 迭代切片后的元素

    Examples:
    >>> pipe1 = (
    ...     pipe (range (0, 1000))
    ...     | pfilter (lambda x: x % 4 == 0)
    ...     | pfilter (lambda x: x % 15 == 0)
    ...     | ptransform (lambda x: x + 2)
    ...     | pdrop (2)
    ...     | list
    ...     | print
    ...     )
    [122, 182, 242, 302, 362, 422]

    """
    return pslice(n, None)


pdropwhile = PipeAdapter()(itertools.dropwhile)
"""
对上一次管道传递的返回值（如果是可迭代对象）跳过直到谓词首次失败的元素

Args:
    pred (predicate): 判断元素是否符合条件的谓词

Examples:
>>> pipe1 = (
...     pipe (range (0, 1000))
...     | pfilter (lambda x: x % 4 == 0)
...     | pfilter (lambda x: x % 15 == 0)
...     | ptransform (lambda x: x + 2)
...     | ptakewhile (lambda x: x<300)
...     | list
...     | print
...     )
[2, 62, 122, 182, 242]

"""


@PipeAdapter(0)
def lazy_psplit(iterable, delimiter):
    """
    惰性地将上一次管道传递的返回值（如果是可迭代对象）按分隔符分割成多个子列表。

    Args:
        delimiter: 分隔符，用于分割可迭代对象。

    Yields:
        list: 分割后的每一个子列表。

    Examples:
        >>> pipe ([1, ",", 2, ",", 3]) | lazy_psplit (",") | list | print
        [[1], [2], [3]]

    """
    current_segment = []
    for item in iterable:
        if item == delimiter:
            if current_segment:
                yield current_segment
                current_segment = []
        else:
            current_segment.append(item)
    if current_segment:
        yield current_segment


@PipeAdapter(0)
def pcounted(iterator, count):
    """
    从上一次管道传递的返回值（如果是迭代器）的当前位置开始生成指定数量的元素。

    Args:
        count (int): 要从迭代器中生成元素的数量。

    Yields:
        any: 从迭代器中生成的元素。

    Examples:
        >>> iter1 = iter ([1,2,3,4,5,6,7,8,9])
        >>> next (iter1)
        1
        >>> pipe (iter1)|pcounted (3)|list|print
        [2, 3, 4]
    """

    for not_enabled in range(count):
        try:
            yield next(iterator)
        except StopIteration:
            break


padjacent = itertools.pairwise
"""
内置 pairwise 的管道适配器
用于生成上一次管道传递的返回值（如果是可迭代对象）中相邻元素的元组。

Args:
    iterable (Iterable): 要生成相邻元素的可迭代对象。

Yields:
    tuple [Any, Any]: 包含相邻元素的元组。

Example:
    >>> list (padjacent ([1, 2, 3, 4, 5]))
    [(1, 2), (2, 3), (3, 4), (4, 5)]
"""


@PipeAdapter(0)
def padjacent_transform(iterable, func):
    """
    对上一次管道传递的返回值（如果是可迭代对象）中的每相邻两个元素应用指定的函数。

    Args:
        func (callable): 对相邻元素应用的函数，该函数应接受两个参数并返回一个结果。

    Examples:
        >>> (
        ...     pipe (range (0, 1000))
        ...     | pfilter (lambda x: x % 4 == 0)
        ...     | pfilter (lambda x: x % 15 == 0)
        ...     | ptransform (lambda x: x + 2)
        ...     | pslice (8)   #包含：2, 62, 122, 182, 242, 302, 362, 422
        ...     | padjacent_transform (lambda x,y: y+x)
        ...     | list
        ...     | print
        ... )
        [64, 184, 304, 424, 544, 664, 784]
    """
    return (func(a, b) for a, b in padjacent(iterable))


@PipeAdapter(0)
def pchunk(iterable, size):
    """
    将上一次管道传递的返回值（如果是可迭代对象）分割成大小为 size 的块。

    Args:
        size: 每个块的大小。

    Returns:
        generator: 产生大小为 size 的块。

    Examples:
        >>> (
        ...     pipe (range (0, 100))
        ...     | pfilter (lambda x: x % 4 == 0)
        ...     | pslice (8)
        ...     | pchunk (2)
        ...     | list
        ...     | print
        ...)
        [[0, 4], [8, 12], [16, 20], [24, 28]]
    """
    it = iter(iterable)
    while True:
        chunk = list(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk


@PipeAdapter(0)
def pslide(iterable, n):
    """
    滑动窗口的生成器。将将上一次管道传递的返回值（如果是可迭代对象）分割为长度为 n 的滑动窗口（每次向后滑动一个元素）。

    Args:
        n: 窗口大小。

    Yields:
        list: 一个长度为 n 的窗口。

    Examples:
        >>> pipe ([1, 2, 3, 4, 5]) | pslide (3) | list | print
        [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    """
    it = iter(iterable)
    window = []
    for item in it:
        window.append(item)
        if len(window) == n:
            yield list(window)
            window.pop(0)


@PipeAdapter(0)
def pchunk_by(iterable, pred):
    """
    根据给定的谓词函数，将上一次管道传递的返回值（如果是可迭代对象）分割为多个子列表。

    Args:
        pred (Callable): 用于判断分割点的谓词函数。当谓词函数对某元素返回 True 时，开始新的分组。

    Yields:
        List: 按谓词分割后的子列表。

    Examples:
        >>> pipe ([1, 2, 0, 3, 0, 4]) | pchunk_by (lambda x: x == 0) |list | print
        [[1, 2], [0], [3], [0], [4]]

    """
    group = []
    for item in iterable:
        meet_cond = pred(item)
        # 如果这是第一个元素或者条件改变了，开始新的组
        if not group or meet_cond != pred(group[0]):
            if group:
                yield group
            group = [item]
        else:
            group.append(item)
    if group:
        yield group


@PipeAdapter(0)
def pstride(iterable, step):
    """
    对上一次管道传递的返回值（如果是可迭代对象）进行步长为 step 的切片操作。

    Args:
        step (int): 切片的步长。

    Yields:
        any: 步长为 step 的切片结果。

    Examples:
        >>> (pipe (range (10))
        ...  | pstride (2)
        ...  | list
        ...  | print)
        [0, 2, 4, 6, 8]
    """
    return itertools.islice(iterable, None, None, step)


def main():
    """管道操作使用演示"""

    import operator
    import re
    from io import TextIOWrapper
    from collections import Counter
    import os

    # 数值计算流水线
    pipe(3) | operator.neg | (lambda x: x**2) | (lambda x: x // 2) | print
    # 多参数管道操作
    pipe(3, 5) | operator.add | extend(8) | operator.sub | print
    # 字符串处理链
    text = "Hello, World!"
    clean_text = (pipe(text) | str.strip | str.lower | str.capitalize).get()
    print(clean_text)
    # 单词计数
    if False:  # 改为 True 启用
        (
            pipe("测试输出.txt")
            | open
            | get_mtd("read")  # 相当于 TextIOWrapper.read ()
            | str.lower
            | prepend(r"\w+")  # 等同于 insert (0, r"\w+")
            | re.findall
            | Counter
            | print
        )
    # 文件路径操作
    (
        pipe("/home/user/file1.txt")
        | unpack_return_values()  # 启用返回值解包
        | os.path.split
        | update_kwargs(sep=",")
        | print  # 打印文件名
    )

    # 构建 URL
    def build_url(base_url: str, **params) -> str:
        """构建带查询参数的 URL"""
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query}" if query else base_url

    (
        pipe("https://api.example.com/data")  # 基础 URL 作为位置参数
        | update_kwargs(page=1, limit=10, verbose=True, sort="desc")
        | del_kwarg("verbose")  # 删除 verbose 参数
        | update_kwargs(page=2)  # 修改 page 参数
        | build_url  # 构建完整 URL
        | print  # 输出结果
    )

    # 可迭代类型操作流水线
    pipe1 = (
        pipe(range(0, 100))
        | pfilter(lambda x: x % 4 == 0)
        | pslice(8)
        | pslide(3)
        | list
        | print
    )

    # 幽默的示例：美国在阿富汗
    (
        pipe("阿富汗塔利班")
        | set_args(0, "临时政府")
        | set_args(0, "民族团结政府")
        | set_args(0, "阿富汗塔利班")
        | print
    )


if __name__ == "__main__":
    main()
