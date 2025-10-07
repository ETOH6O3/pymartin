"""

模块概述
----------------------
本模块提供了一系列实用的辅助函数

函数概览
----------------------
0. 谓词
   - is_odd,is_even    : 判断奇偶性
   - is_prime_num       : 判断是否为质数
   - is_divisible_by,is_indivisible_by  : 判断可否整除
   - is_perfect_num     : 判断是否是完美数
   - is_n_decimal       : 验证浮点数小数位数
   - is_comparable  : 检查变量可比性
   - is_iterable          : 判断对象可迭代性

1. 数值
   - sieve_primes   : 筛选范围内所有质数
   - factoring      : 因式分解
   - divisors       : 查找因数
   - nth_prime_num  : 第 n 个质数

2. 输入处理
   - restricted_input          : 带内容限制的输入
   - restricted_input_with_timeout: 带时间和内容限制的输入（异步）

3. 字符串操作
   - multisplit   : 多分隔符分割
   - replace_pro           : 增强版字符串替换
   - diff_char       : 计算字符串差异
   - replace_diff    : 生成差异标记字符串

4. 流程控制
   - do_while : do-while 循环实现

5. 数据生成
   - multiplication_table     : 生成乘法表
   - enumerate_comb       : 枚举所有组合
   - enumerate_perm         : 枚举所有排列

"""

import asyncio
import sys
import re
import typing
import collections
import enum
import itertools

if __name__ == "__main__":
    import time
    from pipe import *


def is_odd(num: int) -> bool:
    """
    判断一个整数是不是奇数

    Returns:
        bool: 对象是奇数则为真，为偶数则为假

    Examples:
        >>> is_odd (33550336)
        False
        >>> is_odd (33550335)
        True
    """

    return bool(num & 0b1)


def is_even(num: int) -> bool:
    """
    判断一个整数是不是偶数

    Returns:
        bool: 对象是偶数则为真，为奇数则为假

    Examples:
        >>> is_even (33550336)
        True
        >>> is_even (33550335)
        False
    """

    return not bool(num & 0b1)


def is_divisible_by(divisor: int):
    """
    工厂函数，生成判断一个数可否被 divisor 整除的函数。

    Args:
        divisor: 除数

    Returns:
        function: 判断给定的被除数是否能被 divisor 整除

    Examples:
        >>> from martin.pipe import *
        >>> pipe (range (10))
        ... |pfilter ( is_divisible_by (3) )
        ... |list
        ... |print
        [0, 3, 6, 9]

    """

    def is_divisible_by_divisor(dividend: int):
        return not bool(dividend % divisor)

    return is_divisible_by_divisor


def is_indivisible_by(divisor: int):
    """
    工厂函数，生成判断一个数是否不能被 divisor 整除的函数。

    Args:
        divisor: 除数

    Returns:
        function: 判断给定的被除数是否不能被 divisor 整除

    Examples:
        >>> from martin.pipe import *
        >>> pipe (range (10))
        ... |pfilter ( is_indivisible_by (3) )
        ... |list
        ... |print
        [1, 2, 4, 5, 7, 8]
    """

    def is_indivisible_by_divisor(dividend: int):
        return bool(dividend % divisor)

    return is_indivisible_by_divisor


def sieve_primes(limit: int):
    """
    使用埃拉托斯特尼筛法筛选出小于等于给定限制的所有质数。

    Args:
        limit: 筛选质数的上限。

    Returns:
        List [int]: 包含所有小于等于给定限制的质数的列表。

    """
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_p in enumerate(sieve) if is_p]


if __name__ == "__main__":
    start = time.time()

# 先使用埃拉托斯特尼筛法预筛选 10000 以内质数
_prime_nums: list[int] = sieve_primes(10000)

if __name__ == "__main__":
    end = time.time()
    print(f"_prime_nums 初始化耗时: {end - start:.4f} 秒")


