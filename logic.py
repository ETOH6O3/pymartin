"""
逻辑函数模块 Logic Function Module
===

包含逻辑信号类型 Logic 和逻辑函数类型 LogicFunction 的定义与实现。

更新日志
---
- 2024-07-10: 实现奎恩 - 麦克拉斯基法化简逻辑函数，模块名称暂为 quine_mccluskey
- 2025-10-25: 逻辑函数化简重磅升级！加入了 Logic 和 LogicFunction 类，全面支持面向对象编程，用户可以自定义逻辑函数并获取真值表、 sop 和化简结果
"""
import typing
import functions

def quine_mccluskey(*minterms_dec):
    """
    使用奎恩 - 麦克拉斯基法化简逻辑函数。

    Args:
        *minterms_dec (int): 最小项编码，十进制

    Returns:
        tuple: 所有必要乘积项的二进制表示

    Raises:
        无

    Exaples:
        >>> quine_mccluskey (0, 1, 3, 5, 7)
        ... ('--1', '00-')
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
    max_length: int = max(len(d) for d in minterms)

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
            return tuple(results)


class Logic[WIDTH: int = 32]:
    """
    # 逻辑信号类型 Logic 
    - 完全由 bool 值组成（不存在不定态 x 和高组态 z）
    - 支持位运算和算术运算（按无符号数进行运算）。
    - 运算时严格进行位宽检查。
    - 相当于 systemverilog 里的 logic 类型。

    ## type parameters:
        WIDTH (int): 信号的位宽，默认为 32 位。

    Attributes:
        _bits (bool): 各个位的布尔值，低位在前。
        _width (int | None): 信号位宽。用于位宽检查。

    ## Methods:
        __init__: 构造函数，支持多种构造方式。
        __repr__: 返回对象的字符串表示。
        __str__: 返回信号的二进制字符串表示。
        __int__: 返回信号的整数值。
        位运算方法: __and__, __or__, __xor__, __invert__, __lshift__, __rshift__, 以及对应的就地运算方法。
        算术运算方法: __neg__, __pos__, __add__, __sub__, __mul__, __floordiv__
        容器方法: __len__, __getitem__, __setitem__, __iter__, __reversed__
    

    """

    _bits: list[bool]
    _WIDTH: int

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

        ### 参数包构造
        
        #### Args:
            *bits: 可变参数，根据参数类型和数量进行不同的构造方式。
            
        ## Raises:
            TypeError: 当构造参数不符合任何一种方式时抛出。

        ## Examples:

            >>> Logic[1] ()                # 默认构造
            Logic(0b0)
            >>> Logic[1] (True)            # 布尔值构造
            Logic(0b1)
            >>> Logic[8] ('11010010')      # 字符串构造
            Logic(0b11010010)
            >>> Logic[8] (10)             # 整型构造，自适应位宽
            Logic(0b1010)
            >>> Logic[8] (10, 8)           # 整型构造，指定位宽
            Logic(0b00001010)
            >>> Logic[4] (True, False, True, False)  # 参数包构造
            Logic(0b1010)
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

        elif len(bits) == 2 and all(
            isinstance(b, int) for b in bits
        ):  # 指定位宽的整型构造
            temp: Logic[WIDTH] = Logic[WIDTH](bin(bits[0])[2:].zfill(bits[1]))
            self._bits = temp._bits
            self._WIDTH = temp._WIDTH

        elif all(isinstance(b, bool) for b in bits):  # 参数包构造（低位在前）
            self._bits = list(bits)
            self._WIDTH = len(bits)

        else:  # 非法构造
            raise TypeError("非法构造")

    def __repr__(self) -> str:
        return f"Logic({str (self)})"

    def __str__(self):
        """
        转为字符串。注意存在前缀 0b

        ## Examples:

            >>> str (Logic[4] (10))
            '0b1010'
            >>> str (Logic[8] ('11010010'))
            '0b11010010'
        """
        return f"0b{''.join (['1' if b else '0' for b in reversed (self._bits)])}"

    def __int__(self):
        """
        
        转为整数。视为无符号数。
        
        ## Examples:

            >>> int (Logic[4] (10))
            10
            >>> int (Logic[8] ('11010010'))
            210 
        """
        return int(str(self), 2)

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

    def __iand__(self, other: "Logic [WIDTH]") -> "Logic [WIDTH]":
        if other._WIDTH != self._WIDTH:
            raise ValueError(
                f"位宽不匹配，左操作数宽度为 {self._WIDTH}，右操作数宽度为 {other._WIDTH}"
            )
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        self._bits = [a and b for a, b in zip(self._bits, other._bits)]
        return self

    def __ior__(self, other: "Logic [WIDTH]") -> "Logic [WIDTH]":
        if other._WIDTH != self._WIDTH:
            raise ValueError(
                f"位宽不匹配，左操作数宽度为 {self._WIDTH}，右操作数宽度为 {other._WIDTH}"
            )
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        self._bits = [a or b for a, b in zip(self._bits, other._bits)]
        return self

    def __ixor__(self, other: "Logic [WIDTH]") -> "Logic [WIDTH]":
        if other._WIDTH != self._WIDTH:
            raise ValueError(
                f"位宽不匹配，左操作数宽度为 {self._WIDTH}，右操作数宽度为 {other._WIDTH}"
            )
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        self._bits = [a ^ b for a, b in zip(self._bits, other._bits)]
        return self

    def __ilshift__(self, shamt: int) -> "Logic [WIDTH]":
        if shamt < 0:
            raise ValueError("左移位数必须为非负整数")
        self._bits = ([False] * shamt + self._bits)[:WIDTH]
        return self

    def __irshift__(self, shamt: int) -> "Logic [WIDTH]":
        if shamt < 0:
            raise ValueError("右移位数必须为非负整数")
        self._bits = self._bits[shamt:] + [False] * shamt
        return self

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
        int_self = int(str(self), base=2)
        int_other = int(str(other), base=2)
        return Logic(
            *reversed([(bit == "1") for bit in bin(int_self + int_other)[2::]])
        )

    def __sub__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=2)
        int_other = int(str(other), base=2)
        return Logic(
            *reversed([(bit == "1") for bit in bin(int_self - int_other)[2::]])
        )

    def __mul__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=2)
        int_other = int(str(other), base=2)
        return Logic(
            *reversed([(bit == "1") for bit in bin(int_self * int_other)[2::]])
        )

    def __floordiv__(self, other: "Logic") -> "Logic":
        if not all(isinstance(b, bool) for b in other._bits):
            raise ValueError("运算对象必须为 Logic 类型")
        int_self = int(str(self), base=2)
        int_other = int(str(other), base=2)
        return Logic(
            *reversed([(bit == "1") for bit in bin(int_self // int_other)[2::]])
        )

    # ============================== 容器 ====================================
    def __len__(self) -> int:
        return len(self._bits)

    def __getitem__(self, item: int) -> bool:
        return self._bits[item]

    def __setitem__(self, item: int, value: bool):
        self._bits[item] = value

    def __iter__(self):
        return iter(self._bits)

    def __reversed__(self):
        return Logic[WIDTH](*reversed(self._bits))


class LogicFunction[input_width, output_width]:
    """
    逻辑函数类型 LogicFunction

    ## type parameters:
        input_width (int): 输入信号的位宽。
        output_width (int): 输出信号的位宽。

    Attributes:
        _INPUT_WIDTH (int): 输入信号的位宽。
        _OUTPUT_WIDTH (int): 输出信号的位宽。
        _function (Callable[[Logic[input_width]], Logic[output_width]]): 逻辑函数的实现。

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

        return wrapper

    def __init__(
        self,
        input_width: int,
        output_width: int,
        function: typing.Callable[[Logic[input_width]], Logic[output_width]],
    ):
        """
        构造函数，设定输入输出位宽和逻辑函数实现。

        Note:
            - 逻辑函数无需用户定义输入输出位宽检查，已由类自动处理
        """

        self._INPUT_WIDTH = input_width
        self._OUTPUT_WIDTH = output_width
        self._function = self._WidthCheck(function)

    def set_function(
        self, function: typing.Callable[[Logic[input_width]], Logic[output_width]]
    ):
        """
        设定逻辑函数的实现。

        Note:
            - 逻辑函数无需用户定义输入输出位宽检查，已由类自动处理
        """
        self._function = self._WidthCheck(function)

    def __call__(self, input: Logic[input_width]) -> Logic[output_width]:
        """
        强制检查输入输出位宽后，调用逻辑函数。

        Examples:
            >>> def example_func (input: Logic[2]) -> Logic[1]:
            ...     return Logic[1] (input[0] or input[1]) # 或运算
            >>> func = LogicFunction[2, 1] (2, 1, example_func)
            >>> func (Logic[2] (0, 1))
            Logic(0b1)
            >>> func (Logic[2] (0, 0))
            Logic(0b0)
        """
        return self._function(input)

    def truth_table(self):
        """
        获取真值表

        Returns:
            dict[Logic[input_width], Logic[output_width]]: 真值表，键为输入，值为对应输出。

        Examples:
            >>> def example_func (input: Logic[4]) -> Logic[3]:
            ...     \"\"\"信号计数\"\"\"
            ...     return Logic[4](str(input).count("1"))
            >>> func = LogicFunction[4, 3] (4, 3, example_func)
            >>> func.truth_table()
            {Logic(0b0000): Logic(0b000), Logic(0b0001): Logic(0b001), Logic(0b0010): Logic(0b001), Logic(0b0011): Logic(0b010), Logic(0b0100): Logic(0b001), Logic(0b0101): Logic(0b010), Logic(0b0110): Logic(0b010), Logic(0b0111): Logic(0b011), Logic(0b1000): Logic(0b001), Logic(0b1001): Logic(0b010), Logic(0b1010): Logic(0b010), Logic(0b1011): Logic(0b011), Logic(0b1100): Logic(0b010), Logic(0b1101): Logic(0b011), Logic(0b1110): Logic(0b011), Logic(0b1111): Logic(0b100)}
            
        """
        _truth_table: dict[Logic[input_width], Logic[output_width]] = {}
        for i in range(0, 2**self._INPUT_WIDTH):
            input = Logic[input_width](i, self._INPUT_WIDTH)
            _truth_table[input] = self(input)
        return _truth_table

    def sop(self):
        """
        获取最小项之和表示

        Returns:
            list[list[int]]: 最小项之和表示，索引为输出的第 n 位，值为该位的最小项列表。

        Examples:
            >>> def decoder_7448 (input: Logic[4]) -> Logic[7]:
            ...     \"\"\"74LS48 八段管译码器\"\"\"
            ...     match str(input)[2:]: # 去掉 0b 前缀
            ...         case "0000": return Logic[7] ("1111110") # 显示 0
            ...         case "0001": return Logic[7] ("0110000") # 显示 1
            ...         case "0010": return Logic[7] ("1101101") # 显示 2
            ...         case "0011": return Logic[7] ("1111001") # 显示 3
            ...         case "0100": return Logic[7] ("0110011") # 显示 4
            ...         case "0101": return Logic[7] ("1011011") # 显示 5
            ...         case "0110": return Logic[7] ("1011111") # 显示 6
            ...         case "0111": return Logic[7] ("1110000") # 显示 7
            ...         case "1000": return Logic[7] ("1111111") # 显示 8
            ...         case "1001": return Logic[7] ("1111011") # 显示 9
            ...         case _: return Logic[7] ("0000000")   # 其他情况不显示
            >>> func = LogicFunction[4, 7] (4, 7, decoder_7448)
            >>> func.sop()
            [[2, 3, 4, 5, 6, 8, 9], [0, 4, 5, 6, 8, 9], [0, 2, 6, 8], [0, 2, 3, 5, 6, 8, 9], [0, 1, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 7, 8, 9], [0, 2, 3, 5, 6, 7, 8, 9]]
        
        """
        truth_table = self.truth_table()
        _sop: list[list[int]] = [
            [] for _ in range(self._OUTPUT_WIDTH)
        ]  # 索引：输出的第 n 位，值：最小项
        for bit_i in range(self._OUTPUT_WIDTH):
            for input, output in truth_table.items():
                if output[bit_i]:
                    _sop[bit_i].append(int(input))
        return _sop

    def simplified(self):
        """
        将最小项之和使用 QM 法化简
        
        Returns:
            list[tuple]: 化简结果，索引为输出的第 n 位，值为该位化简后的必要项。
        
        Examples:
            >>> def decoder_7448 (input: Logic[4]) -> Logic[7]:
            ...     \"\"\"74LS48 八段管译码器\"\"\"
            ...     match str(input)[2:]: # 去掉 0b 前缀
            ...         case "0000": return Logic[7] ("1111110") # 显示 0
            ...         case "0001": return Logic[7] ("0110000") # 显示 1
            ...         case "0010": return Logic[7] ("1101101") # 显示 2
            ...         case "0011": return Logic[7] ("1111001") # 显示 3
            ...         case "0100": return Logic[7] ("0110011") # 显示 4
            ...         case "0101": return Logic[7] ("1011011") # 显示 5
            ...         case "0110": return Logic[7] ("1011111") # 显示 6
            ...         case "0111": return Logic[7] ("1110000") # 显示 7
            ...         case "1000": return Logic[7] ("1111111") # 显示 8
            ...         case "1001": return Logic[7] ("1111011") # 显示 9
            ...         case _: return Logic[7] ("0000000")   # 其他情况不显示
            >>> func = LogicFunction[4, 7] (4, 7, decoder_7448)
            >>> func.simplified()
            [('001-', '010-', '100-', '0-10'), ('010-', '01-0', '100-', '0-00'), ('0-10', '-000'), ('001-', '0101', '0-10', '100-', '00-0'), ('0--1', '01--', '-00-'), ('00--', '0-00', '0-11', '-00-'), ('0-1-', '01-1', '100-', '00-0')]
        """
        sop = self.sop()
        _simplified: list[tuple] = [
            tuple() for _ in range(self._OUTPUT_WIDTH)
        ]  # 索引：输出的第 n 位，值：合并后的必要项
        for bit_i in range(self._OUTPUT_WIDTH):
            _simplified[bit_i] = quine_mccluskey(*sop[bit_i])
        return _simplified


