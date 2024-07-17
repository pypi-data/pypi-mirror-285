import math


def has_decimal_and_floor(num):
    if isinstance(num, float) and num != int(num):  # 判断是否为浮点数且不是整数
        return math.floor(num)  # 向下取整
    else:
        return num


def has_decimal_and_ceil(num):
    if isinstance(num, float) and num != int(num):
        return math.ceil(num)  # 向上取整
    else:
        return num


def has_decimal_and_round(num, digits=0):
    if isinstance(num, float) and num != int(num):
        return round(num, digits)  # 四舍五入到指定的小数位数
    else:
        return num



