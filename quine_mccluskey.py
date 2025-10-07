import functions


def quine_mccluskey(*minterms_dec):
    """
    使用奎恩-麦克拉斯基法化简逻辑函数。

    Args:
        *minterms_dec (int): 最小项编码，十进制

    Returns:
        tuple: 所有必要乘积项的二进制表示

    Raises:
        无

    Exaples:
        >>> quine_mccluskey(0, 1, 3, 5, 7)
        ... ('--1', '00-')
    """

    def replace_single_diff(str1: str, str2: str, target_char: str = "-") -> str | None:
        """
        比较两个字符串，若恰好有一个字符不同，则返回差异位置替换为target_char的新字符串
        用于奎恩麦克拉斯基法的最小项合并

        Args:
            str1: 第一个输入字符串
            str2: 第二个输入字符串
            target_char: 替换后的字符，默认为'-'。

        Returns:
            str: 处理后的新字符串
            None: 当无差异、多个差异

        Raises:
            ValueError: 当输入字符串长度不一致时

        Examples:
            >>> replace_single_diff("abc", "adc")
            'a-c'
            >>> replace_single_diff("11-", "10-")
            '1--'
            >>> replace_single_diff("-bc", "abc")
            '-bc'
            >>> replace_single_diff("a-c", "a1c")
            'a-c'
        """
        if functions.diff_char(str1, str2) == 1:
            return functions.replace_diff(str1, str2, "-")
        else:
            return None

    # 读取最小项编码表，并转换为二进制字符串列表
    minterms: list = [bin(int(x))[2:] for x in minterms_dec]  # 切去0b

    # 确定最大位数
    max_length: int = max(len(d) for d in minterms)

    # 保持位数统一
    minterms = [d.zfill(max_length) for d in minterms]

    """
    根据包含1的个数将最小项分组为列表
    列表的索引是1的个数，
    元素是  最小项编码的单元素元组：最小项编码（合并前）
            乘积项所包含的最小项编码组成的元组：乘积项编码（合并后）
    """
    grouped_minterms: list[dict[tuple:str]] = [
        dict() for _ in range(max_length + 1)
    ]  # 最少0个1，最多有max_length个1

    for minterms_index in range(0, len(minterms)):
        num_of_1 = minterms[minterms_index].count("1")
        grouped_minterms[num_of_1].update(
            {(minterms[minterms_index],): minterms[minterms_index]}  # 用元组表示
        )

    # 第一步：合并乘积项

    unmergeable_terms: dict[tuple[int] : str] = (
        dict()
    )  # 记录不能合并的项,需要去重，顺序无关紧要

    while True:
        """
        将每一组的每一个最小项与相邻组里所有的最小项逐一比较。
        若仅有一个因子不同，则可以合并,并消除不同的因子。
        消去的因子用-表示。不能合并的项需要记录并移除。
        """

        merge_rslts: list[dict[tuple:str]] = [dict() for _ in range(max_length + 1)]
        # 临时存储合并结果,索引是1的个数，元素是 最小项编号组合：二进制最小项编码（字典）

        mergeable: list[dict[tuple:bool]] = [dict() for _ in range(max_length + 1)]
        # 记录每一个项是否可以合并，索引是1的个数，元素是 最小项编号（组合）：是否可合并（字典）

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
                            )  # 排序的目的：防止诸如（0,2，8,10）：0-0-0与（0,8,2,10）：0-0-0被视为两个不同的乘积项
                            mergeable[num_of_1][term[0]] = True
                            mergeable[num_of_1 + 1][other_term[0]] = True
                # 不可替换，记录
                if term[0] not in mergeable[num_of_1]:
                    unmergeable_terms.update({term[0]: term[1]})
        # 迭代，进行下一次合并
        grouped_minterms = merge_rslts
        # 终止条件:全部合并不了
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
        # print(comb)
        all_minterms: set = set()
        for item in comb:
            all_minterms |= set(item[0])
        # print(all_minterms)
        if minterms_remained.issubset(all_minterms):
            # 合并结果
            results: list = list(results.values())
            for item in comb:
                results.append(item[1])
            return tuple(results)


def main():
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

    # 11. 典型卡诺图测试1 (形成方形)
    print("典型卡诺图测试1:", quine_mccluskey(0, 1, 4, 5))  # 预期: ('-0-',)

    # 12. 典型卡诺图测试2 (形成条状)
    print("典型卡诺图测试2:", quine_mccluskey(2, 3, 6, 7))  # 预期: ('-1-',)

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

    #八段管转码
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
    print("y0 -", quine_mccluskey(1,4,11,13))


if __name__ == "__main__":
    main()
