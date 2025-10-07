"""增强的函数签名获取模块

该模块提供了一个增强版的函数签名获取工具，可以获取包括内置函数在内的
各种Python对象的函数签名。当标准的inspect.signature()方法无法获取函
数签名时，该模块会尝试通过多种方式来获取签名信息。

主要功能:
- get_signature(obj): 获取任意可调用对象的函数签名
- 支持从类型存根文件(.pyi)中获取签名
- 为无法获取签名的对象生成通用签名

使用示例:
    >>> # 获取普通函数签名
    >>> def my_func(a, b=1):
    ...     pass

    >>> sig = get_signature(my_func)
    >>> print(f"{my_func.__name__}{sig}")

    >>> # 获取内置函数签名
    >>> sig = get_signature(len)
    >>> print(f"len{sig}")

注意事项:
- 对于某些内置函数，可能只能获取到通用签名

"""

import inspect
import types
import sys
import os
import ast
import importlib.util
from typing import Callable, Optional, Any, Union


def get_signature(obj: Any) -> inspect.Signature:
    """
    增强版的get_signature函数，当inspect.signature无法获取时，
    尝试通过存根文件或其他方式获取函数签名。

    Args:
        obj: 需要获取签名的对象

    Returns:
        inspect.Signature: 函数签名对象

    Raises:
        ValueError: 当无法获取函数签名时抛出异常
    """
    # 首先尝试使用inspect.signature
    try:
        return inspect.signature(obj)
    except (ValueError, TypeError):
        # 如果失败，尝试从存根文件获取
        return _get_signature_from_stub(obj)


def _get_signature_from_stub(obj: Any) -> inspect.Signature:
    """
    从存根文件中获取函数签名

    Args:
        obj: 需要获取签名的对象

    Returns:
        inspect.Signature: 函数签名对象
    """

    # 获取对象的模块和名称
    module_name = getattr(obj, "__module__", None)
    obj_name = getattr(obj, "__name__", None)

    if not module_name or not obj_name:
        raise ValueError(f"无法确定对象 {obj} 的模块或名称")

    # 尝试查找对应的存根文件
    try:
        signature = _find_signature_in_typeshed(module_name, obj_name)
        if signature:
            return signature
    except Exception:
        pass

    # 最后回到通用签名
    return _generate_generic_signature(obj)


def _find_signature_in_typeshed(
    module_name: str, obj_name: str
) -> Optional[inspect.Signature]:
    """
    在typeshed存根文件中查找函数签名

    Args:
        module_name: 模块名称
        obj_name: 对象名称

    Returns:
        inspect.Signature: 函数签名对象，如果找不到则返回None
    """
    # 查找标准库的存根文件
    # 首先尝试在标准typeshed位置查找
    try:
        # 获取Python安装路径
        stdlib_path = os.path.join(os.path.dirname(os.__file__), "..", "Lib")
        if os.path.exists(stdlib_path):
            # 查找对应的.pyi文件
            module_file = module_name.replace(".", os.sep) + ".pyi"
            stub_file_path = os.path.join(stdlib_path, module_file)

            if os.path.exists(stub_file_path):
                signature = _parse_stub_file(stub_file_path, obj_name)
                if signature:
                    return signature
    except Exception:
        pass

    # 如果标准位置找不到，尝试查找第三方typeshed
    try:
        import site

        for site_package in site.getsitepackages():
            typeshed_path = os.path.join(site_package, "typeshed", "stdlib")
            if os.path.exists(typeshed_path):
                module_file = module_name.replace(".", os.sep) + ".pyi"
                stub_file_path = os.path.join(typeshed_path, module_file)

                if os.path.exists(stub_file_path):
                    signature = _parse_stub_file(stub_file_path, obj_name)
                    if signature:
                        return signature
    except Exception:
        pass

    return None