def test_qm():
    print(quine_mccluskey(0, 2, 3, 8, 10, 14, 15, 22, 24, 27, 31))
    print(quine_mccluskey(0, 1, 4, 5, 7))
    print(quine_mccluskey(1, 2, 4, 7, 8, 11, 13, 14))
    print(quine_mccluskey(1, 4, 6, 8, 9, 10, 11, 15))

    # 新增测试
    print("\n===== 新增测试 =====")

    # 2. 单个最小项测试
    print("单个最小项测试:", quine_mccluskey(0))  # 预期: ('0',)

    # 3. 两个相邻最小项测试
    print("两个相邻最小项测试:", quine_mccluskey(0, 1))  # 预期: ('-',)

    # 4. 四个角最小项测试 (完全合并)
    print("四个角最小项测试:", quine_mccluskey(0, 2, 8, 10))  # 预期: ('-0-0',)

    # 5. 所有最小项测试 (完全合并)
    print("所有最小项测试:", quine_mccluskey(0, 1, 2, 3, 4, 5, 6, 7))  # 预期: ('---',)

    # 6. 非相邻最小项测试 (无法合并)
    print("非相邻最小项测试:", quine_mccluskey(0, 3))  # 预期: ('00', '11')

    # 7. 奇数个最小项测试
    print("奇数个最小项测试:", quine_mccluskey(0, 1, 3, 5, 7))  # 预期: ('--1', '00-')

    # 8. 大数值最小项测试
    print(
        "大数值最小项测试:", quine_mccluskey(255, 256)
    )  # 预期: ('011111111', '100000000')

    # 9. 混合长度最小项测试
    print(
        "混合长度最小项测试:", quine_mccluskey(1, 3, 10, 42)
    )  # 预期: ('00001', '00011', '01010', '101010')

    # 10. 重复最小项测试
    print("重复最小项测试:", quine_mccluskey(0, 0, 1, 1))  # 预期: ('-',)

    # 11. 典型卡诺图测试 1 (形成方形)
    print("典型卡诺图测试 1:", quine_mccluskey(0, 1, 4, 5))  # 预期: ('-0-',)

    # 12. 典型卡诺图测试 2 (形成条状)
    print("典型卡诺图测试 2:", quine_mccluskey(2, 3, 6, 7))  # 预期: ('-1-',)

    # 13. 复杂合并测试
    print(
        "复杂合并测试:",
        quine_mccluskey(
            42,
            187,
            93,
            231,
            15,
            76,
            200,
            119,
            3,
            156,
            244,
            67,
            178,
            99,
            21,
            135,
            55,
            210,
            33,
            168,
        ),
    )
    # 预期:
    # ('00101010', '10111011', '01011101', '11100111', '00001111', '01001100', '11001000',
    # '0-110111', '0-000011', '10011100', '11110100', '10110010', '01-00011', '00010101',
    # '10000111', '11010010', '00100001', '10101000')

    # 八段管转码
    print("八段管转码测试:")
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


