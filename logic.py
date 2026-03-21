"""
逻辑函数模块 Logic Function Module
===

面向解题的逻辑函数一条龙化简服务

使用经典的奎恩-麦克拉斯基化简算法，支持面向对象的逻辑函数封装，提供完整的逻辑函数表示和可视化分析化简功能。

快速上手
---

1. Logic[WIDTH] 逻辑信号类

- 严格的位宽检查
- 泛型支持，尽可能确保类型安全
- 支持位运算、无符号数算术运算
- 容器接口（索引、切片、迭代）
- 天然不可变，确保数值安全

>>> # 多种构造方式
>>> signal1 = Logic[8]()           # 默认构造
>>> signal1 # __repr__ 和 __str__ 方法输出表示形式高位在前
Logic(0)
>>> str(signal1)
0b0
>>> signal2 = Logic[8](True, True, True, False)   # 布尔值构造, 低位在前
>>> signal3 = Logic[8]('11010010') # 字符串构造，高位在前
>>> signal4 = Logic[8](8, width=5)        # 整型构造 5 位逻辑信号
>>> signal5 = Logic[8]([True, False, True, False]) # 容器构造, 低位在前
>>> # 支持无符号运算和位运算
>>> signal1 or signal2 # 逻辑运算，位数不变
Logic(0b0111)
>>> signal4 + signal4 # 加法运算，含进位信号
Logic(0b010000)
>>> signal4 - signal4 # 减法运算，位数不变
Logic(0b00000)
>>> signal4 * signal4 # 乘法运算，位数相加
Logic(0b0001000000)
>>> signal4 // signal4 # 除法运算，位数不变
Logic(0b00001)
>>> # 容器方法
>>> signal2[0] # 下标访问，返回布尔值
True
>>> signal2[0:4:2] # 切片访问，返回新的 Logic
Logic(0b11)
>>> *signal2 # 解包
True, True, True, False
>>> signal2[0]  = True # Logic 为不可变类型，不支持下标赋值、切片赋值、就地运算
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
    import platform
    ^^^^^^^^^^
TypeError: 'Logic' object does not support item assignment
>>> # 示例： 打印 RS 锁存器的时序转换到文件
>>> with open("RS时序转换.txt", "w") as f:
...     print(
...         "++++++++++++++++++++++++++++++RS 锁存器 ( NAND 实现 )++++++++++++++++++++++++++++++++++++++",
...         file=f,
...     )
...     for i in range(4):
...         R, S = Logic[2](i, 2)  # 解包，等价于 assign {R,S} = i (verilog)
...         print(f"\\n === R={R},S={S} ===", file=f)
...         for j in range(4):
...             Q, Qn = Logic[2](j, 2)
...             print(f"\\nInitial Q={Q},Qn={Qn}\\n", file=f)
...             for i in range(3):
...                 print(f"t{i} Q={Q},Qn={Qn} => ", end="", file=f)
...                 Q, Qn = not (R and Qn), not (
...                     S and Q
...                 )  # python 的非阻塞赋值， 相当于 Q <= R ~& Qn; Qn <= S ~& Q; (verilog)
...                 print(f" Q={Q},Qn={Qn}", file=f)

2. FmtLogicFunction[input_width,output_width] 逻辑函数封装类

- 全自动封装函数对象
- 全自动位宽解析与检查
- 全自动可视化化简流程
- 全自动格式化输入输出

>>> # ==================== 使用 python 语法描述逻辑 ====================
>>> def encoder(IN: Logic[4]) -> Logic[2]: # 自动格式化依赖于完整的类型注解，输入类型必须标明位宽
...         \"\"\"4 - 2 位低位优先编码器\"\"\"
...         for i in range(0, 4): # 内部实现面向结果就好啦
...             if IN[i]:
...                 return Logic[2](i, 2)
...         return Logic[2](0, 2) # 输出位宽必须确保恒定，否则会出现意想不到的错误
...
>>> # ==================== 封装为函数对象，自动加入位宽检查功能 ====================
>>> wrapped_encoder = FmtLogicFunction[4, 2](encoder)
>>> wrapped_encoder(Logic[4]("1111")) # 像原来一样调用
Logic (00)
>>> try: # 尝试传入位宽与类型注解相违背的参数
...     wrapped_encoder(Logic[2](2))
... except Exception as e:
...     print(e)
...
输入位宽不匹配，期望 4，实际 2
>>> # ==================== 自动化简流水线 ====================
>>> wrapped_encoder.simp_pipeline() # 接连调用了方法 truth_table, sop, simplified 并输出
====== 逻辑函数 encoder 化简流水线 ======
truth_table():
 {(('IN', Logic (0000)),): (('Y', Logic (00)),), (('IN', Logic (0001)),): (('Y', Logic (00)),), (('IN', Logic (0010)),): (('Y', Logic (01)),), (('IN', Logic (0011)),): (('Y', Logic (00)),), (('IN', Logic (0100)),): (('Y', Logic (10)),), (('IN', Logic (0101)),): (('Y', Logic (00)),), (('IN', Logic (0110)),): (('Y', Logic (01)),), (('IN', Logic (0111)),): (('Y', Logic (00)),), (('IN', Logic (1000)),): (('Y', Logic (11)),), (('IN', Logic (1001)),): (('Y', Logic (00)),), (('IN', Logic (1010)),): (('Y', Logic (01)),), (('IN', Logic (1011)),): (('Y', Logic (00)),), (('IN', Logic (1100)),): (('Y', Logic (10)),), (('IN', Logic (1101)),): (('Y', Logic (00)),), (('IN', Logic (1110)),): (('Y', Logic (01)),), (('IN', Logic (1111)),): (('Y', Logic (00)),)}
sop():
 [[2, 6, 8, 10, 14], [4, 8, 12]]
simplified():
 {'Y0': ('IN1!IN0', 'IN3!IN2!IN0'), 'Y1': ('IN2!IN1!IN0', 'IN3!IN1!IN0')}
>>> # ==================== 多输入多输出函数 ====================
>>> @FmtLogicFunction[4,3] # 我们可以直接将 FmtLogicFunction 类当做函数修饰器用
... def adder_2bit(a: Logic[2], b: Logic[2]): # 各输出的位宽不尽相同，我们可以不注解返回类型
...     \"\"\"2 位加法器\"\"\"
...     carry, *sum = a + b # 这里使用解包模拟位拼接，注意 *sum 是 list[bool], carry 是 bool
...     return {"sum": Logic[2](sum), "cout": Logic[1](carry)} # 必须以名称：值的键值对返回,每个返回值仍然需要定长
...
>>> adder_2bit.simp_pipeline()
====== 逻辑函数 adder_2bit 化简流水线 ======
truth_table():
 {(('a', Logic (00)), ('b', Logic (00))): (('sum', Logic (00)), ('cout', Logic (0))), (('a', Logic (01)), ('b', Logic (00))): (('sum', Logic (00)), ('cout', L('cout', Logic (1))), (('a', Logic (00)), ('b', Logic (01))): (('sum', Logic (00)), ('cout', Logic (1))), (('a', Logic (01)), ('b', Logic (01))): (('sum', Logic (01)), ('cout', Logic (0))), (('a', Logic (10)), ('b', Logic (01))): (('sum', Logic (01)), ('cout', Logic (1))), (('a', Logic (11)), ('b', Logic (01))): (('sum', Logic (10)), ('cout', Logic (0))), (('a', Logic (00)), ('b', Logic (10))): (('sum', Logic (01)), ('cout', Logic (0))), (('a', Logic (01)), ('b', Logic (10))): (('sum', Logic (01)), ('cout', Logic (1))), (('a', Logic (10)), ('b', Logic (10))): (('sum', Logic (10)), ('cout', Logic (0))), (('a', Logic (11)), ('b', Logic (10))): (('sum', Logic (10)), ('cout', Logic (1))), (('a', Logic (00)), ('b', Logic (11))): (('sum', Logic (01)), ('cout', Logic (1))), (('a', Logic (01)), ('b', Logic (11))): (('sum', Logic (10)), ('cout', Logic (0))), (('a', Logic (10)), ('b', Logic (11))): (('sum', Logic (10)), ('cout', Logic (1))), (('a', Logic (11)), ('b', Logic (11))): (('sum', Logic (11)), ('cout', Logic (0)))}
sop():
 [[2, 3, 5, 6, 8, 9, 12, 15], [7, 10, 11, 13, 14, 15], [1, 3, 4, 6, 9, 11, 12, 14]]
simplified():
 {'sum0': ('!b1!b0a1', '!b1b0!a1a0', '!b1a1!a0', 'b1!b0!a1', 'b1!a1!a0', 'b1b0a1a0'), 'sum1': ('b0a1a0', 'b1a1', 'b1b0a0'), 'cout0': ('!b0a0', 'b0!a0')}
>>> # ==================== 其它功能 ====================
>>> adder_2bit.pos() # 获取最大项之积
[[0, 1, 4, 7, 10, 11, 13, 14], [0, 1, 2, 3, 4, 5, 6, 8, 9, 12], [0, 2, 5, 7, 8, 10, 13, 15]]
>>> # 位宽属性被设为受保护常量成员，遵照“大家都是成年人”原则，允许用户直接获取（脑子没坏不要更改常量）
>>> adder_2bit._INPUT_WIDTH
4
>>> adder_2bit._OUTPUT_WIDTH
3

保留为用户接口的细节
---

以下内容本应当作为内部实现，但考虑到可能的解题需求，保留为用户接口。使用者可自行查看对应的函数 / 类文档了解使用方法

quine_mccluskey  : QM 法化简函数
LogicFunctionFormat  : 输入输出格式，配合 quine_mccluskey 使用
default_fmt : 生成默认格式
generate_logic_function_fmt  : 自动推导逻辑函数输入输出格式

更新日志
---
- 2024-07-10: 实现奎恩 - 麦克拉斯基法化简逻辑函数，模块名称暂为 quine_mccluskey.py
- 2025-10-25: 逻辑函数化简重磅升级！加入了 Logic 和 _LogicFunction 类，全面支持面向对象编程，用户可以自定义逻辑函数并获取真值表、 sop 和化简结果。模块名称改为 logic.py
- 2025-10-27: 支持定制格式化输入输出名称，支持由逻辑函数直接生成对应的格式化映射表
- 2025-10-30: 加入接口 FmtLogicFunction 类，所有流程全自动完成。文档完善。
- 2025-11-02: 修复示例代码的逻辑错误。
"""

