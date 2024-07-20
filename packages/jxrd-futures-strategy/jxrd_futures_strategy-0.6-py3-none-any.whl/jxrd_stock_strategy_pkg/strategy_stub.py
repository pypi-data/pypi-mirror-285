import json
from datetime import datetime

from jxrd_stock_strategy_pkg import strategy, time_utils

g_params = {'exchange': 'ZCE', 'tag': 'Z', 'name': 'SA', 'no': 'MAIN', 'date': 'A', 'min': 3.0, 'max': 9999.99,
            'price': 6000, 'profit_percent': 0, 'scale': 0, 'profit_percent_decimal_direct': 'up', 'days': 0,
            'quantity': 1}


def buy(qty, open_position, cid, needCover=False):
    # pass
    print(f" buy 建多仓 {qty} {open_position}")


def buy_to_cover(qty, open_position, cid, user_no, needCover=False, ):
    # pass
    print(f" buy_to_cover 平空仓操作 {qty} {open_position}")


def sell(qty, open_position, cid, needCover=False):
    # pass
    print(f" sell 平多仓操作 {qty} {open_position}")


def sell_short(qty, open_position, cid, needCover=False):
    # pass
    print(f" sell_short 建空仓操作 {qty} {open_position}")


def plot_numeric(message, price, color=0xdd0000):
    pass


def open_price_event(current_strategy, trading_day=None):
    return open_price_map.get(trading_day, 0)


def no_day_line_call_back_event():
    return {"Buy": buy, "BuyToCover": buy_to_cover, "Sell": sell, "SellShort": sell_short,
            "LogInfo": print, "plot_numeric": plot_numeric,
            "open_price_event": open_price_event}


def all_open_price(record_list):
    for row in record_list:
        dt_object = datetime.strptime(time_utils.float_to_time(row['datetime']), "%H:%M:%S")
        time_part = dt_object.strftime("%H:%M:%S")
        if time_part == "21:00:00":
            open_price_map[row['tradingday']] = row['open']
        if time_part == "09:00:00":
            if row['tradingday'] not in open_price_map:
                open_price_map[row['tradingday']] = row['open']


if __name__ == '__main__':
    # if len(sys.argv) < 1:
    #     print("缺少参数!")
    #     sys.exit(1)
    print("实盘策略测试")
    global open_price_map
    open_price_map = {'20240718': 7671}
    records = []
    with open('../resource/tick-data.csv', 'r') as file:
        for line in file:
            record = json.loads(line.replace("\n", "")[1:-1].replace("\'", '"'))
            records.append(record)
    all_open_price(records)

    strategy = strategy.NoDayLineStrategy(
        {}, g_params, no_day_line_call_back_event())
    with open('../resource/tick-data.csv', 'r') as file:
        for line in file:
            record = json.loads(line.replace("\n", "")[1:-1].replace("\'", '"'))
            strategy.handle_data(record)
