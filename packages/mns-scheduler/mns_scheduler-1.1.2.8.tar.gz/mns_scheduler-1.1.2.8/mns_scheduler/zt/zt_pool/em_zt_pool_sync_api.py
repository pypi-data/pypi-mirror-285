import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)
import pandas as pd
import mns_common.api.akshare.stock_zt_pool_api as stock_zt_pool_api
import mns_common.api.ths.zt.ths_stock_zt_pool_api as ths_stock_zt_pool_api
import mns_common.utils.date_handle_util as date_handle_util
import mns_common.component.concept.ths_concept_common_service_api as ths_concept_common_service_api
from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.component.company.company_common_service_api as company_common_service_api
from loguru import logger
import mns_common.utils.data_frame_util as data_frame_util
import mns_common.component.common_service_fun_api as common_service_fun_api
import mns_common.component.trade_date.trade_date_common_service_api as trade_date_common_service_api

'''
东方财富涨停池
'''

mongodb_util = MongodbUtil('27017')

ZT_FIELD = ['_id', 'symbol', 'name', 'now_price', 'chg', 'first_closure_time',
            'last_closure_time', 'connected_boards_numbers',
            'zt_reason', 'closure_funds',
            # 'closure_funds_per_amount', 'closure_funds_per_flow_mv',
            'frying_plates_numbers',
            # 'statistics_detail', 'zt_type', 'market_code',
            'statistics',
            # 'zt_flag',
            'industry', 'first_sw_industry',
            'second_sw_industry',
            'third_sw_industry', 'ths_concept_name',
            'ths_concept_code', 'ths_concept_sync_day', 'em_industry',
            'mv_circulation_ratio', 'ths_concept_list_info', 'kpl_plate_name',
            'kpl_plate_list_info', 'company_type', 'diff_days', 'symbol', 'amount',
            'quantity_ratio', 'high', 'low', 'high', 'low', 'open', 'list_date',
            'exchange', 'wei_bi', 'flow_mv', 'total_mv', 'buy_1_num',
            'classification', 'flow_mv_sp', 'total_mv_sp', 'flow_mv_level',
            'amount_level', 'new_stock', 'list_date_01', 'index', 'str_day']


