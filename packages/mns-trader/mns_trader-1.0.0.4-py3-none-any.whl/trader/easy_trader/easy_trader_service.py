import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 33
project_path = file_path[0:end]
sys.path.append(project_path)
from loguru import logger
import easytrader
from easytrader import grid_strategies
from flask import jsonify
user = easytrader.use('ths')
user.connect(r'D:\Program Files\ths\xiadan.exe')
user.grid_strategy = grid_strategies.Xls
user.grid_strategy_instance.tmp_folder = 'C:\\custom_folder'


# 下单
def order_buy(symbol, buy_price, buy_volume):
    logger.warning("买入代码:{},买入价格:{},买入数量:{}", symbol, buy_price, buy_volume)
    user.enable_type_keys_for_editor()
    buy_result = user.buy(symbol, buy_price, buy_volume)

    return buy_result


# 自动一键打新
def auto_ipo_buy():
    return user.auto_ipo()


# 获取持仓
def get_position():
    result = user.position
    return jsonify(result)


# 卖出
def order_sell(symbol, sell_price, sell_volume):
    logger.warning("卖出代码:{},卖出价格:{},卖出数量:{}", symbol, sell_price, sell_volume)
    user.enable_type_keys_for_editor()
    sell_result = user.sell(symbol, sell_price, sell_volume)
    return sell_result


# 取消
def order_cancel(entrust_no):
    user.enable_type_keys_for_editor()
    cancel_result = user.cancel_entrust(entrust_no)
    return cancel_result


if __name__ == '__main__':
    auto_ipo_buy()