def _parse_stub_file(stub_file_path: str, obj_name: str) -> Optional[inspect.Signature]:
    """
    解析存根文件并提取指定对象的签名

    Args:
        stub_file_path: 存根文件路径
        obj_name: 对象名称

    Returns:
        inspect.Signature: 函数签名对象，如果找不到则返回None
    """
    try:
        with open(stub_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析AST
        tree = ast.parse(content)

        # 查找函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == obj_name:
                # 解析参数
                parameters = []
                args = node.args

                # 处理位置参数
                num_defaults = len(args.defaults)
                for i, arg in enumerate(args.args):
                    kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
                    default = inspect.Parameter.empty

                    # 检查是否有默认值
                    if i >= len(args.args) - num_defaults:
                        default = "..."  # 简化处理，默认值在存根中通常不重要

                    param = inspect.Parameter(name=arg.arg, kind=kind, default=default)
                    parameters.append(param)

                # 处理可变位置参数 (*args)
                if args.vararg:
                    param = inspect.Parameter(
                        name=args.vararg.arg, kind=inspect.Parameter.VAR_POSITIONAL
                    )
                    parameters.append(param)

                # 处理关键字参数
                num_kw_defaults = len(args.kw_defaults)
                for i, arg in enumerate(args.kwonlyargs):
                    kind = inspect.Parameter.KEYWORD_ONLY
                    default = inspect.Parameter.empty

                    if i < num_kw_defaults and args.kw_defaults[i] is not None:
                        default = "..."

                    param = inspect.Parameter(name=arg.arg, kind=kind, default=default)
                    parameters.append(param)

                # 处理可变关键字参数 (**kwargs)
                if args.kwarg:
                    param = inspect.Parameter(
                        name=args.kwarg.arg, kind=inspect.Parameter.VAR_KEYWORD
                    )
                    parameters.append(param)

                return inspect.Signature(parameters=parameters)

        return None
    except Exception:
        return None


def _parse_signature_string(sig_str: str) -> inspect.Signature:
    """
    解析签名字符串为inspect.Signature对象

    Args:
        sig_str: 签名字符串

    Returns:
        inspect.Signature: 函数签名对象
    """
    # 这是一个简化的解析器，实际实现会更复杂
    # 移除函数名（假设格式为 name(...)）
    if "(" in sig_str and ")" in sig_str:
        # 提取括号内的内容
        params_str = sig_str[sig_str.find("(") + 1 : sig_str.rfind(")")]

        # 简单处理参数
        parameters = []
        if params_str and params_str != "/":  # 不是空参数列表
            # 处理特殊标记
            params_str = params_str.replace("/", "").strip()
            if params_str:
                # 分割参数
                param_parts = params_str.split(",")
                for i, part in enumerate(param_parts):
                    part = part.strip()
                    if not part:
                        continue

                    # 处理*args, **kwargs
                    if part.startswith("**"):
                        param_name = part[2:]
                        param_kind = inspect.Parameter.VAR_KEYWORD
                    elif part.startswith("*"):
                        param_name = part[1:]
                        param_kind = inspect.Parameter.VAR_POSITIONAL
                    else:
                        param_kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
                        # 处理默认值
                        if "=" in part:
                            param_name = part.split("=")[0].strip()
                        else:
                            param_name = part

                    # 处理关键字 only 参数
                    if (
                        part.startswith("*")
                        and not part.startswith("**")
                        and len(part) > 1
                    ):
                        param_name = part[1:]

                    param = inspect.Parameter(name=param_name, kind=param_kind)
                    parameters.append(param)

        return inspect.Signature(parameters=parameters)

    # 默认返回空参数列表
    return inspect.Signature(parameters=[])





def _generate_generic_signature(obj: Any) -> inspect.Signature:
    """
    生成通用的函数签名

    Args:
        obj: 目标对象

    Returns:
        inspect.Signature: 通用函数签名对象
    """
    # 创建一个接受任意参数的签名
    parameters = [
        inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
        inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
    ]
    return inspect.Signature(parameters=parameters)


# 使用示例和测试函数
def main():
    """测试增强版get_signature函数"""

    # 测试正常的Python函数
    def test_func(a, b=1, *args, c=2, **kwargs):
        pass

    print("测试正常函数:")
    try:
        sig = get_signature(test_func)
        print(f"  {test_func.__name__}{sig}")
    except Exception as e:
        print(f"  错误: {e}")

    # 测试内置函数
    # ... existing code ...
    # 测试内置函数
    def is_public_builtin(obj):
        name = getattr(obj, "__name__", "")
        return not name.startswith("_")

    if isinstance(__builtins__, dict):
        builtin_functions = [
            obj
            for obj in __builtins__.values()
            if callable(obj) and hasattr(obj, "__name__") and is_public_builtin(obj)
        ]
    else:
        builtin_functions = [
            obj
            for obj in vars(__builtins__).values()
            if callable(obj) and hasattr(obj, "__name__") and is_public_builtin(obj)
        ]

    print("\n测试内置函数:")
    for func in builtin_functions:
        try:
            sig = get_signature(func)
            print(f"  {func.__name__}{sig}")
        except Exception as e:
            print(f"  {func.__name__}: 错误 - {e}")


if __name__ == "__main__":
    main()