# coding: utf-8

import typing
import inspect
from typing import get_type_hints, get_args, get_origin, Union, Dict, Any
import types
import collections
import functools

if __name__ == "__main__":
    import functions
else:
    from . import functions


if __name__ == "__main__":
    import json


@typing.overload
def quine_mccluskey(*minterms_dec, width: int = 0) -> tuple[str]: ...
@typing.overload
def quine_mccluskey(
    *minterms_dec,
    width: int = 0,
    fmt: "LogicFunctionFormat",
    output_bit: int = 0,
) -> dict[str, tuple[str]]: ...


def quine_mccluskey(
    *minterms_dec,
    width=0,
    fmt=None,
    output_bit=0,
) -> tuple[str] | dict[str, tuple[str]]:
    """
    使用奎恩 - 麦克拉斯基法化简逻辑函数。

    Args:
        *minterms_dec (int): 最小项编码，十进制
        width (int | None): 指定最小项的位宽，指定的位宽小于最大位宽时会被调整。 默认为 0，自适应位宽。
        fmt (LogicFunctionFormat | None): 合并结果格式化方式，默认为 None，不进行格式化。
        output_bit (int): 指定化简结果在 fmt 中的位置索引，仅在 fmt 不为 None 时有效

    Returns:
        tuple: 所有必要乘积项的二进制表示

    Raises:
        无

    Exaples:
        >>> quine_mccluskey (0, 1, 3, 5, 7, width=4)
        ... ('0--1', '000-')
    """

    def replace_single_diff(str1: str, str2: str, target_char: str = "-") -> str | None:
        """
        比较两个字符串，若恰好有一个字符不同，则返回差异位置替换为 target_char 的新字符串
        用于奎恩麦克拉斯基法的最小项合并

        Args:
            str1: 第一个输入字符串
            str2: 第二个输入字符串
            target_char: 替换后的字符，默认为 '-'。

        Returns:
            str: 处理后的新字符串
            None: 当无差异、多个差异

        Raises:
            ValueError: 当输入字符串长度不一致时

        Examples:
            >>> replace_single_diff ("abc", "adc")
            'a-c'
            >>> replace_single_diff ("11-", "10-")
            '1--'
            >>> replace_single_diff ("-bc", "abc")
            '-bc'
            >>> replace_single_diff ("a-c", "a1c")
            'a-c'
        """
        if functions.diff_char(str1, str2) == 1:
            return functions.replace_diff(str1, str2, "-")
        else:
            return None

    # 读取最小项编码表，并转换为二进制字符串列表
    minterms: list = [bin(int(x))[2:] for x in minterms_dec]  # 切去 0b

    # 确定最大位数
    max_length: int = max(max(len(d) for d in minterms), width)
    # 保持位数统一
    minterms = [d.zfill(max_length) for d in minterms]

    """
    根据包含 1 的个数将最小项分组为列表
    列表的索引是 1 的个数，
    元素是  最小项编码的单元素元组：最小项编码（合并前）
            乘积项所包含的最小项编码组成的元组：乘积项编码（合并后）
    """
    grouped_minterms: list[dict[tuple:str]] = [
        dict() for _ in range(max_length + 1)
    ]  # 最少 0 个 1，最多有 max_length 个 1

    for minterms_index in range(0, len(minterms)):
        num_of_1 = minterms[minterms_index].count("1")
        grouped_minterms[num_of_1].update(
            {(minterms[minterms_index],): minterms[minterms_index]}  # 用元组表示
        )

    # 第一步：合并乘积项

    unmergeable_terms: dict[tuple[int] : str] = (
        dict()
    )  # 记录不能合并的项, 需要去重，顺序无关紧要

    while True:
        """
        将每一组的每一个最小项与相邻组里所有的最小项逐一比较。
        若仅有一个因子不同，则可以合并, 并消除不同的因子。
        消去的因子用 - 表示。不能合并的项需要记录并移除。
        """

        merge_rslts: list[dict[tuple:str]] = [dict() for _ in range(max_length + 1)]
        # 临时存储合并结果, 索引是 1 的个数，元素是 最小项编号组合：二进制最小项编码（字典）

        mergeable: list[dict[tuple:bool]] = [dict() for _ in range(max_length + 1)]
        # 记录每一个项是否可以合并，索引是 1 的个数，元素是 最小项编号（组合）：是否可合并（字典）

        for num_of_1 in range(0, max_length + 1):
            for term in grouped_minterms[num_of_1].items():
                if num_of_1 != max_length:
                    for other_term in grouped_minterms[num_of_1 + 1].items():
                        # 尝试替换
                        replace_rslt: str = replace_single_diff(term[1], other_term[1])
                        if replace_rslt != None:
                            # 替换成功，记录结果
                            num_of_1_after_replace = replace_rslt.count("1")
                            merge_rslts[num_of_1_after_replace].update(
                                {
                                    tuple(
                                        sorted(
                                            (
                                                *term[0],
                                                *other_term[0],
                                            )
                                        )
                                    ): replace_rslt
                                }
                            )  # 排序的目的：防止诸如（0,2，8,10）：0-0-0 与（0,8,2,10）：0-0-0 被视为两个不同的乘积项
                            mergeable[num_of_1][term[0]] = True
                            mergeable[num_of_1 + 1][other_term[0]] = True
                # 不可替换，记录
                if term[0] not in mergeable[num_of_1]:
                    unmergeable_terms.update({term[0]: term[1]})
        # 迭代，进行下一次合并
        grouped_minterms = merge_rslts
        # 终止条件: 全部合并不了
        if not any(merge_rslts):
            break

    # 第二步：选择必要的乘积项

    results: dict[tuple[str], str] = dict()  # 储存化简结果
    minterms_included: set[str] = set()  # 最终保留的乘积项已经包含的最小项

    for minterm in minterms:

        product_terms_included: list = []  # 记录包含该最小项的乘积项
        minterms_included_in_product_terms: list = (
            []
        )  # 记录包含该最小项的乘积项所包含的所有乘积项

        for tuple_of_minterms, product_term in unmergeable_terms.items():
            if minterm in tuple_of_minterms:
                product_terms_included.append({tuple_of_minterms: product_term})
                minterms_included_in_product_terms.extend(tuple_of_minterms)

        if len(product_terms_included) == 1:
            # 仅包含在一个乘积项中，该乘积项必须在结果中
            results.update(product_terms_included[0])
            # 记录该乘积项包含的最小项
            minterms_included |= set(minterms_included_in_product_terms)

    minterms_remained: set = set(minterms) - minterms_included

    product_terms_remained: dict = {
        key: item for key, item in unmergeable_terms.items() if key not in results
    }

    # 第三步：枚举法选择最少的乘积项
    for comb in functions.enumerate_comb(product_terms_remained.items()):
        # print (comb)
        all_minterms: set = set()
        for item in comb:
            all_minterms |= set(item[0])
        # print (all_minterms)
        if minterms_remained.issubset(all_minterms):
            # 合并结果
            results: list = list(results.values())
            for item in comb:
                results.append(item[1])
            break

    if fmt is None:
        return tuple(results)

    else:
        # ============================格式化===============================

        output_name: str = ""
        input_names: list[str] = ["" for _ in range(max_length)]

        # 在 fmt 中查找输出名称
        for output_range, name in fmt.output_fmt.items():
            if output_bit in output_range:
                output_name = (
                    f"{name}{(output_bit - output_range.start) // output_range.step}"
                )
                break

        # 在 fmt 中查找输入名称
        for input_range, name in fmt.input_fmt.items():
            for bit_index in input_range:
                input_names[bit_index] = (
                    f"{name}{(bit_index - input_range.start) // input_range.step}"
                )

        # 格式化结果

        formatted_results: list[str] = list("" for _ in results)
        for index_prod, prod_term in enumerate(results):
            for index_in, char in enumerate(prod_term):
                if char == "1":
                    formatted_results[index_prod] = (
                        formatted_results[index_prod]
                        + f"{input_names[max_length - index_in - 1]}"
                    )  # 高位在后
                elif char == "0":
                    formatted_results[index_prod] = formatted_results[index_prod] + (
                        f"!{input_names[max_length - index_in - 1]}"
                    )
                elif char == "-":
                    pass

        return {output_name: tuple(formatted_results)}