def test_logic():
    F = False
    T = True
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

    def logic_function_simp_pipeline(func: LogicFunction, func_name_: str = "logic_function"):
        print(f"\n======逻辑函数{func_name_}化简流水线======")
        print(f"\nfunc.truth_table():\n{func.truth_table()}\n")
        print(f"func.sop():\n{func.sop()}\n")
        print(f"func.simplified():\n{func.simplified()}\n")

    def wire_count(logic_in: Logic[4]):
        """信号计数"""
        return Logic[3](str(logic_in).count("1"), 3)
    logic_function_simp_pipeline(LogicFunction[4, 3](4, 3, wire_count), "wire_count")

    def decoder_7448(logic_in: Logic[4]) -> Logic[7]:
        """7448译码器"""
        bin_in = str(logic_in)[2:].zfill(4)
        match bin_in:
            case "0000":  # 0
                return Logic[7]("1111110")
            case "0001":  # 1
                return Logic[7]("0110000")
            case "0010":  # 2
                return Logic[7]("1101101")
            case "0011":  # 3
                return Logic[7]("1111001")
            case "0100":  # 4
                return Logic[7]("0110011")
            case "0101":  # 5
                return Logic[7]("1011011")
            case "0110":  # 6
                return Logic[7]("1011111")
            case "0111":  # 7
                return Logic[7]("1110000")
            case "1000":  # 8
                return Logic[7]("1111111")
            case "1001":  # 9
                return Logic[7]("1111011")
            case _:  # 非 BCD 输入（10-15），默认全部灭或空显示
                return Logic[7]("0000000")
    logic_function_simp_pipeline(LogicFunction[4, 7](4, 7, decoder_7448), "decoder_7448")


def main():
    pass
    test_qm()
    test_logic()


if __name__ == "__main__":
    main()