def is_prime_num(n: int) -> bool:
    """
    判断一个整数是否为质数。

    Args:
        n: 需要判断的整数。

    Returns:
        bool: 如果 n 是质数，则返回 True；否则返回 False。

    """

    # 扩充_prime_nums 直到 n 在覆盖范围内
    while _prime_nums[-1] < n:
        num += 1
        # 除了 2 和 3 之外，所有的质数都分布在 6 的倍数附近
        if num % 6 not in (1, 5):
            continue
        # 判断 num 是否为质数
        is_prime = True
        for p in _prime_nums:
            if p * p > num:
                break
            if num % p == 0:
                is_prime = False
                break
        if is_prime:
            _prime_nums.append(num)
    return n in _prime_nums


def factoring(num: int):
    """
    将整数 num 进行因式分解，返回其所有素因子（允许重复）。

    Args:
        num: 需要分解的整数。

    Returns:
        List [int]: num 的所有素因子（从小到大，允许重复）。

    Examples:
        >>> factoring (12)
        [2, 2, 3]
        >>> factoring (97)
        [97]
    """
    if num < 2:
        return []
    factors = []
    # 扩充_prime_nums 直到最大素数大于等于 sqrt (n)
    max_needed = int(num**0.5) + 1
    last_prime = _prime_nums[-1]
    candidate = last_prime
    while last_prime < max_needed:
        candidate += 1
        if candidate % 6 not in (1, 5):
            continue
        is_prime = True
        for p in _prime_nums:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            _prime_nums.append(candidate)
        last_prime = _prime_nums[-1]
    # 查找素因子
    for p in _prime_nums:
        if p * p > num:
            break
        while num % p == 0:
            factors.append(p)
            num //= p
    if num > 1:
        factors.append(num)
    return factors


def divisors(num: int) -> list[int]:
    """
    查找一个正整数的所有因数

    Args:
        num: 要查找因数的正整数

    Returns:
        List [int]: 所有因数（从小到大）

    Examples:
        >>> proper_divisors (12)[:-1] # 查找真因数
        [1, 2, 3, 4, 6, 12]
        >>> proper_divisors (13) # 查找因数
        [1, 13]
    """
    if num <= 1:
        return []
    factors = factoring(num)
    factor_count = collections.Counter(factors)
    # 构造每个素因子的所有可能幂次
    # e.g. Counter({2: 2, 3: 1, 19: 1}) -> [[1, 2, 4], [1, 3], [1, 19]]
    powers = [[p**e for e in range(count + 1)] for p, count in factor_count.items()]
    # 枚举所有组合
    result = set()
    for combo in itertools.product(*powers):
        # 求combo累乘
        prod = 1
        for x in combo:
            prod *= x
        result.add(prod)
    return sorted(result)


def is_perfect_num(num: int):
    # 完全数都是以 6 或 8 结尾。如果以 8 结尾，那么就肯定是以 28 结尾。
    if num % 100 != 28 and num % 10 != 6:
        return False
    else:
        # 完全数的二进制表示都是前 1 后 0 且 1 的数目比 0 多 1
        bin_num = bin(num)[2:]
        if len(bin_num) % 2:
            half = len(bin_num) // 2 + 1
            if (
                bin_num[:half] == "1" * half
                and bin_num[half:]
                == "0" * (len(bin_num) - half)  # 是诸如 0b1111000 的格式
                and sum(divisors(num)[:-1]) == num  # 真因数和为本身
            ):
                return True

            else:  # 不是诸如 0b1111000 的格式 或 真因数和不为本身
                return False
        else:  # 二进制表示长度为偶数，完全不可能是诸如 0b1111000 的格式
            return False


def nth_prime_num(n: int) -> int:
    """
    返回第 n 个质数。

    Args:
        n: 质数的序号，从 1 开始计数。

    Returns:
        int: 第 n 个质数。

    Raises:
        ValueError: 如果 n 不是正数，则抛出异常。

    """
    if n <= 0:
        raise ValueError(f"n 必须是正数，实际值：{n}")
    try:
        return _prime_nums[n - 1]
    except IndexError:  # 超出覆盖范围
        num = _prime_nums[-1]
        while len(_prime_nums) < n:
            num += 1
            # 除了 2 和 3 之外，所有的质数都分布在 6 的倍数附近
            if num % 6 not in (1, 5):
                continue
            # 判断 num 是否为质数
            is_prime = True
            for p in _prime_nums:
                if p * p > num:
                    break
                if num % p == 0:
                    is_prime = False
                    break
            if is_prime:
                _prime_nums.append(num)

        return _prime_nums[n - 1]