class Logic[WIDTH: int = 32]:
    """
    # 逻辑信号类型 Logic

    - 完全由 bool 值组成（不存在不定态 x 和高组态 z），相当于 systemverilog 里的 bit 数组类型。
    - 支持位运算、算术运算（按无符号数进行运算）、各种容器方法（支持解包）。
    - 运算时严格进行位宽检查，确保类型安全
    - 天然不可变，元组存储，禁止增强赋值，数值安全

    ## type parameters:
        WIDTH (int): 信号的位宽，默认为 32 位。

    Attributes:
        _bits (bool): 各个位的布尔值，低位在前。
        _width (int | None): 信号位宽。用于位宽检查。

        _fmt_radix (static, int): 格式化输出的进制，默认为 2 进制。

    ## Methods:
        __get_fmt_radix (static): 获取当前格式化输出进制。
        __set_fmt_radix (static): 设定格式化输出进制。
        __init__: 构造函数，支持多种构造方式。
        __repr__: 返回对象的字符串表示。
        __str__: 返回信号的二进制字符串表示。
        __int__: 返回信号的整数值。
        位运算方法: __and__, __or__, __xor__, __invert__, __lshift__, __rshift__
        算术运算方法: __neg__, __pos__, __add__, __sub__, __mul__, __floordiv__
        容器方法: __len__, __getitem__, __setitem__, __iter__, __reversed__


    """

    _bits: list[bool]
    _WIDTH: int
    _fmt_radix: int = 2

    @staticmethod
    def get_fmt_radix() -> int:
        """
        获取当前格式化输出进制
        """
        return Logic._fmt_radix

    @staticmethod
    def set_fmt_radix(radix: int):
        """
        设定格式化输出进制

        Args:
            radix (int): 进制，支持 2、8、10、16。

        Raises:
            ValueError: 当进制不支持时抛出。
        """
        if radix in (2, 8, 10, 16):
            Logic._fmt_radix = radix
        else:
            raise ValueError("仅支持 2、8、10、16 进制")

    @typing.overload
    def __init__(self): ...

    """
    默认构造，生成 1 位宽的 Logic 信号，值为 0。
    """

    @typing.overload
    def __init__(self, *bits: bool): ...

    """
    参数包构造，生成指定各个位的 Logic 信号。
    """

    @typing.overload
    def __init__(self, bits: str): ...

    """
    字符串构造，生成与字符串表示相同的 Logic 信号。
    高位在前，低位在后。
    """

    @typing.overload
    def __init__(self, num: int, width: int | None = None): ...

    """
    整型构造，生成与整数值相同的 Logic 信号。
    若指定 width，则生成指定位宽的 Logic 信号；否则生成自适应位宽的 Logic 信号。
    """

    @typing.overload
    def __init__(self, bits: typing.Iterable[bool]): ...

    """
    容器构造    
    """

    def __init__(self, *bits):
        """
        构造函数

        ## 重载解析

        ### 默认构造
        - 无参数构造，生成 1 位宽的 Logic 信号，值为 0。

        #### Args:
            无

        ### 布尔值构造
        - 单个布尔值，生成 1 位宽的 Logic 信号。

        #### Args:
            bit (bool): 单个布尔值，生成 1 位宽的 Logic 信号。

        ### 字符串构造
        - 单个字符串，生成与字符串表示相同的 Logic 信号。

        #### Args:
            bits (str): 二进制字符串表示，高位在前，低位在后。

        ### 整型构造

        #### Args:
            num (int): 整数值，生成与整数值相同的 Logic 信号。
            width (int | None): 指定位宽，默认为 None，自适应位宽。

        ### 容器构造

        #### Args:
            bits (typing.Iterable[bool]): 布尔值容器，生成与容器中布尔值相同的 Logic 信号。

        ### 参数包构造

        #### Args:
            *bits: 可变参数，根据参数类型和数量进行不同的构造方式。

        ## Raises:
            TypeError: 当构造参数不符合任何一种方式时抛出。

        ## Examples:

            >>> Logic [1] ()                # 默认构造
            Logic (0b0)
            >>> Logic [1] (True)            # 布尔值构造
            Logic (0b1)
            >>> Logic [8] ('11010010')      # 字符串构造
            Logic (0b11010010)
            >>> Logic [8] (10)             # 整型构造，自适应位宽
            Logic (0b1010)
            >>> Logic [8] (10, 8)           # 整型构造，指定位宽
            Logic (0b00001010)
            >>> Logic [4] ([True, False, True, False])  # 容器构造
            Logic (0b1010)
            >>> Logic [4] (True, False, True, False)  # 参数包构造
            Logic (0b1010)
        """

        if len(bits) == 0:  # 默认构造
            self._bits = [False]
            self._WIDTH = 1

        elif len(bits) == 1:
            if isinstance(bits[0], bool):  # 布尔值构造
                self._bits = [bits[0]]
                self._WIDTH = 1
            elif isinstance(bits[0], str):  # 字符串构造 (高位在前)
                self._bits = list(reversed([(bit == "1") for bit in bits[0]]))
                self._WIDTH = len(self._bits)
            elif isinstance(bits[0], int):  # 整型构造
                temp: Logic[WIDTH] = Logic[WIDTH](bin(bits[0])[2:])
                self._bits = temp._bits
                self._WIDTH = temp._WIDTH
            elif functions.is_iterable(bits[0]) and all(
                isinstance(b, bool) for b in bits[0]
            ):  # 容器构造
                self._bits = list(bits[0])
                self._WIDTH = len(self._bits)
            else:  # 非法构造
                raise TypeError(f"非法构造, 参数类型: {type(bits[0])}")

        elif len(bits) == 2 and all(
            (type(b) == int)
            for b in bits  # 此处不能使用 isinstance , 因为 bool 是 int 的子类
        ):  # 指定位宽的整型构造
            temp: Logic[WIDTH] = Logic[WIDTH](bin(bits[0])[2:].zfill(bits[1]))
            self._bits = temp._bits
            self._WIDTH = temp._WIDTH

        elif all(isinstance(b, bool) for b in bits):  # 参数包构造（低位在前）
            self._bits = list(bits)
            self._WIDTH = len(bits)

        else:  # 非法构造
            raise TypeError(f"非法构造, 参数类型: {[type(b) for b in bits]}")

    def __repr__(self) -> str:
        return f"Logic ({"".join(["1" if b else "0" for b in reversed(self._bits)])})"

    def __str__(self) -> str:
        """
        转为字符串。注意存在前缀 0b、0o、0d、0x。

        ## Notes:
            - 字符串表示总是完整表示所有位，包括高位的 0。
            - 此方法受当前格式化输出进制设置影响，若想确保转为二进制形式可以使用 tuple 或 list 方法转为布尔元组 / 列表

        ## Examples:

            >>> str (Logic [4] (10))
            '0b1010'
            >>> str (Logic [8] ('11010010'))
            '0b11010010'
        """
        bin_str = "".join(["1" if b else "0" for b in reversed(self._bits)])
        bin_int = int(bin_str, 2)

        if Logic.get_fmt_radix() == 10:
            return f"0d{bin_int}"
        elif Logic.get_fmt_radix() == 16:
            return f"0x{hex(bin_int)[2:]}"
        elif Logic.get_fmt_radix() == 8:
            return f"0o{oct(bin_int)[2:]}"
        elif Logic.get_fmt_radix() == 2:
            return f"0b{bin_str}"
        else:
            raise ValueError("仅支持 2、8、10、16 进制")

    def __bool__(self) -> bool:
        """
        转为布尔值。仅当所有位均为 0 时返回 False，否则返回 True。

        ## Examples:

            >>> bool (Logic [4] (0))
            False
            >>> bool (Logic [4] (10))
            True
        """
        return any(self._bits)

    def __int__(self):
        """

        转为整数。视为无符号数。

        ## Examples:

            >>> int (Logic [4] (10))
            10
            >>> int (Logic [8] ('11010010'))
            210
        """
        return int(str(self), base=Logic.get_fmt_radix())

    # --------------------------------- 位运算 ------------------------------------

    def __and__(self, other: "Logic [WIDTH]") -> "Logic [WIDTH]":
        if other._WIDTH != self._WIDTH:
            raise ValueError(
                f"位宽不匹配，左操作数宽度为 {self._WIDTH}，右操作数宽度为 {other._WIDTH}"
            )
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        return Logic(*[a and b for a, b in zip(self._bits, other._bits)])

    def __or__(self, other: "Logic [WIDTH]") -> "Logic [WIDTH]":
        if other._WIDTH != self._WIDTH:
            raise ValueError(
                f"位宽不匹配，左操作数宽度为 {self._WIDTH}，右操作数宽度为 {other._WIDTH}"
            )
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        return Logic(*[a or b for a, b in zip(self._bits, other._bits)])

    def __xor__(self, other: "Logic [WIDTH]") -> "Logic [WIDTH]":
        if other._WIDTH != self._WIDTH:
            raise ValueError(
                f"位宽不匹配，左操作数宽度为 {self._WIDTH}，右操作数宽度为 {other._WIDTH}"
            )
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        return Logic(*[a ^ b for a, b in zip(self._bits, other._bits)])

    def __invert__(self) -> "Logic [WIDTH]":
        return Logic(*[not b for b in self._bits])

    def __lshift__(self, shamt: int) -> "Logic [WIDTH]":
        if shamt < 0:
            raise ValueError("左移位数必须为非负整数")
        return Logic(*([False] * shamt + self._bits)[:WIDTH])

    def __rshift__(self, shamt: int) -> "Logic [WIDTH]":
        if shamt < 0:
            raise ValueError("右移位数必须为非负整数")
        return Logic(*(self._bits[shamt:] + [False] * shamt))

    # --------------------------------- 算术运算 ------------------------------------

    def __neg__(self) -> "Logic [WIDTH]":
        # 视为无符号类型，直接取相反数补码
        temp: list[bool] = []
        carry: bool = True
        for b in reversed(self._bits):
            if carry:
                if b:
                    temp.append(False)
                else:
                    temp.append(True)
                    carry = False
            else:
                temp.append(b)
        return Logic(*reversed(temp))

    def __pos__(self) -> "Logic [WIDTH]":
        return self

    def __add__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=Logic.get_fmt_radix())
        int_other = int(str(other), base=Logic.get_fmt_radix())
        return Logic(
            int_other + int_self, max(self._WIDTH, other._WIDTH) + 1  # 包含进位
        )

    def __sub__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=Logic.get_fmt_radix())
        int_other = int(str(other), base=Logic.get_fmt_radix())
        return Logic(int_self - int_other, max(self._WIDTH, other._WIDTH))

    def __mul__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=Logic.get_fmt_radix())
        int_other = int(str(other), base=Logic.get_fmt_radix())
        return Logic(
            int_self * int_other,
            self._WIDTH + other._WIDTH,
        )

    def __floordiv__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=Logic.get_fmt_radix())
        int_other = int(str(other), base=Logic.get_fmt_radix())
        return Logic(
            int_self // int_other,
            self._WIDTH - other._WIDTH if self._WIDTH >= other._WIDTH else 1,
        )

    # ============================== 容器 ====================================
    def __len__(self) -> int:
        return len(self._bits)

    @typing.overload
    def __getitem__(self, index: int) -> "bool": ...
    @typing.overload
    def __getitem__(self, slice_inst: slice) -> "Logic": ...

    def __getitem__(self, item) -> "Logic | bool":
        if isinstance(item, slice):
            # 处理切片操作，返回新的Logic对象
            sliced_bits = self._bits[item]
            # 由于切片可能改变位宽，我们创建一个新的Logic对象
            # 这里我们不能准确指定新的位宽，因为切片是动态的
            return Logic(*sliced_bits)
        else:
            # 处理单个索引
            return self._bits[item]

    def __iter__(self):
        return iter(self._bits)

    def __reversed__(self):
        return Logic[WIDTH](*reversed(self._bits))

    def count(self, value: bool) -> int:
        """
        统计信号中指定布尔值的个数。

        Args:
            value (bool): 要统计的布尔值。

        Returns:
            int: 指定布尔值的个数。

        Examples:
            >>> logic_signal = Logic [8] ('11010010')
            >>> logic_signal.count (True)
            4
            >>> logic_signal.count (False)
            4
        """
        return self._bits.count(value)


