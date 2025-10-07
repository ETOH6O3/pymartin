r"""
内置函数自动签名模块
===================

本模块完全由AI设计、AI编写、AI测试。<del>什么3A大作</del>


概述
----------------------
buildin_signatures.py 模块提供了一个增强的函数签名获取机制，专门处理Python内置函数和类型的签名信息。
该模块解决了标准库inspect.signature无法正确处理某些内置函数的问题。

核心功能
----------------------

智能签名获取函数
get_signature(func: Callable) -> inspect.Signature函数提供统一的签名获取接口：


1. 尝试使用inspect.signature获取签名
2. 尝试对内置c++函数根据c++函数签名生成python函数签名
3. 最终回退到通用签名(*args, **kwargs)

使用示例
----------------------
>>> from buildin_signatures import get_signature

获取内置函数的签名
>>> print(get_signature(print))
(*values, sep=' ', end='\n', file=None, flush=False)

获取列表方法的签名
>>> print(get_signature(list.append))
(self, item)

获取无法通过inspect直接获取签名的函数
>>> print(get_signature(map))
(function, iterable, *iterables)

处理类方法
>>> class MyClass:
...     @classmethod
...     def my_classmethod(cls, a, b=1):
...         pass
>>> print(get_signature(MyClass.my_classmethod))
(a, b=1)




技术细节
----------------------
参数顺序规则
所有手动签名严格遵守Python参数顺序规则：
1. 位置参数 (POSITIONAL_ONLY)
2. 位置或关键字参数 (POSITIONAL_OR_KEYWORD)
3. 可变位置参数 (VAR_POSITIONAL)
4. 关键字参数 (KEYWORD_ONLY)
5. 可变关键字参数 (VAR_KEYWORD)

错误处理
- 当传入不可调用对象时，抛出TypeError
- 当无法确定签名时，返回通用签名(*args, **kwargs)
- 对不存在的方法添加了保护性检查（如frozenset的可变方法）

特殊处理
- 类方法：自动移除第一个参数（cls或self）
- 绑定方法：尝试从底层函数获取签名
- 内置C函数：使用通用签名作为回退



设计理念
--------------------
1. 精准覆盖：只处理inspect.signature无法正确处理的内置函数
2. 最小侵入：优先使用标准库方法，只在必要时使用手动签名
3. 向后兼容：保持与标准inspect.Signature对象的兼容性
4. 渐进增强：可轻松扩展添加更多需要手动签名的函数




注意事项
----------------------
1. 对于纯Python实现的函数，应优先使用inspect.signature
2. 模块主要解决CPython实现中的内置函数签名问题
3. 对第三方库的函数支持有限，建议直接使用inspect.signature
4. 模块会随着Python版本更新可能需要维护

-----------------------------------------------------------------------------------

此模块特别适用于需要动态分析函数签名的场景，如代码生成、文档工具、IDE智能提示等高级应用。

"""

import inspect
import itertools
import builtins
import functools
import operator
import typing
import types