def is_n_decimal(num: float, n: int) -> bool:
    """
    判断一个浮点数是否最多有 n 位小数（忽略末尾的 0）。

    Args:
        num: 待判断的浮点数
        n: 期望的最大小数位数，允许小于 0（判断整数末尾的 0 的数目）

    Returns:
        如果数字的小数位数不超过 n 则返回 True，否则返回 False

    Examples:
        >>> is_n_decimal (1.23450, 4)
        True
        >>> is_n_decimal (1.23456, 4)
        False
    """

    # 处理浮点数精度问题
    factor = 10**n
    abs_num = abs(num)
    return abs(abs_num * factor - round(abs_num * factor)) < 1e-8


def is_comparable(var1: typing.Any, var2: typing.Any) -> bool:
    """
    判断两个变量是否可以安全地进行比较操作。

    Args:
        var1: 第一个变量
        var2: 第二个变量

    Returns:
        如果两个变量支持比较操作返回 True，否则返回 False

    Examples:
        >>> is_comparable (10, 20)
        True
        >>> is_comparable (10, "20")
        False
    """
    try:
        # 测试两种基本比较操作
        var1 == var2
        var1 > var2
        return True
    except TypeError:
        return False


def is_iterable(obj):
    """
    判断传入的对象是否为可迭代对象。

    Args:
        obj: 需要判断的对象。

    Returns:
        如果对象为可迭代对象，则返回 True；否则返回 False。

    Raises:
        无

    Examples:

        >>> print (is_iterable ([1, 2, 3]))
        True
        >>> print (is_iterable ("hello"))
        True
        >>> print (is_iterable (42))
        False
    """
    return isinstance(obj, collections.abc.Iterable)


class ErrorMethod(enum.IntEnum):
    """
    为 restricted_input 定义的错误处理策略的枚举类

    Attributes:
        REENTER (int:0): 发生错误时重新尝试操作
        EXIT    (int:1): 发生错误时直接退出程序
        RAISE   (int:2): 发生错误时抛出异常

    """

    REENTER = 0
    EXIT = 1
    RAISE = 2


def restricted_input(
    prompt: object = "",
    min_length: int = 0,
    max_length: int = -1,
    valid_list: typing.Optional[typing.Sequence[str]] = None,
    invalid_prompt: str = "非法输入！",
    error_method: ErrorMethod = ErrorMethod.REENTER,
    predicate: typing.Callable[[str], bool] = lambda s: True,
) -> str:
    """
    获取受限制的用户输入（支持长度、允许值列表和自定义验证）

    Args:
        prompt: 输入提示信息
        min_length: 最小输入长度（非正数表示无限制）
        max_length: 最大输入长度（负数表示无限制）
        valid_list: 允许的输入值列表（None 表示无限制）
        invalid_prompt: 非法输入时的提示信息
        error_method: 错误处理方式（ErrorMethod.REENTER 即 0 = 重新输入, ErrorMethod.EXIT 即 1 = 退出程序, ErrorMethod.RAISE 即 2 = 抛出异常）
        predicate: 自定义验证函数（输入字符串返回布尔值）

    Returns:
        符合要求的用户输入字符串

    Raises:
        ValueError: 当 error_method 值无效时
        ValueError: 当 error_method=2 且输入非法时
        SystemExit: 当 error_method=1 且输入非法时

    Examples:
        >>> # 要求输入长度在 3-6 之间的字母
        >>> value = restricted_input (
        ...     "请输入:",
        ...     min_length=3,
        ...     max_length=6,
        ...     predicate=lambda s: s.isalpha ()
        ... )
    """
    # 参数验证
    if error_method not in (0, 1, 2):
        raise ValueError("error_method 只能是 0, 1 或 2")

    valid_set = set(valid_list) if valid_list is not None else None
    current_prompt = prompt

    while True:
        try:
            user_input = input(current_prompt)
        except EOFError:
            user_input = ""

        # 验证输入
        errors = []
        if min_length > 0 and len(user_input) < min_length:
            errors.append(f"长度小于 {min_length}")

        if max_length >= 0 and len(user_input) > max_length:
            errors.append(f"长度大于 {max_length}")

        if valid_set is not None and user_input not in valid_set:
            errors.append("不在允许的值列表中")

        if not predicate(user_input):
            errors.append("未通过自定义验证")

        # 输入有效则返回
        if not errors:
            return user_input

        # 处理无效输入
        error_msg = f"{invalid_prompt}（原因：{', '.join (errors)}）"

        if error_method == ErrorMethod.REENTER:
            current_prompt = f"{error_msg}，请重新输入："
        elif error_method == ErrorMethod.EXIT:
            print(error_msg)
            sys.exit(1)
        elif error_method == ErrorMethod.RAISE:
            raise ValueError(error_msg)