class LogicFunctionFormat[input_width, output_width](
    collections.namedtuple("LogicFunctionFormat", ["input_fmt", "output_fmt"])
):
    """
    逻辑函数格式化输入输出对象

    它是一个 pair, 元素名称分别是 input_fmt 和 output_fmt ，建议使用关键字传参来构造

    琪第一个元素为输入格式化的映射表（字典），第二个元素为输出格式化的映射表（字典）

    字典的键为标准库 range 类，表示位宽范围，值为对应的名称

    例如，一个二位加法器的输入格式化映射表可以表示为：
    ```python
    {range (0, 2): "a", range (2, 4): "b", range (4, 5): "cin"}
    ```
    此时，输入信号的第 0-1 位会被命名为 a0 和 a1，第 2-3 位会被命名为 b0 和 b1，第 4 位会被命名为 cin0

    **若 range 没有覆盖所有位， 则这些位输出时会被忽略**

    """


def default_fmt(input_width: int, output_width: int) -> LogicFunctionFormat:
    """
    生成逻辑函数的默认格式化对象，输入命名为 X，输出命名为 Y。

    Args:
        _input_width (int): 输入信号的位宽。
        _output_width (int): 输出信号的位宽。

    Returns:
        LogicFunctionFormat: 逻辑函数格式化对象，输入输出命名为 X 和 Y。
    """
    return LogicFunctionFormat(
        input_fmt={range(0, input_width): "X"},
        output_fmt={range(0, output_width): "Y"},
    )


