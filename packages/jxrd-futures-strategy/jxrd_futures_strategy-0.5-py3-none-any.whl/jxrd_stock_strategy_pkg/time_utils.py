def float_to_time(time_float):
    # 假设time_float形如0.HHMM，其中HH是小时，MM是分钟
    # 将浮点数转换为字符串并去掉开头的'0.'
    time_str = str(time_float)[2:]

    # 确保time_str至少有4个字符（例如，如果它是0.15，则应为0015）
    time_str = time_str.zfill(4)

    # 切片字符串得到小时和分钟
    hours = time_str[:2]
    minutes = time_str[2:]

    # 格式化输出
    return f"{hours}:{minutes}:00"