async def restricted_input_with_timeout(
    prompt: object = "",
    min_length: int = 0,
    max_length: int = -1,
    valid_list: typing.Optional[typing.Sequence[str]] = None,
    invalid_prompt: str = "非法输入！",
    error_method: ErrorMethod = ErrorMethod.REENTER,
    timeout: float = 0,
    predicate: typing.Callable[[str], bool] = lambda s: True,
) -> str:
    """
    带超时的限制用户输入（异步版本）

    Args:
        prompt: 输入提示信息
        min_length: 最小输入长度（0 表示无限制）
        max_length: 最大输入长度（非正数表示无限制）
        valid_list: 允许的输入值列表（None 表示无限制）
        invalid_prompt: 非法输入时的提示信息
        error_method: 错误处理方式（ErrorMethod.REENTER 即 0 = 重新输入, ErrorMethod.EXIT 即 1 = 退出程序, ErrorMethod.RAISE 即 2 = 抛出异常）
        timeout: 输入超时时间（秒），非正数表示无超时
        predicate: 自定义验证函数（输入字符串返回布尔值）

    Returns:
        符合要求的用户输入字符串，超时返回空字符串

    Raises:
        ValueError: 当 error_method 值无效时
        ValueError: 当 error_method=2 且输入非法时
        asyncio.TimeoutError: 当超时时（内部处理）

    Examples:
        >>> async def example ():
        ...     value = await restricted_input_with_timeout (
        ...         "请在 5 秒内输入:",
        ...         timeout=5,
        ...         min_length=1
        ...     )
    """
    # 参数验证
    if timeout < 0:
        raise ValueError("timeout 不能为负数")
    if error_method not in (0, 1, 2):
        raise ValueError("error_method 只能是 0, 1 或 2")

    valid_set = set(valid_list) if valid_list is not None else None

    async def input_coroutine():
        current_prompt = prompt
        while True:
            try:
                user_input = await asyncio.to_thread(input, current_prompt)
            except EOFError:
                user_input = ""

            # 验证输入
            errors = []
            if min_length > 0 and len(user_input) < min_length:
                errors.append(f"长度小于 {min_length}")

            if max_length >= 0 and len(user_input) > max_length:
                errors.append(f"长度大于 {max_length}")

            if valid_set is not None and user_input not in valid_set:
                errors.append("不在允许的值列表中")

            if not predicate(user_input):
                errors.append("未通过自定义验证")

            # 输入有效则返回
            if not errors:
                return user_input

            # 处理无效输入
            error_msg = f"{invalid_prompt}（原因：{', '.join (errors)}）"

            if error_method == ErrorMethod.REENTER:
                current_prompt = f"{error_msg}，请重新输入："
            elif error_method == ErrorMethod.EXIT:
                print(error_msg)
                sys.exit(1)
            elif error_method == ErrorMethod.RAISE:
                raise ValueError(error_msg)

    try:
        if timeout > 0:
            return await asyncio.wait_for(input_coroutine(), timeout)
        return await input_coroutine()
    except asyncio.TimeoutError:
        print("\n 超时！按两次回车键继续...", end="")
        # 防止之后的程序在一次回车前提前运行
        input("再按一次回车以继续：")
        return ""