@typing.overload
def _LogicFunctionFormatter(
    func: typing.Callable[[Logic], dict[str, Logic]],
    fmt: LogicFunctionFormat,
) -> typing.Callable[[Logic], Logic]: ...


@typing.overload
def _LogicFunctionFormatter(
    func: typing.Callable[[Logic], Logic],
    fmt: LogicFunctionFormat,
) -> typing.Callable[[Logic], Logic]: ...


def _LogicFunctionFormatter(func, fmt):
    """
    逻辑函数装饰器。若逻辑函数有多输入和**字典形式**的多输出，装饰后会将输入/输出按照 fmt 中的索引顺序合并为单个输入 / 单个输出。

    装饰后的逻辑函数可以直接封装为 _LogicFunction 对象， 而多输入多输出函数是无法直接封装为 _LogicFunction 对象的。

    Args:
        func (typing.Callable[[Logic], dict[str, Logic] | Logic]): 需要格式化的逻辑函数。多输出**必须为字典格式**。
        fmt (LogicFunctionFormat): 逻辑函数格式化对象。

    Returns:
        wrapper (typing.Callable[[Logic],Logic]): 可以直接封装为 _LogicFunction 对象的逻辑函数

    Raises:
        TypeError: 当逻辑函数返回类型不符合预期时抛出。

    """

    def wrapper(input: Logic):
        # 拆分输入
        split_in = {
            name: input[_range.start : _range.stop : _range.step]
            for _range, name in fmt.input_fmt.items()
        }

        output = func(**split_in)

        if isinstance(output, dict):
            # 合并输出
            output_max_length = (
                max((_range.stop - _range.step) for _range in fmt.output_fmt.keys()) + 1
            )
            merged_output = [False for _ in range(output_max_length)]
            for _range, name in fmt.output_fmt.items():
                merged_output[_range.start : _range.stop : _range.step] = output[
                    name
                ]  # 解包再切片赋值
            return Logic(*merged_output)

        elif isinstance(output, Logic):
            return output

        else:
            raise TypeError(
                f"不支持的函数返回类型，期望 dict 或 Logic， 实际为 {type(output)}"
            )

    return wrapper


def _LogicFunctionFormatterFactory(
    fmt: LogicFunctionFormat,
) -> typing.Callable[
    [typing.Callable[[Logic], dict[str, Logic]]],
    typing.Callable[[Logic], Logic],
]:
    """
    逻辑函数装饰器生成器。用于生成逻辑函数装饰器。

    Args:
        fmt (LogicFunctionFormat): 逻辑函数格式化对象。

    Returns:
        decorator (typing.Callable): 逻辑函数装饰器。

    Raises:
        无

    Examples:
        >>> @_LogicFunctionFormatterFactory ( LogicFunctionFormat (
        ...     input_fmt={ range (0,2): "a", range (2,4): "b" },
        ...     output_fmt={ range (0,1): "sum", range (1,2): "carry" }
        ... ) )
        ... def adder_2bit ( a: Logic[2], b: Logic[2] ) -> dict[str, Logic[1]]:
        ...     total = a + b
        ...     return {
        ...         "sum": total[0:1],
        ...         "carry": total[1:2]
        ...     }
    """

    return functools.partial(_LogicFunctionFormatter, fmt=fmt)


