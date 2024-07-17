from jxrd_stock_strategy_pkg import number_utils


class BackTestParams:

    def __init__(self):
        self.trade_day = None
        self.open_price = 0
        self.profit = 0
        self.open_position = 0
        self.stop_profit_position = 0

    def set_trade_day(self, value):
        self.trade_day = value

    def get_trade_day(self):
        return self.trade_day

    def set_open_price(self, value):
        self.open_price = value

    def get_open_price(self):
        return self.open_price

    def set_profit(self, value):
        self.profit = value

    def get_profit(self):
        return self.profit

    def set_open_position(self, value):
        self.open_position = value

    def get_open_position(self):
        return self.open_position

    def set_stop_profit_position(self, value):
        self.stop_profit_position = value

    def get_stop_profit_position(self):
        return self.stop_profit_position

    def calculate_open_position(self, value, decimal_direct: 'none'):
        self.set_open_position(calculate_open_position(value, decimal_direct))


def calculate_open_position(value, decimal_direct: 'none'):
    dic = {"up": number_utils.has_decimal_and_ceil,
           "down": number_utils.has_decimal_and_floor,
           "round": number_utils.has_decimal_and_round}
    return dic.get(decimal_direct, to_decimal)(value)


def to_decimal(num=0):
    return num