def multisplit(text: str, *separators: str) -> list[str]:
    """
    使用多个分隔符分割字符串

    Args:
        text: 要分割的字符串
        separators: 一个或多个分隔符，无则按空格分割

    Returns:
        分割后的字符串列表

    Examples:
        >>> multisplit ("apple,banana;orange|grape", ",", ";", "|")
        ['apple', 'banana', 'orange', 'grape']

        >>> multisplit ("hello world  python")  # 默认按空白分割
        ['hello', 'world', 'python']
    """
    if not separators:
        # 没有提供分隔符时按任意空白字符分割
        return re.split(r"\s+", text.strip())

    pattern = "|".join(map(re.escape, separators))
    return [part for part in re.split(pattern, text) if part]


def replace_pro(
    text: str,
    old: str,
    new: str,
    start_index: int = 0,
    replace_count: typing.Optional[int] = None,
) -> str:
    """
    增强版字符串替换（支持起始位置和替换次数控制）

    Args:
        text: 原始文本
        old: 要替换的子字符串
        new: 替换后的新字符串
        start_index: 从第几个匹配开始替换（0 表示第一个），不允许逆序索引
        replace_count: 要替换的最大次数（None 表示替换所有），多于可替换次数则全部替换

    Returns:
        替换后的新文本

    Raises:
        TypeError: 参数类型错误
        ValueError: 参数值无效

    Examples:
        >>> replace_pro ("a-b-c-d", "-", "+", start_index=1, replace_count=2)
        'a-b+c+d'
    """
    # 参数验证
    if not isinstance(text, str):
        raise TypeError(f"text 必须是字符串，实际类型为 {type (text).__name__}")
    if not isinstance(old, str):
        raise TypeError(f"old 必须是字符串，实际类型为 {type (old).__name__}")
    if not isinstance(new, str):
        raise TypeError(f"new 必须是字符串，实际类型为 {type (new).__name__}")
    if not isinstance(start_index, int):
        raise TypeError(
            f"start_index 必须是整数，实际类型为 {type (start_index).__name__}"
        )
    if replace_count is not None and not isinstance(replace_count, int):
        raise TypeError(
            f"replace_count 必须是整数或 None，实际类型为 {type (replace_count).__name__}"
        )

    if start_index < 0:
        raise ValueError(f"start_index 不能为负数，实际值: {start_index}")
    if replace_count is not None and replace_count < 0:
        raise ValueError(f"replace_count 不能为负数，实际值: {replace_count}")

    # 特殊情况处理
    if not old:
        return text
    if replace_count == 0:
        return text

    # 查找所有匹配位置
    matches = []
    index = 0
    while index < len(text):
        pos = text.find(old, index)
        if pos == -1:
            break
        matches.append(pos)
        index = pos + len(old)

    total_matches = len(matches)

    # 处理无效的起始索引
    if start_index >= total_matches:
        return text

    # 计算实际替换范围
    start_idx = start_index
    end_idx = (
        total_matches
        if replace_count is None
        else min(start_index + replace_count, total_matches)
    )

    # 构建结果字符串
    parts = []
    current_index = 0

    # 处理起始索引之前的匹配（不替换）
    for i in range(start_idx):
        start_pos = matches[i]
        end_pos = matches[i] + len(old)
        parts.append(text[current_index:end_pos])
        current_index = end_pos

    # 替换指定范围的匹配
    for i in range(start_idx, end_idx):
        start_pos = matches[i]
        end_pos = matches[i] + len(old)

        parts.append(text[current_index:start_pos])
        parts.append(new)
        current_index = end_pos

    # 添加剩余部分
    parts.append(text[current_index:])

    return "".join(parts)


def diff_char(bin1: str, bin2: str, wildcard: list = ["*", "?"]):
    """
    比较两个长度相同的字符串不同的字符数，允许自定义通配符

    Args:
        bin1: 第一个字符串
        bin2: 第二个字符串
        wildcard: 通配符

    Returns:
        int: 不同因子个数

    Raises:
        ValueError: 两个字符串长度不同

    Examples:
        >>> diff_char ('114510','11??14',['?'])
        1
    """
    if len(bin1) != len(bin2):
        raise ValueError(f"字符串 {bin1} 与 {bin2} 长度不同！")
    count: int = 0  # 不同项计数
    for index in range(0, len(bin1)):
        if bin1[index] in wildcard or bin2[index] in wildcard:
            continue
        if bin1[index] != bin2[index]:
            count += 1
    return count


