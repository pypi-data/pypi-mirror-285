# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import re


def get_digit_char(string: str) -> str:
    """
    提取数字
    '84.2' -> '842'
    'abc123' -> '123'
    :param string:
    :return:
    """
    return re.sub(u"([^\u0030-\u0039])", "", string)


def get_integer_decimals(string: str) -> list:
    """
    提取小数和整数
    'abc84.2'    -> ['84.2']
    'abc84.2@56' -> ['84.2', '56']
    :param string:
    :return:
    """
    res = re.findall(r"\d+[.\d]*", string)
    return res


def only_contain_letter_char(self, string: str) -> bool:
    """
    仅包含字母（大小写）
    """
    return len(self.get_letter_char(string)) == len(string)


def get_letter_char(string: str) -> str:
    # 提取大小写字母
    return re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", string)


def get_digit_letter_char(string: str) -> str:
    # 提取大小写字母、数字
    return re.sub(u"([^\u0041-\u005a\u0061-\u007a\u0030-\u0039])", "", string)


def only_chinese(string: str) -> bool:
    """
    string都是中文
    :param string:
    :return: True都是中文 | 否
    """
    match_chinese = re.sub(u"([^\u4e00-\u9fa5])", "", string)
    return len(match_chinese) == len(string)


def normalize_cos_sign(string, sign: str = None):
    """
    cos符号标准化：将cos15°转成cos(radians(15))
    cos15° -> cos(radians(15))
    cos5 -> cos(radians(5))
    cosa° -> cos(radians(a))
    cosθ -> cos(radians(θ))
    cos(a) -> cos(radians(a))
    cos(15°) -> cos(radians(15))
    cos(5) -> cos(radians(5))
    :param string:
    :param sign:
    :return:
    """
    if not sign:
        sign = "radians"
    # ori = string
    items = re.split("[+-/*]", string)
    if len(items) > 0:
        for item in items:
            res = re.findall("[Cc][Oo0][Ss]", item)
            if len(res) > 0:
                value = item.replace(res[0], "").replace("°", "").replace("。", "").replace("(", "").replace(")", "")
                if sign:
                    value = "({0}({1}))".format(sign, value)
                else:
                    value = "({0})".format(value)
                string = string.replace(item, "cos" + value)
    # print(ori, "->", side_length)
    return string


def normalize_multiple_sign(string, from_char: list = None, to_char="*"):
    """
    乘号标准化：将x、X、×转成*
    161.9+x2-nXSxd+nxS+2x+2x(a+b) -> 161.9+x2-n*S*d+n*S+2x+2*(a+b)
    :param string:
    :param from_char: ["x", "X"]
    :param to_char: 标准化的字符
    :return:
    """
    if from_char is None:
        from_char = ["x", "X"]
    items = re.split("[+-/*]", string)
    if len(items) > 0:
        for item in items:
            from_join = "".join(from_char)
            pattern = "^[^"+from_join+"].*["+from_join+"]{1}.*[^"+from_join+"]$"
            res = re.findall(pattern, item)
            if len(res) > 0:
                item = str(res[0]).replace("x", to_char).replace("X", to_char).replace("×", to_char)
                string = string.replace(res[0], item)
    return string


def normalize_calculate_formula(string: str) -> str:
    """
    计算公式标准化，字符串排序
    (320+10707/2+1272)*2+(12+11)  ->   2*(10707/2+1272+320)+(11+12)
    320+10707/2+1272              ->   10707/2+1272+320
    320+1272*2                    ->   1272*2+320
    320+1272*2+(12+11)            ->   1272*2+320+(11+12)
    17+3.1416*110                 ->   110*3.1416+17
    """
    # 先把括号里的顺序排列好
    res = re.findall(r"[(](.*?)[)]", string)
    string_blank = string
    blank_map = {}
    if len(res):
        for i, item in enumerate(res):
            ite = str(item).split("+")
            ite.sort()
            string = string.replace(item, "+".join(ite))
            string_blank = string_blank.replace("(" + item + ")", "A{0}".format(i))
            blank_map["A{0}".format(i)] = "(" + "+".join(ite) + ")"
    else:
        ite = string_blank.split("+")
        ite.sort()
        string_blank = "+".join(ite)
    # 再把乘号顺序排列好
    res = string_blank.split("+")
    res.sort()
    string_blank = "+".join(res)
    for i, item in enumerate(res):
        ite = item.split("*")
        ite.sort()
        string_blank = string_blank.replace(item, "*".join(ite))
    # 再次排序
    res = string_blank.split("+")
    res.sort()
    string_blank = "+".join(res)
    # 最后映射转换
    for blank in blank_map:
        string_blank = string_blank.replace(blank, blank_map.get(blank))
    return string_blank