def save_zt_info(str_day):
    if bool(1 - trade_date_common_service_api.is_trade_day(str_day)):
        return None

    stock_em_zt_pool_df_data = stock_zt_pool_api.stock_em_zt_pool_df(
        date_handle_util.no_slash_date(str_day))

    stock_em_zt_pool_df_data = common_service_fun_api.total_mv_classification(stock_em_zt_pool_df_data)

    stock_em_zt_pool_df_data = common_service_fun_api.classify_symbol(stock_em_zt_pool_df_data)

    stock_em_zt_pool_df_data = common_service_fun_api.symbol_amount_simple(stock_em_zt_pool_df_data)

    stock_em_zt_pool_df_data = company_common_service_api.amendment_industry(stock_em_zt_pool_df_data)
    try:
        # 同花顺问财涨停池
        ths_zt_pool_df_data = ths_stock_zt_pool_api.get_real_time_zt_info()

        # del stock_em_zt_pool_df_data['ths_concept_name']
        # del stock_em_zt_pool_df_data['ths_concept_code']

        for stock_one in stock_em_zt_pool_df_data.itertuples():
            try:
                stock_em_zt_pool_df_data = ths_concept_common_service_api.set_last_ths_concept(stock_one.symbol,
                                                                                               stock_em_zt_pool_df_data,
                                                                                               str_day)
                ths_zt_pool_one_df = ths_zt_pool_df_data.loc[ths_zt_pool_df_data['symbol'] == stock_one.symbol]
                if data_frame_util.is_empty(ths_zt_pool_one_df):
                    continue
                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'zt_reason'] = \
                    list(ths_zt_pool_one_df['zt_reason'])[0]

                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'quantity_ratio'] = \
                    list(ths_zt_pool_one_df['quantity_ratio'])[0]
                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'high'] = \
                    list(ths_zt_pool_one_df['high'])[0]
                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'low'] = \
                    list(ths_zt_pool_one_df['low'])[0]
                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'open'] = \
                    list(ths_zt_pool_one_df['open'])[0]

                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'wei_bi'] = \
                    list(ths_zt_pool_one_df['wei_bi'])[0]

                stock_em_zt_pool_df_data.loc[stock_em_zt_pool_df_data['symbol'] == stock_one.symbol, 'buy_1_num'] = \
                    list(ths_zt_pool_one_df['buy_1_num'])[0]

            except BaseException as e:
                logger.error("出现异常:{}", e)
    except BaseException as e:
        stock_em_zt_pool_df_data['zt_reason'] = ''
        stock_em_zt_pool_df_data['quantity_ratio'] = 0
        stock_em_zt_pool_df_data['high'] = 0
        stock_em_zt_pool_df_data['low'] = 0
        stock_em_zt_pool_df_data['open'] = 0
        stock_em_zt_pool_df_data['wei_bi'] = 0
        stock_em_zt_pool_df_data['buy_1_num'] = 0
        logger.error("出现异常:{}", e)

    stock_em_zt_pool_df_data['list_date'] = stock_em_zt_pool_df_data['list_date'].apply(
        lambda x: pd.to_numeric(x, errors="coerce"))

    stock_em_zt_pool_df_data['new_stock'] = False
    # 将日期数值转换为日期时间格式
    stock_em_zt_pool_df_data['list_date_01'] = pd.to_datetime(stock_em_zt_pool_df_data['list_date'], format='%Y%m%d')
    str_day_date = date_handle_util.str_to_date(str_day, '%Y-%m-%d')
    # 计算日期差值 距离现在上市时间
    stock_em_zt_pool_df_data['diff_days'] = stock_em_zt_pool_df_data.apply(
        lambda row: (str_day_date - row['list_date_01']).days, axis=1)
    # 上市时间小于100天为新股
    stock_em_zt_pool_df_data.loc[
        stock_em_zt_pool_df_data["diff_days"] < 100, ['new_stock']] \
        = True
    stock_em_zt_pool_df_data = stock_em_zt_pool_df_data.dropna(subset=['diff_days'], axis=0, inplace=False)

    # 按照"time"列进行排序，同时将值为0的数据排到最末尾
    stock_em_zt_pool_df_data = stock_em_zt_pool_df_data.sort_values(by=['first_closure_time'])

    # 重置索引，并将排序结果保存到新的"index"列中

    stock_em_zt_pool_df_data['str_day'] = str_day
    stock_em_zt_pool_df_data['_id'] = stock_em_zt_pool_df_data['symbol'] + "_" + str_day

    stock_em_zt_pool_df_data = stock_em_zt_pool_df_data[ZT_FIELD]
    mongodb_util.save_mongo(stock_em_zt_pool_df_data, 'stock_zt_pool')
    return stock_em_zt_pool_df_data


if __name__ == '__main__':
    save_zt_info('2024-06-25')
# from datetime import datetime
#
# if __name__ == '__main__':
#
#     sync_date = date_handle_util.add_date_day('20240110', 0)
#
#     now_date = datetime.now()
#
#     str_now_day = sync_date.strftime('%Y-%m-%d')
#
#     while now_date > sync_date:
#         try:
#             save_zt_info(str_now_day)
#             sync_date = date_handle_util.add_date_day(date_handle_util.no_slash_date(str_now_day), 1)
#             print(str_now_day)
#             str_now_day = sync_date.strftime('%Y-%m-%d')
#
#         except BaseException as e:
#             sync_date = date_handle_util.add_date_day(date_handle_util.no_slash_date(str_now_day), 1)
#             str_now_day = sync_date.strftime('%Y-%m-%d')