class _LogicFunction[input_width, output_width]:
    """
    逻辑函数类型 _LogicFunction

    ## type parameters:
        input_width (int): 输入信号的位宽。
        output_width (int): 输出信号的位宽。

    Attributes:
        _INPUT_WIDTH (int): 输入信号的位宽。
        _OUTPUT_WIDTH (int): 输出信号的位宽。
        _function (Callable [[Logic [input_width]], Logic [output_width]]): 逻辑函数的实现。

    ## Methods:
        __init__: 构造函数，设定输入输出位宽和逻辑函数实现。
        set_function: 设定逻辑函数的实现。
        __call__: 调用逻辑函数。
        truth_table: 生成逻辑函数的真值表。
        sop: 生成逻辑函数的最小项之和表示。
        simplified: 使用奎恩 - 麦克拉斯基法化简最小项之和表示。

    ## Notes:
        - 该类尽可能地支持了泛型编程，强烈建议设定 type parameters
        - 逻辑函数在调用时会进行严格的输入输出位宽检查
    """

    _INPUT_WIDTH: int
    _OUTPUT_WIDTH: int
    _function = lambda: Logic[1](False)

    def _WidthCheck(
        self, func: typing.Callable[[Logic[input_width]], Logic[output_width]]
    ):
        """
        函数修饰器，为逻辑函数添加输入输出位宽断言。
        """

        def wrapper(input: Logic[input_width]):

            if input._WIDTH != self._INPUT_WIDTH:
                raise ValueError(
                    f"输入位宽不匹配，期望 {self._INPUT_WIDTH}，实际 {input._WIDTH}"
                )
            else:
                re = func(input)
                if re._WIDTH != self._OUTPUT_WIDTH:
                    raise ValueError(
                        f"输出位宽不匹配，期望 {self._OUTPUT_WIDTH}，实际 {re._WIDTH}"
                    )
                else:
                    return re

        wrapper.__name__ = func.__name__

        return wrapper

    @typing.overload
    def __init__(
        self,
        input_width: int,
        output_width: int,
        function: typing.Callable[[Logic[input_width]], Logic[output_width]],
    ): ...

    @typing.overload
    def __init__(self, func: "FmtLogicFunction"): ...

    @functions.CopyConstructor
    def __init__(self, input_width, output_width=None, function=None):
        """
        构造函数，设定输入输出位宽和逻辑函数实现。

        Note:
            - 逻辑函数无需用户定义输入输出位宽检查，已由类自动处理
        """
        if isinstance(input_width, int):

            self._INPUT_WIDTH = input_width
            self._OUTPUT_WIDTH = output_width
            self._function = self._WidthCheck(function)

        else:
            raise TypeError(
                f"非法构造, 参数类型: {type(input_width)}, {type(output_width)}, {type(function)}"
            )

    def __call__(self, input: Logic[input_width]) -> Logic[output_width]:
        """
        强制检查输入输出位宽后，调用逻辑函数。

        Examples:
            >>> def example_func (input: Logic [2]) -> Logic [1]:
            ...     return Logic [1] (input [0] or input [1]) # 或运算
            >>> func = _LogicFunction [2, 1] (2, 1, example_func)
            >>> func (Logic [2] (0, 1))
            Logic (0b1)
            >>> func (Logic [2] (0, 0))
            Logic (0b0)
        """

        return self._function(input)

    @typing.overload
    def truth_table(
        self, fmt: LogicFunctionFormat[input_width, output_width]
    ) -> dict[tuple[tuple[str, Logic]], tuple[tuple[str, Logic]]]: ...

    @typing.overload
    def truth_table(self) -> dict[Logic[input_width], Logic[output_width]]: ...

    def truth_table(
        self, fmt: LogicFunctionFormat[input_width, output_width] | None = None
    ) -> (
        dict[Logic[input_width], Logic[output_width]]
        | dict[tuple[tuple[str, Logic]], tuple[tuple[str, Logic]]]
    ):
        """
        获取真值表

        Args:
            fmt (LogicFunctionFormat | None): 格式化输入输出的映射表，默认为 None，不进行格式化（注意不是采用默认格式化）。

        Returns:
            dict [Logic [input_width], Logic [output_width]] | dict[tuple[tuple[str,Logic]], tuple[tuple[str,Logic]]]:
                真值表，不格式化时键为输入，值为对应输出；格式化时键为输入的格式化表示，值为对应输出的格式化表示。

        Examples:
            >>> def example_func (input: Logic [4]) -> Logic [3]:
            ...     \"\"\"信号计数 \"\"\"
            ...     return Logic [3](input.count (True), 3)
            >>> func = _LogicFunction [4, 3] (4, 3, example_func)
            >>> func.truth_table()
             {Logic (0b0000): Logic (0b000), Logic (0b0001): Logic (0b001), Logic (0b0010): Logic (0b001), Logic (0b0011): Logic (0b010), Logic (0b0100): Logic (0b001), Logic (0b0101): Logic (0b010), Logic (0b0110): Logic (0b010), Logic (0b0111): Logic (0b011), Logic (0b1000): Logic (0b001), Logic (0b1001): Logic (0b010), Logic (0b1010): Logic (0b010), Logic (0b1011): Logic (0b011), Logic (0b1100): Logic (0b010), Logic (0b1101): Logic (0b011), Logic (0b1110): Logic (0b011), Logic (0b1111): Logic (0b100)}
            >>> # 二位加法器真值表，格式化输入输出
            >>> func = _LogicFunction [4, 3] (4, 3, lambda input: input[0:2] + input[2:4])
            >>> func.truth_table (fmt= LogicFunctionFormat[4,3](
            ...     {range(0,2):"a",range(2,4):"b"},
            ...     {range(0,2):"sum",range(2,3):"cout"}
            ...     ))
             {(('a', Logic (00)), ('b', Logic (00))): (('sum', Logic (00)), ('cout', Logic (0))), (('a', Logic (01)), ('b', Logic (00))): (('sum', Logic (01)), ('cout', Logic (0))), (('a', Logic (10)), ('b', Logic (00))): (('sum', Logic (10)), ('cout', Logic (0))), (('a', Logic (11)), ('b', Logic (00))): (('sum', Logic (11)), ('cout', Logic (0))), (('a', Logic (00)), ('b', Logic (01))): (('sum', Logic (01)), ('cout', Logic (0))), (('a', Logic (01)), ('b', Logic (01))): (('sum', Logic (10)), ('cout', Logic (0))), (('a', Logic (10)), ('b', Logic (01))): (('sum', Logic (11)), ('cout', Logic (0))), (('a', Logic (11)), ('b', Logic (01))): (('sum', Logic (00)), ('cout', Logic (1))), (('a', Logic (00)), ('b', Logic (10))): (('sum', Logic (10)), ('cout', Logic (0))), (('a', Logic (01)), ('b', Logic (10))): (('sum', Logic (11)), ('cout', Logic (0))), (('a', Logic (10)), ('b', Logic (10))): (('sum', Logic (00)), ('cout', Logic (1))), (('a', Logic (11)), ('b', Logic (10))): (('sum', Logic (01)), ('cout', Logic (1))), (('a', Logic (00)), ('b', Logic (11))): (('sum', Logic (11)), ('cout', Logic (0))), (('a', Logic (01)), ('b', Logic (11))): (('sum', Logic (00)), ('cout', Logic (1))), (('a', Logic (10)), ('b', Logic (11))): (('sum', Logic (01)), ('cout', Logic (1))), (('a', Logic (11)), ('b', Logic (11))): (('sum', Logic (10)), ('cout', Logic (1)))}
        """
        self = _LogicFunction(
            self
        )  # 显式将子类转换为基类， 从而防止 虚函数覆盖逻辑 而是使用类似 C++ 的命名隐藏逻辑

        if fmt is None:
            _truth_table: dict[Logic[input_width], Logic[output_width]] = {}
            for i in range(0, 2**self._INPUT_WIDTH):
                input = Logic[input_width](i, self._INPUT_WIDTH)
                _truth_table[input] = self(input)
                continue
            return _truth_table

        else:
            _truth_table: dict[tuple[tuple[str, Logic]], tuple[tuple[str, Logic]]] = {}
            for i in range(0, 2**self._INPUT_WIDTH):
                input_not_fmted = Logic[input_width](i, self._INPUT_WIDTH)
                output_not_fmted = self(input_not_fmted)

                fmted_input_part: tuple[tuple[str, Logic]] = tuple(
                    (
                        name,
                        input_not_fmted[
                            fmt_range.start : fmt_range.stop : fmt_range.step
                        ],
                    )
                    for fmt_range, name in fmt.input_fmt.items()
                )
                fmted_output_part: tuple[tuple[str, Logic]] = tuple(
                    (
                        name,
                        output_not_fmted[
                            fmt_range.start : fmt_range.stop : fmt_range.step
                        ],
                    )
                    for fmt_range, name in fmt.output_fmt.items()
                )

                _truth_table[fmted_input_part] = fmted_output_part
            return _truth_table

    def sop(self):
        """
        获取最小项之和表示

        Returns:
            list [list [int]]: 最小项之和表示，索引为输出的第 n 位，值为该位的最小项列表。

        Examples:
            >>> def decoder_7448 (input: Logic [4]) -> Logic [7]:
            ...     \"\"\"74LS48 八段管译码器 \"\"\"
            ...     bin_in = tuple(reversed(logic_in)) # 为方便我们改为高位在前
            ...     match bin_in:
            ...         case (False, False, False, False):  # 0
            ...             return Logic [7]("1111110")
            ...         case (False, False, False, True):  # 1
            ...             return Logic [7]("0110000")
            ...         case (False, False, True, False):  # 2
            ...             return Logic [7]("1101101")
            ...         case (False, False, True, True):  # 3
            ...             return Logic [7]("1111001")
            ...         case (False, True, False, False):  # 4
            ...             return Logic [7]("0110011")
            ...         case (False, True, False, True):  # 5
            ...             return Logic [7]("1011011")
            ...         case (False, True, True, False):  # 6
            ...             return Logic [7]("1011111")
            ...         case (False, True, True, True):  # 7
            ...             return Logic [7]("1110000")
            ...         case (True, False, False, False):  # 8
            ...             return Logic [7]("1111111")
            ...         case (True, False, False, True):  # 9
            ...             return Logic [7]("1111011")
            ...         case _:  # 非 BCD 输入（10-15），默认全部灭或空显示
            ...             return Logic [7]("0000000")
            >>> func = _LogicFunction [4, 7] (4, 7, decoder_7448)
            >>> func.sop()
            [[2, 3, 4, 5, 6, 8, 9], [0, 4, 5, 6, 8, 9], [0, 2, 6, 8], [0, 2, 3, 5, 6, 8, 9], [0, 1, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 7, 8, 9], [0, 2, 3, 5, 6, 7, 8, 9]]

        """
        self = _LogicFunction(
            self
        )  # 显式将子类转换为基类， 从而防止以 虚函数覆盖逻辑 调用其它成员而是使用类似 C++ 的命名隐藏逻辑
        truth_table = self.truth_table()
        _sop: list[list[int]] = [
            [] for _ in range(self._OUTPUT_WIDTH)
        ]  # 索引：输出的第 n 位，值：最小项
        for bit_i in range(self._OUTPUT_WIDTH):
            for input, output in truth_table.items():
                if output[bit_i]:
                    _sop[bit_i].append(int(input))
                continue
        return _sop

    def pos(self):
        """
        获取最大项之积表示

        Returns:
            list [list [int]]: 最大项之积表示，索引为输出的第 n 位，值为该位的最大项列表。
        """
        self = _LogicFunction(
            self
        )  # 显式将子类转换为基类， 从而防止 虚函数覆盖逻辑 调用其它成员而是使用类似 C++ 的命名隐藏逻辑
        truth_table = self.truth_table()
        _pos: list[list[int]] = [
            [] for _ in range(self._OUTPUT_WIDTH)
        ]  # 索引：输出的第 n 位，值：最大项
        for bit_i in range(self._OUTPUT_WIDTH):
            for input, output in truth_table.items():
                if not output[bit_i]:
                    _pos[bit_i].append(int(input))
        return _pos

    @typing.overload
    def simplified(self) -> list[tuple]: ...

    @typing.overload
    def simplified(
        self, fmt: LogicFunctionFormat[input_width, output_width]
    ) -> dict[str, tuple[str]]: ...

    def simplified(
        self, fmt: LogicFunctionFormat[input_width, output_width] | None = None
    ):
        """
        将最小项之和使用 QM 法化简

        Args:
            fmt (LogicFunctionFormat[input_width, output_width] | None): 格式化信息，默认为 None，不进行格式化（注意不是采用默认格式化）。

        Returns:
            list [tuple]: 化简结果，索引为输出的第 n 位，值为该位化简后的必要项。

        Examples:
            >>> def decoder_7448 (input: Logic [4]) -> Logic [7]:
            ...     \"\"\"74LS48 八段管译码器 \"\"\"
            ...     bin_in = tuple(reversed(logic_in)) # 为方便我们改为高位在前
            ...     match bin_in:
            ...         case (False, False, False, False):  # 0
            ...             return Logic [7]("1111110")
            ...         case (False, False, False, True):  # 1
            ...             return Logic [7]("0110000")
            ...         case (False, False, True, False):  # 2
            ...             return Logic [7]("1101101")
            ...         case (False, False, True, True):  # 3
            ...             return Logic [7]("1111001")
            ...         case (False, True, False, False):  # 4
            ...             return Logic [7]("0110011")
            ...         case (False, True, False, True):  # 5
            ...             return Logic [7]("1011011")
            ...         case (False, True, True, False):  # 6
            ...             return Logic [7]("1011111")
            ...         case (False, True, True, True):  # 7
            ...             return Logic [7]("1110000")
            ...         case (True, False, False, False):  # 8
            ...             return Logic [7]("1111111")
            ...         case (True, False, False, True):  # 9
            ...             return Logic [7]("1111011")
            ...         case _:  # 非 BCD 输入（10-15），默认全部灭或空显示
            ...             return Logic [7]("0000000")
            >>> func = _LogicFunction [4, 7] (4, 7, decoder_7448)
            >>> func.simplified()
            [('001-', '010-', '100-', '0-10'), ('010-', '01-0', '100-', '0-00'), ('0-10', '-000'), ('001-', '0101', '0-10', '100-', '00-0'), ('0--1', '01--', '-00-'), ('00--', '0-00', '0-11', '-00-'), ('0-1-', '01-1', '100-', '00-0')]
        """
        sop = self.sop()
        if fmt is None:
            _simplified: list[tuple] = [
                tuple() for _ in range(self._OUTPUT_WIDTH)
            ]  # 索引：输出的第 n 位，值：合并后的必要项
            for bit_i in range(self._OUTPUT_WIDTH):
                _simplified[bit_i] = quine_mccluskey(*sop[bit_i])
            return _simplified
        else:
            _simplified: dict[str, tuple[str]] = {}
            for bit_i in range(self._OUTPUT_WIDTH):
                _simplified.update(
                    quine_mccluskey(
                        *sop[bit_i],
                        width=self._INPUT_WIDTH,
                        fmt=fmt,
                        output_bit=bit_i,
                    )
                )
            return _simplified