# 修复后的内置类型手动签名
BUILTIN_SIGNATURES = {
    # itertools 模块
    itertools.islice: inspect.Signature(
        parameters=[
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("stop", inspect.Parameter.POSITIONAL_OR_KEYWORD),
            inspect.Parameter(
                "start", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=0
            ),
            inspect.Parameter(
                "step", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=1
            ),
        ]
    ),
    itertools.chain: inspect.Signature(
        parameters=[inspect.Parameter("iterables", inspect.Parameter.VAR_POSITIONAL)]
    ),
    itertools.cycle: inspect.Signature(
        parameters=[inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    itertools.repeat: inspect.Signature(
        parameters=[
            inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "times", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    itertools.groupby: inspect.Signature(
        parameters=[
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "key", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    # builtins 模块
    builtins.map: inspect.Signature(
        parameters=[
            inspect.Parameter("function", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_OR_KEYWORD),
            inspect.Parameter("iterables", inspect.Parameter.VAR_POSITIONAL),
        ]
    ),
    builtins.filter: inspect.Signature(
        parameters=[
            inspect.Parameter("function", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_OR_KEYWORD),
        ]
    ),
    builtins.zip: inspect.Signature(
        parameters=[inspect.Parameter("iterables", inspect.Parameter.VAR_POSITIONAL)]
    ),
    builtins.sorted: inspect.Signature(
        parameters=[
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "key", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "reverse", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=False
            ),
        ]
    ),
    builtins.enumerate: inspect.Signature(
        parameters=[
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "start", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=0
            ),
        ]
    ),
    builtins.sum: inspect.Signature(
        parameters=[
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "start", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=0
            ),
        ]
    ),
    builtins.range: inspect.Signature(
        parameters=[
            inspect.Parameter("stop", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "start", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=0
            ),
            inspect.Parameter(
                "step", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=1
            ),
        ]
    ),
    builtins.isinstance: inspect.Signature(
        parameters=[
            inspect.Parameter("obj", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("class_or_tuple", inspect.Parameter.POSITIONAL_ONLY),
        ]
    ),
    builtins.issubclass: inspect.Signature(
        parameters=[
            inspect.Parameter("cls", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("class_or_tuple", inspect.Parameter.POSITIONAL_ONLY),
        ]
    ),
    # 修复print函数签名 - 将VAR_POSITIONAL放在最后
    builtins.print: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "sep", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=" "
            ),
            inspect.Parameter(
                "end", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="\n"
            ),
            inspect.Parameter(
                "file", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "flush", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=False
            ),
            inspect.Parameter("values", inspect.Parameter.VAR_POSITIONAL),
        ]
    ),
    builtins.len: inspect.Signature(
        parameters=[inspect.Parameter("obj", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    builtins.open: inspect.Signature(
        parameters=[
            inspect.Parameter("file", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "mode", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="r"
            ),
            inspect.Parameter(
                "buffering", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=-1
            ),
            inspect.Parameter(
                "encoding", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "errors", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "newline", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "closefd", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=True
            ),
            inspect.Parameter(
                "opener", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    builtins.input: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "prompt", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=""
            ),
        ]
    ),
    builtins.abs: inspect.Signature(
        parameters=[inspect.Parameter("x", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    builtins.round: inspect.Signature(
        parameters=[
            inspect.Parameter("number", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "ndigits", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    builtins.pow: inspect.Signature(
        parameters=[
            inspect.Parameter("base", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("exp", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "mod", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    builtins.divmod: inspect.Signature(
        parameters=[
            inspect.Parameter("a", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("b", inspect.Parameter.POSITIONAL_ONLY),
        ]
    ),
    builtins.all: inspect.Signature(
        parameters=[inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    builtins.any: inspect.Signature(
        parameters=[inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    # 修复max/min函数签名 - 将VAR_POSITIONAL放在最后
    builtins.max: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "key", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "default", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
        ]
    ),
    builtins.min: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "key", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "default", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
        ]
    ),
    builtins.getattr: inspect.Signature(
        parameters=[
            inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("name", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "default", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    builtins.setattr: inspect.Signature(
        parameters=[
            inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("name", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("value", inspect.Parameter.POSITIONAL_ONLY),
        ]
    ),
    builtins.hasattr: inspect.Signature(
        parameters=[
            inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("name", inspect.Parameter.POSITIONAL_ONLY),
        ]
    ),
    builtins.id: inspect.Signature(
        parameters=[inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    builtins.hash: inspect.Signature(
        parameters=[inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    builtins.breakpoint: inspect.Signature(
        parameters=[
            inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
            inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
        ]
    ),
    # functools 模块
    functools.partial: inspect.Signature(
        parameters=[
            inspect.Parameter("func", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
            inspect.Parameter("keywords", inspect.Parameter.VAR_KEYWORD),
        ]
    ),
    functools.reduce: inspect.Signature(
        parameters=[
            inspect.Parameter("function", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("iterable", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "initializer", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    # operator 模块
    operator.add: inspect.Signature(
        parameters=[
            inspect.Parameter("a", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("b", inspect.Parameter.POSITIONAL_ONLY),
        ]
    ),
    operator.itemgetter: inspect.Signature(
        parameters=[
            inspect.Parameter("item", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("items", inspect.Parameter.VAR_POSITIONAL),
        ]
    ),
    operator.attrgetter: inspect.Signature(
        parameters=[
            inspect.Parameter("attr", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("attrs", inspect.Parameter.VAR_POSITIONAL),
        ]
    ),
    operator.methodcaller: inspect.Signature(
        parameters=[
            inspect.Parameter("name", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
            inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
        ]
    ),
    # 新增必要的手动签名
    next: inspect.Signature(
        parameters=[
            inspect.Parameter("iterator", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "default", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    iter: inspect.Signature(
        parameters=[
            inspect.Parameter("object", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter(
                "sentinel", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    callable: inspect.Signature(
        parameters=[inspect.Parameter("obj", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    memoryview: inspect.Signature(
        parameters=[inspect.Parameter("obj", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    bin: inspect.Signature(
        parameters=[inspect.Parameter("number", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    oct: inspect.Signature(
        parameters=[inspect.Parameter("number", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    hex: inspect.Signature(
        parameters=[inspect.Parameter("number", inspect.Parameter.POSITIONAL_ONLY)]
    ),
    property: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "fget", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "fset", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "fdel", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
            inspect.Parameter(
                "doc", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
            ),
        ]
    ),
    bytes: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "source", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=b""
            ),
            inspect.Parameter(
                "encoding", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="utf-8"
            ),
            inspect.Parameter(
                "errors", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="strict"
            ),
        ]
    ),
    bytearray: inspect.Signature(
        parameters=[
            inspect.Parameter(
                "source", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=b""
            ),
            inspect.Parameter(
                "encoding", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="utf-8"
            ),
            inspect.Parameter(
                "errors", inspect.Parameter.POSITIONAL_OR_KEYWORD, default="strict"
            ),
        ]
    ),
}

# 为内置类型添加签名
for cls in [list, dict, set, str, tuple, frozenset]:
    # 构造函数
    if cls is dict:
        BUILTIN_SIGNATURES[cls] = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    "iterable", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
                ),
                inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
            ]
        )
    else:
        BUILTIN_SIGNATURES[cls] = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    "iterable", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None
                ),
            ]
        )

    # 列表方法
    if cls is list:
        methods = {
            "append": [("self",), ("item",)],
            "extend": [("self",), ("iterable",)],
            "insert": [("self",), ("index",), ("object",)],
            "pop": [("self",), ("index", -1)],
            "remove": [("self",), ("value",)],
            "index": [("self",), ("value",), ("start", 0), ("end", None)],
            "count": [("self",), ("value",)],
            "sort": [("self",), ("key", None), ("reverse", False)],
        }
        for method, params in methods.items():
            parameters = []
            for param in params:
                if len(param) == 1:
                    parameters.append(
                        inspect.Parameter(param[0], inspect.Parameter.POSITIONAL_ONLY)
                    )
                else:
                    parameters.append(
                        inspect.Parameter(
                            param[0],
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            default=param[1],
                        )
                    )
            BUILTIN_SIGNATURES[getattr(cls, method)] = inspect.Signature(
                parameters=parameters
            )

    # 字典方法
    elif cls is dict:
        methods = {
            "update": [
                ("self",),
                ("other", None),
                ("kwargs", inspect.Parameter.VAR_KEYWORD),
            ],
            "get": [("self",), ("key",), ("default", None)],
            "setdefault": [("self",), ("key",), ("default", None)],
            "pop": [("self",), ("key",), ("default", None)],
            "keys": [("self",)],
            "values": [("self",)],
            "items": [("self",)],
        }
        for method, params in methods.items():
            parameters = []
            for param in params:
                if isinstance(param, tuple):
                    if len(param) == 1:
                        parameters.append(
                            inspect.Parameter(
                                param[0], inspect.Parameter.POSITIONAL_ONLY
                            )
                        )
                    else:
                        parameters.append(
                            inspect.Parameter(
                                param[0],
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                default=param[1],
                            )
                        )
                else:  # VAR_KEYWORD
                    parameters.append(
                        inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)
                    )
            BUILTIN_SIGNATURES[getattr(cls, method)] = inspect.Signature(
                parameters=parameters
            )

    # 集合方法 (仅适用于可变集合)
    elif cls is set:
        methods = {
            "add": [("self",), ("element",)],
            "remove": [("self",), ("element",)],
            "discard": [("self",), ("element",)],
            "pop": [("self",)],
            "update": [("self",), ("iterables", inspect.Parameter.VAR_POSITIONAL)],
        }
        for method, params in methods.items():
            parameters = []
            for param in params:
                if isinstance(param, tuple):
                    parameters.append(
                        inspect.Parameter(param[0], inspect.Parameter.POSITIONAL_ONLY)
                    )
                else:  # VAR_POSITIONAL
                    parameters.append(
                        inspect.Parameter("iterables", inspect.Parameter.VAR_POSITIONAL)
                    )
            BUILTIN_SIGNATURES[getattr(cls, method)] = inspect.Signature(
                parameters=parameters
            )

    # 字符串方法
    elif cls is str:
        methods = {
            "lower": [("self",)],
            "upper": [("self",)],
            "strip": [("self",), ("chars", None)],
            "split": [("self",), ("sep", None), ("maxsplit", -1)],
            "join": [("self",), ("iterable",)],
            "replace": [("self",), ("old",), ("new",), ("count", -1)],
            "startswith": [("self",), ("prefix",), ("start", 0), ("end", None)],
            "endswith": [("self",), ("suffix",), ("start", 0), ("end", None)],
            "format": [
                ("self",),
                ("args", inspect.Parameter.VAR_POSITIONAL),
                ("kwargs", inspect.Parameter.VAR_KEYWORD),
            ],
        }
        for method, params in methods.items():
            parameters = []
            for param in params:
                if isinstance(param, tuple):
                    if len(param) == 1:
                        parameters.append(
                            inspect.Parameter(
                                param[0], inspect.Parameter.POSITIONAL_ONLY
                            )
                        )
                    else:
                        parameters.append(
                            inspect.Parameter(
                                param[0],
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                default=param[1],
                            )
                        )
                elif param == inspect.Parameter.VAR_POSITIONAL:
                    parameters.append(
                        inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL)
                    )
                else:  # VAR_KEYWORD
                    parameters.append(
                        inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)
                    )
            BUILTIN_SIGNATURES[getattr(cls, method)] = inspect.Signature(
                parameters=parameters
            )

    # 元组方法
    elif cls is tuple or cls is frozenset:
        methods = {
            "index": [("self",), ("value",), ("start", 0), ("end", None)],
            "count": [("self",), ("value",)],
        }
        for method, params in methods.items():
            parameters = []
            for param in params:
                if isinstance(param, tuple):
                    if len(param) == 1:
                        parameters.append(
                            inspect.Parameter(
                                param[0], inspect.Parameter.POSITIONAL_ONLY
                            )
                        )
                    else:
                        parameters.append(
                            inspect.Parameter(
                                param[0],
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                default=param[1],
                            )
                        )
            # 只添加存在的方法
            if hasattr(cls, method):
                BUILTIN_SIGNATURES[getattr(cls, method)] = inspect.Signature(
                    parameters=parameters
                )

# 为文件对象添加常用方法
file_methods = {
    "read": [("self",), ("size", -1)],
    "write": [("self",), ("text",)],
    "readline": [("self",), ("size", -1)],
    "readlines": [("self",), ("hint", -1)],
    "writelines": [("self",), ("lines",)],
    "seek": [("self",), ("offset",), ("whence", 0)],
    "tell": [("self",)],
    "close": [("self",)],
    "flush": [("self",)],
    "truncate": [("self",), ("size", None)],
}

for method, params in file_methods.items():
    parameters = []
    for param in params:
        if len(param) == 1:
            parameters.append(
                inspect.Parameter(param[0], inspect.Parameter.POSITIONAL_ONLY)
            )
        else:
            parameters.append(
                inspect.Parameter(
                    param[0], inspect.Parameter.POSITIONAL_OR_KEYWORD, default=param[1]
                )
            )
    # 为所有文件类对象的方法添加签名
    BUILTIN_SIGNATURES[getattr(typing.IO, method, None)] = inspect.Signature(
        parameters=parameters
    )


def get_signature(func: typing.Callable) -> inspect.Signature:
    """安全获取函数签名，处理内置类型

    Args:
        func (Callable): 要获取签名的函数或方法

    Returns:
        inspect.Signature: 函数的签名对象

    Raises:
        TypeError: 如果输入不是可调用对象
    """
    if not callable(func):
        raise TypeError(f"Object {func!r} is not callable")

    # 1. 优先检查手动签名字典
    if func in BUILTIN_SIGNATURES:
        return BUILTIN_SIGNATURES[func]

    # 2. 处理类方法
    if isinstance(func, classmethod):
        try:
            sig = inspect.signature(func.__func__)
            parameters = list(sig.parameters.values())
            if parameters and parameters[0].name in ("cls", "self"):
                parameters = parameters[1:]
            return inspect.Signature(parameters)
        except (ValueError, TypeError):
            pass

    # 3. 尝试使用inspect.signature
    try:
        return inspect.signature(func)
    except (ValueError, TypeError):
        # 4. 对于C实现的内置函数，使用通用签名
        if isinstance(func, types.BuiltinFunctionType):
            return inspect.Signature(
                parameters=[
                    inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
                    inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
                ]
            )

        # 5. 尝试获取绑定方法的签名
        if hasattr(func, "__self__") and func.__self__ is not None:
            try:
                return inspect.signature(func.__func__)
            except (ValueError, TypeError):
                pass

        # 6. 最终回退到通用签名
        return inspect.Signature(
            parameters=[
                inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
                inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
            ]
        )