def replace_diff(str1: str, str2: str, target_char: str = "-") -> str | None:
    """
    返回差异位置替换为目标字符的新字符串

    Args:
        str1: 第一个输入字符串
        str2: 第二个输入字符串
        target_char: 替换后的字符，默认为 '-'。

    Returns:
        str: 处理后的新字符串

    Raises:
        ValueError: 当输入字符串长度不一致时

    Examples:
        >>> replace_diff ("abc", "adc")
        'a-c'
        >>> replace_diff ("11-", "10-")
        '1--'
        >>> replace_diff ("-bc", "abc")
        '-bc'
        >>> replace_diff ("a-c", "01c",'*')
        '**c'
    """
    # 1. 检查字符串长度
    if len(str1) != len(str2):
        raise ValueError(f"字符串长度不同: {len (str1)} != {len (str2)}")

    # 2. 找出差异位置
    diff_indices = []
    for i, (a, b) in enumerate(zip(str1, str2)):
        # 记录非通配符字符不同的位置
        if a != b:
            diff_indices.append(i)

    # 4. 构建结果字符串
    result_chars = []
    diff_index = diff_indices[0]
    for i, char in enumerate(str1):
        if i == diff_index:
            # 差异位置
            result_chars.append(target_char)
        else:
            # 非差异位置
            result_chars.append(char)

    return "".join(result_chars)


def do_while(
    action: typing.Callable[[], None], condition: typing.Callable[[], bool]
) -> None:
    """
    执行 do-while 循环（先执行后判断）

    Args:
        action: 每次循环要执行的操作（无参数）
        condition: 循环条件（返回布尔值）

    Examples:
        >>> count = 3
        >>> def action ():
        ...     nonlocal count
        ...     print (count)
        ...     count -= 1
        >>> do_while (action, lambda: count > 0)
        3
        2
        1
    """
    action()
    while condition():
        action()


def multiplication_table(n: int, reverse: bool = False) -> str:
    """
    生成 n 阶乘法表（返回格式化字符串）

    Args:
        n (int): 乘法表的最大乘数（正整数）
        reverse (bool, optional): 是否逆序生成乘法表。默认为 False。

    Returns:
        格式化后的乘法表字符串

    Raises:
        TypeError: n 不是整数
        ValueError: n 不是正数

    Examples:
        >>> table = multiplication_table (3,False)
        >>> print (table)
        3*1=3  3*2=6  3*3=9
        2*1=2  2*2=4
        1*1=1
    """
    if not isinstance(n, int):
        raise TypeError(f"n 必须是整数，实际类型为 {type (n).__name__}")
    if n <= 0:
        raise ValueError(f"n 必须是正整数，实际值: {n}")

    # 计算最大数字宽度
    max_value = n * n
    num_width = len(str(max_value))
    col_width = num_width * 2 + 3  # 每个单元格的宽度

    # 构建乘法表字符串
    table_lines = []

    for i in range(n, 0, -1) if reverse else range(1, n + 1, 1):
        row_parts = []
        for j in range(1, i + 1):
            product = i * j
            # 格式化每个乘法表达式
            expr = f"{i}*{j}={product}"
            row_parts.append(f"{expr:<{col_width}}")

        # 将当前行合并为一个字符串
        line = "".join(row_parts)
        table_lines.append(line)

    # 将行连接为完整表格字符串
    table_str = "\n".join(table_lines)

    return table_str  # 返回格式化字符串


def enumerate_comb(iterable: typing.Iterable):
    """
    从少到多地生成可迭代对象的元素的所有组合。（不考虑元素重复的情况）

    Args:
        iterable (iterable): 包含要生成组合的元素。

    Yields:
        tuple: 从 iterable 中生成的一个组合。

    Examples:
        >>> for comb in enumerate_comb ([1,2,3]):
        ...     print (comb)
        ()
        (1,)
        (2,)
        (3,)
        (1, 2)
        (1, 3)
        (2, 3)
        (1, 2, 3)
    """
    for length in range(0, len(list(iterable)) + 1):
        yield from itertools.combinations(iterable, length)