def _extract_logic_width(type_hint: Any) -> int | None:
    """
    从类型提示中提取 Logic 类型的位宽参数

    Args:
        type_hint: 类型提示

    Returns:
        int | None: 位宽值，如果不是 Logic 类型则返回 None
    """
    # 检查是否是泛型类型
    origin = get_origin(type_hint)
    if origin is not None:
        # 处理泛型类型如 Logic[WIDTH]
        if hasattr(origin, "__name__") and origin.__name__ == "Logic":
            args = get_args(type_hint)
            if args and isinstance(args[0], int):
                return args[0]

    # 检查是否是直接的类型引用（在某些Python版本中）
    if hasattr(type_hint, "__name__") and type_hint.__name__ == "Logic":
        # 尝试从 __args__ 获取类型参数
        if hasattr(type_hint, "__args__") and type_hint.__args__:
            arg = type_hint.__args__[0]
            if isinstance(arg, int):
                return arg

    return None


def _get_logic_type_parameters(func: typing.Callable) -> Dict[str, Any]:
    """
    获取函数中输入输出 Logic 类型的类型参数（位宽）

    Args:
        func: 要分析的函数，**确保类型注解完备且返回值定长**

    Returns:
        Dict[str, Any]: 包含输入输出类型参数的字典，结构如下：

        {

            'inputs': {

                'param_name': width,  # 输入参数名 -> 位宽

            },

            'outputs': {


                'output_name': width,  # 输出名（单输出默认为 Y ） -> 位宽

            },

    Raises:
        TypeError: 当函数类型注解不完整时
    """
    result = {"inputs": {}, "outputs": {}}

    # 获取函数的类型提示
    type_hints = get_type_hints(func)

    # 获取函数签名
    sig = inspect.signature(func)

    # 分析输入参数
    for param_name, param in sig.parameters.items():
        if param_name in type_hints:
            param_type = type_hints[param_name]
            width = _extract_logic_width(param_type)
            if width is not None:
                result["inputs"][param_name] = width

    # 分析返回类型，由于我们面向解题，不用考虑性能问题，故直接传递一个参数试试

    # 生成一个合乎位宽的输入参数
    input_args = [Logic(0, width) for width in result["inputs"].values()]
    output = func(*input_args)

    if isinstance(output, dict):
        for output_name, output_value in output.items():
            if isinstance(output_value, Logic):
                result["outputs"][output_name] = output_value._WIDTH
            else:
                raise TypeError(
                    f"函数返回字典的值必须为 Logic 类型，实际为 {type(output_value)}"
                )

    elif isinstance(output, Logic):
        result["outputs"]["Y"] = output._WIDTH

    return result


def generate_logic_function_fmt(
    func: typing.Callable[[Logic], Logic],
) -> LogicFunctionFormat:
    """
    自动生成逻辑函数的格式化映射表。**注意：函数必须提供足够完整的类型注解且返回值定长！**

    Args:
        func (typing.Callable[[Logic], Logic]): 需要生成格式化映射表的逻辑函数

    Returns:
        LogicFunctionFormat: 生成的逻辑函数格式化映射表

    Raises:
        ValueError: 当无法解析函数的输入输出位宽时抛出。

    Examples:
        >>> def adder_2bit ( a: Logic [2], b: Logic [2], cin: Logic [1] ) -> dict[str, Logic [3]]:
        ...     total = a + b + cin
        ...     return {
        ...         "sum": total[0:2],
        ...         "carry": total[2:3]
        ...     }
        >>> fmt = generate_logic_function_fmt ( adder_2bit )
        >>> fmt
        (input_fmt={ range (0,2): "a", range (2,4): "b", range (4,5): "cin" }, output_fmt={ range (0,2): "sum", range (2,3): "carry" })
    """

    logic_function_io = _get_logic_type_parameters(func)

    input_fmt = {}
    width_exists = 0
    for name, width in logic_function_io["inputs"].items():
        input_fmt[range(width_exists, width_exists + width)] = name
        width_exists += width

    output_fmt = {}
    width_exists = 0
    for name, width in logic_function_io["outputs"].items():
        output_fmt[range(width_exists, width_exists + width)] = name
        width_exists += width

    return LogicFunctionFormat(input_fmt=input_fmt, output_fmt=output_fmt)


class FmtLogicFunction[input_width, output_width](
    _LogicFunction[input_width, output_width]
):
    """
    自动格式化逻辑函数类型 FmtLogicFunction ，自动生成格式化映射表、进行输入输出位宽检查，
    可以求取真值表、最小项之和、最大项之积及化简结果。

    ## type parameters:
        input_width (int): 输入信号的位宽。
        output_width (int): 输出信号的位宽。

    Attributes:
        _INPUT_WIDTH (int): 输入信号的位宽。
        _OUTPUT_WIDTH (int): 输出信号的位宽。
        _function (Callable [[Logic [input_width]], Logic [output_width]]): 逻辑函数的实现。
        _fmt (LogicFunctionFormat): 逻辑函数的格式化映射表。
        _unformatted_function (Callable [[Logic [input_width]], Logic [output_width]]): 未格式化的逻辑函数实现。用于__call__ 方法调用。

    ## Methods:
        __init__: 构造函数，设定输入输出位宽和逻辑函数实现。
        set_function: 设定逻辑函数的实现。
        __call__: 调用逻辑函数。
        truth_table: 生成逻辑函数的真值表。
        sop: 生成逻辑函数的最小项之和表示。
        simplified: 使用奎恩 - 麦克拉斯基法化简最小项之和表示。
    """

    _fmt: LogicFunctionFormat
    _unformatted_function: typing.Callable[[Logic[input_width]], Logic[output_width]]

    def __init__(
        self, function: typing.Callable[[Logic[input_width]], Logic[output_width]]
    ):
        """
        构造一个封装好的 FmtLogicFunction 对象

        Args:
            function (typing.Callable[[Logic[input_width]], Logic[output_width]]): 需要封装的逻辑函数。必须要有完整的类型注解且返回值定长。

        Raises:
            ValueError: 当无法解析函数的输入输出位宽时抛出。

        """
        fmt = generate_logic_function_fmt(function)
        input_width = sum(
            (_range.stop - _range.start) // _range.step
            for _range in fmt.input_fmt.keys()
        )
        output_width = sum(
            (_range.stop - _range.start) // _range.step
            for _range in fmt.output_fmt.keys()
        )
        formatted_function = _LogicFunctionFormatterFactory(fmt)(function)
        super().__init__(input_width, output_width, formatted_function)
        self._fmt = fmt
        self._unformatted_function = super()._WidthCheck(function)

    def __call__(self, *input):
        return self._function(*input)

    def truth_table(
        self,
    ) -> dict[Logic[input_width], Logic[output_width]]:
        re = super().truth_table(fmt=self._fmt)
        return re

    def simplified(
        self,
    ) -> list[tuple]:
        return super().simplified(fmt=self._fmt)

    def simp_pipeline(self):
        print(
            f"====== 逻辑函数 {self._unformatted_function.__name__} 化简流水线 ======"
        )
        print(f"truth_table():\n {self.truth_table()}")
        print(f"sop():\n {self.sop()}")
        print(f"simplified():\n {self.simplified()}")


