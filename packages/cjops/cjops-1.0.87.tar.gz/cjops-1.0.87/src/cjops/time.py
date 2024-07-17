import pendulum
def get_timestamp(offset=None, current_time=None):
    """
    获取当前时间戳或指定datetime偏移量后的时间戳

    :param offset: 偏移量字符串，格式为 'Xd' 或 'Xh'，X 为数字，d 表示天数，h 表示小时数。
    :now pendulum.DateTime 对象，用于指定时间。默认是当前时间
    """
    # 获取当前时间
    if current_time is None:
        now = pendulum.now(tz='Asia/Shanghai')
    else:
        now = current_time

    # 如果提供了偏移量，则根据偏移量调整时间
    if offset:
        try:
            # 解析偏移量字符串，格式为 'Xd' 或 'Xh'
            # 假设偏移量字符串总是有效的，并且格式正确
            sign = offset[0]
            if sign in ['+', '-']:
                duration, unit = int(offset[1:-1]), offset[-1]
            else:
                duration, unit = int(offset[:-1]), offset[-1]

            # print(sign, duration, unit)
            if unit == 'd':
                # 天数
                duration_in_days = duration if sign != '-' else -duration
                now = now.add(days=duration_in_days)
            elif unit == 'h':
                # 小时数
                duration_in_hours = duration if sign != '-' else -duration
                now = now.add(hours=duration_in_hours)
            else:
                # 如果单位不是 'd' 或 'h'，则抛出异常或返回当前时间戳
                raise ValueError("Invalid unit in offset. Expected 'd' or 'h'.")
                # 将 pendulum 时间对象转换为 Unix 时间戳（秒为单位）
        except Exception:
            raise Exception(f'时间戳格式不正确,eg: 30d, -3d, 3000h, -3h')
    timestamp = now.timestamp()

    return timestamp

if __name__ == '__main__':
    # 测试函数
    print(get_timestamp())  # 默认获取当前时间戳
    print(get_timestamp('-3h'))  # 获取30天后的时间戳
    print(get_timestamp('-3d'))  # 获取3天前的时间戳
    print(get_timestamp('10h'))  # 获取3000小时后的时间戳
    print(get_timestamp('-3'))  # 获取3小时前的时间戳