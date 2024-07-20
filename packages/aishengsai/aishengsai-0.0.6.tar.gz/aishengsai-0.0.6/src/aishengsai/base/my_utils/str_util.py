# createBy yyj
# createTime: 2024/7/2 10:56

def str_reverse(s):
    """
    字符串反转
    :param s:
    :return:
    """
    reversed_s = ''
    for i in range(len(s) - 1, -1, -1):
        reversed_s += s[i]
    return reversed_s
def str_reverse_simple(s):
    """
    字符串反转
    :param s:
    :return:
    """
    return s[::-1]

def sub_str(s, start, end):
    """
    字符串截取
    :param s:
    :param start:
    :param end:
    :return:
    """
    sub_s = ''
    for i in range(start, len(s) if end >= len(s) else end, 1):
        sub_s += s[i]
    return sub_s

def sub_str_simple(s, start, end):
    """
    字符串截取
    :param s:
    :param start:
    :param end:
    :return:
    """
    return s[start:end]