def _test_qm():

    # 八段管转码
    print(
        "=========================== 八段管转码测试: ================================="
    )
    print("y6 +", quine_mccluskey(2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15))
    print("y6 -", quine_mccluskey(0, 1, 7, 12))
    print("y5 +", quine_mccluskey(0, 4, 5, 6, 8, 9, 10, 11, 12, 14, 15))
    print("y5 -", quine_mccluskey(1, 2, 3, 7, 13))
    print("y4 +", quine_mccluskey(0, 2, 6, 8, 10, 11, 12, 13, 14, 15))
    print("y3 +", quine_mccluskey(0, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14))
    print("y3 -", quine_mccluskey(1, 4, 7, 10, 15))
    print("y2 +", quine_mccluskey(0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13))
    print("y1 +", quine_mccluskey(0, 1, 2, 3, 4, 7, 8, 9, 10, 13))
    print("y1 -", quine_mccluskey(5, 6, 11, 12, 14, 15))
    print("y0 +", quine_mccluskey(0, 2, 3, 5, 6, 7, 8, 9, 10, 12, 14, 15))
    print("y0 -", quine_mccluskey(1, 4, 11, 13))


def _test_logic():

    print(
        "\n============================ Logic 测试 ===================================="
    )

    F = False
    T = True
    # Logic.set_fmt_radix(10)
    logic_a = Logic[8](140)
    logic_b = Logic[8](70, 8)
    print("a:", logic_a)
    print("b:", logic_b)
    print("a and b:", logic_a & logic_b)
    print("a or b:", logic_a | logic_b)
    print("a xor b:", logic_a ^ logic_b)
    print("a + b:", logic_a + logic_b)
    print("a - b:", logic_a - logic_b)
    print("a * b:", logic_a * logic_b)
    print("a //b:", logic_a // logic_b)
    print("a [0]:", logic_a[0])
    print("a [1:8:2]:", logic_a[1:8:2])

    print(
        "\n================================== 逻辑函数化简测试 ====================================="
    )

    def wire_count(logic_in: Logic[4]):
        """信号计数"""
        return Logic[3](logic_in.count(T), 3)

    FmtLogicFunction[4, 3](
        wire_count,
    ).simp_pipeline()

    def decoder_7448(logic_in: Logic[4]) -> Logic[7]:
        """7448 译码器"""
        bin_in = tuple(reversed(logic_in))
        match bin_in:
            case (False, False, False, False):  # 0
                return Logic[7]("1111110")
            case (False, False, False, True):  # 1
                return Logic[7]("0110000")
            case (False, False, True, False):  # 2
                return Logic[7]("1101101")
            case (False, False, True, True):  # 3
                return Logic[7]("1111001")
            case (False, True, False, False):  # 4
                return Logic[7]("0110011")
            case (False, True, False, True):  # 5
                return Logic[7]("1011011")
            case (False, True, True, False):  # 6
                return Logic[7]("1011111")
            case (False, True, True, True):  # 7
                return Logic[7]("1110000")
            case (True, False, False, False):  # 8
                return Logic[7]("1111111")
            case (True, False, False, True):  # 9
                return Logic[7]("1111011")
            case _:  # 非 BCD 输入（10-15），默认全部灭或空显示
                return Logic[7]("0000000")

    FmtLogicFunction[4, 7](decoder_7448).simp_pipeline()

    def reverse(logic_in: Logic[4]) -> Logic[4]:
        """4 位信号反转"""
        return Logic[4](int(logic_in[::-1]), 4)

    FmtLogicFunction[4, 4](reverse).simp_pipeline()

    @FmtLogicFunction[4, 3]
    def adder_2bit(a: Logic[2], b: Logic[2]):
        """2 位加法器"""
        carry, *sum = a + b  # 注意 *sum 是 list[bool], carry 是 bool
        return {"sum": Logic[2](sum), "cout": Logic[1](carry)}

    adder_2bit.simp_pipeline()

    print(f"xor pos: {_LogicFunction[2, 1](2, 1, lambda x: x[0:1] ^ x[1:2]).pos()}")

    def encoder(IN: Logic[4]) -> Logic[2]:
        """4 - 2 位低位优先编码器"""
        for i in range(0, 4):
            if IN[i]:
                return Logic[2](i, 2)
        return Logic[2](0, 2)

    FmtLogicFunction[4, 2](encoder).simp_pipeline()

    @FmtLogicFunction[3, 2]
    def gray_counter(X: Logic[3]) -> Logic[2]:
        """格雷码计数器"""
        match tuple(reversed(X)):
            case (False, False, False):
                return Logic[3](1, 3)
            case (False, False, True):
                return Logic[3](3, 3)
            case (False, True, True):
                return Logic[3](2, 3)
            case (False, True, False):
                return Logic[3](6, 3)
            case (True, True, False):
                return Logic[3](7, 3)
            case (True, True, True):
                return Logic[3](5, 3)
            case (True, False, True):
                return Logic[3](4, 3)
            case (True, False, False):
                return Logic[3](0, 3)
            
    gray_counter.simp_pipeline()

    # @FmtLogicFunction[9,5]
    # def GPS_radix10(a:Logic[4],b:Logic[4],Cin:Logic[1]):
    #     """十进制 GPS"""
    #     G = Logic[1](0)
    #     P = Logic[1](0)
    #     if(int(a + b) == 9):
    #         G = Logic[1](0)
    #         P = Logic[1](1)
    #     if(int(a + b) > 9):
    #         G = Logic[1](1)
    #         P = Logic[1](0)
    #     S = (a + b + Cin)[0:4]
    #     return {"G":G,"P":P,"S":S,"Cout":G | (P & Cin)}

    # GPS_radix10.simp_pipeline()
        

    with open("__pycache__/RS时序转换.txt", "w") as f:
        print(
            "++++++++++++++++++++++++++++++RS 锁存器 ( NAND 实现 )++++++++++++++++++++++++++++++++++++++",
            file=f,
        )
        for i in range(4):
            R, S = Logic[2](i, 2)  # 解包，等价于 assign {R,S} = i (verilog)
            print(f"\n=== R={R},S={S} ===", file=f)
            for j in range(4):
                Q, Qn = Logic[2](j, 2)
                print(f"\nInitial Q={Q},Qn={Qn}\n", file=f)
                for i in range(3):
                    print(f"t{i} Q={Q},Qn={Qn} => ", end="", file=f)
                    Q, Qn = not (R and Qn), not (
                        S and Q
                    )  # python 的非阻塞赋值， 相当于 Q <= R ~& Qn; Qn <= S ~& Q; (verilog)
                    print(f" Q={Q},Qn={Qn}", file=f)


def _main():
    pass
    _test_qm()
    _test_logic()


if __name__ == "__main__":
    _main()
