import datetime


class DateTool:
    @staticmethod
    def offset(date_format, offset_type, count, data=None):
        """
        日期偏移（前N天、后N天）
        @param date_format: 格式（如：%Y-%m-%d %H:%M:%S）
        @param offset_type: 偏移类型（Q-向前偏移 即前N天，H-向后偏移 即后N天）
        @param count: 偏移天数
        @param data: 偏移基准日期（如：2020-11-14 19:48:51） 若为None则当前日期
        @return: 偏移后的日期
        """
        # 时间加减
        # 获取当前日期
        if data is None:
            data = datetime.datetime.now().strftime(date_format)
        # 将时间字符串转换为 datetime 格式的时间
        today = datetime.datetime.strptime(data, date_format)
        # 计算偏移量
        if offset_type == 'Q':
            offset = datetime.timedelta(days=-count)
        elif offset_type == 'H':
            offset = datetime.timedelta(days=+count)
        else:
            print(f'偏移类型错误，预期：“Q”或“H”，实际：{offset_type}')
        # 获取修改后的时间并格式化
        re_date = (today + offset).strftime(date_format)
        return re_date