def enumerate_perm(iterable: typing.Iterable):
    """
    从少到多地生成枚举可迭代对象元素的所有排列（不考虑元素重复）。

    Args:
        iterable: 可迭代对象

    Yields:
        tuple: 一个排列

    Examples:
        >>> list(enumerate_perm('ab'))
        [(), ('a',), ('b',), ('a', 'b'), ('b', 'a'),]

    """
    for length in range(0, len(list(iterable)) + 1):
        yield from itertools.permutations(iterable, length)


async def main():
    """测试所有函数的功能"""
    # 测试谓词和数值相关
    print(
        f"114 is odd: {is_odd (114)}",
        f"33550335 is odd: {is_odd (33550335)}",
        None,
        f"114 is even: {is_even (114)}",
        f"33550335 is even: {is_even (33550335)}",
        None,
        f"10 以内 3 的倍数: {(
            pipe (range (10))
            |pfilter ( is_divisible_by (3) )
            |list
            ).get ()}",
        f"10 以内不是 3 的倍数: {(
            pipe (range (10))
            |pfilter ( is_indivisible_by (3) )
            |list
            ).get ()}",
        f"因式分解 228:{factoring (228)}",
        f"228 的因数:{divisors (228)}",
        f"判断完美数:{list(
            zip(
            [0b110,0b11100,0b11110000,137438691328],
            map(
                is_perfect_num,
                [0b110,0b11100,0b1111000,137438691328]
            )
                            )
                            )
                }",
        sep="\n",
        end="\n",
    )
    assert is_n_decimal(1.2345, 4)
    assert not is_n_decimal(1.23456, 4)
    for n in range(1, 101) if False else range(0):  # 改为 True 启用
        print(f"the {n} th prime num: {nth_prime_num (n)}")

    # 测试比较操作支持
    print("比较测试:")
    print(is_comparable(10, 20))  # True
    print(is_comparable(10, "20"))  # False
    print(is_comparable("a", "b"))  # True

    # 测试密码设置
    if False:  # 改为 True 启用测试
        password = restricted_input(
            "设置密码（长度 5-15，需含大小写字母）:",
            min_length=5,
            max_length=15,
            invalid_prompt="密码不符合要求",
            predicate=lambda s: any(c.isupper() for c in s)
            and any(c.islower() for c in s),
        )

        print(f"密码设置成功: {password}")

        result = await restricted_input_with_timeout(
            "请在 5 秒内输入密码:",
            timeout=5,
            valid_list=[password],
            invalid_prompt="密码错误",
        )
        print("密码验证成功!" if result else "输入超时")

    # 测试逆序输出
    big_num = 12345
    print("逆序输出:", end=" ")

    def reverse_digit():
        nonlocal big_num
        print(big_num % 10, end="")
        big_num //= 10

    do_while(reverse_digit, lambda: big_num > 0)
    print()

    # 测试多重分割
    text = "apple,banana;orange|grape"
    print("多重分割:", multisplit(text, ",", ";", "|"))

    # 测试增强替换
    text = "apple-apple-apple-apple"
    result = replace_pro(text, "apple", "orange", start_index=1, replace_count=2)
    print("增强替换:", result)  # apple-orange-orange-apple

    # 测试逆序乘法表（返回字符串）
    print("\n 逆序乘法表:")
    table_str = multiplication_table(10, True)
    print(table_str)  # 输出乘法表字符串

    # 测试字符串比较
    print(diff_char("114510", "11??14", ["?"]))  # 1

    print(replace_diff("001", "111"))  # -01
    print(replace_diff("abc", "adc"))  # "a-c"
    print(replace_diff("11-", "10-"))  # "1--"
    print(replace_diff("-bc", "-dc", "-"))  # --c
    print(replace_diff("a-c", "a1c", "-"))  # a-c
    print(replace_diff("hello", "hexlo", "-"))  # he-lo
    print(replace_diff("--", "ab", "-"))  # --
    print(replace_diff("a*b", "a1b", "*"))  # a*b

    # 测试排列组合
    for tuple in enumerate_comb([1, 2, 3]):
        print(tuple)
    for tuple in enumerate_perm([1, 2]):
        print(tuple)

    # diff_char 和 replace_diff 的使用实例可见 quine_mccluskey.py


if __name__ == "__main__":
    asyncio.run(main())
