import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)

from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.api.msg.push_msg_api as push_msg_api
import mns_common.api.em.em_concept_index_api as em_concept_index_api


import pandas as pd
import mns_common.utils.data_frame_util as data_frame_util
from loguru import logger
mongodb_util = MongodbUtil('27017')

max_concept_code = 1200


# 获取最大概念代码
def get_max_concept_code():
    query = {"concept_code": {'$ne': 'null'}, "success": True}
    ths_concept_max = mongodb_util.descend_query(query, 'em_concept_list', 'concept_code', 1)
    if ths_concept_max.shape[0] == 0:
        concept_code = 'BK1134'
    else:
        concept_code = list(ths_concept_max['concept_code'])[0]
    concept_code = concept_code.replace('BK', '')
    return concept_code


# 获取概念名称
def get_concept_name(concept_code):
    concept_df = em_concept_index_api.sync_all_concept()
    concept_df_one = concept_df.loc[concept_df['concept_code'] == concept_code]
    if data_frame_util.is_empty(concept_df_one):
        return ""
    else:
        return concept_df_one


# 获取概念详情
def sync_concept_detail(concept_code):
    try:
        stock_board_concept_cons_em_df = em_concept_index_api.stock_board_concept_cons_em(concept_code)
        if data_frame_util.is_empty(stock_board_concept_cons_em_df):
            return None
        stock_board_concept_cons_em_df = stock_board_concept_cons_em_df.rename(columns={"序号": "index",
                                                                                        "代码": "symbol",
                                                                                        "名称": "name",
                                                                                        "最新价": "now_price",
                                                                                        "涨跌幅": "chg",
                                                                                        "涨跌额": "change",
                                                                                        "成交量": "volume",
                                                                                        "成交额": "amount",
                                                                                        "振幅": "pct_chg",
                                                                                        "最高": "high",
                                                                                        "最低": "low",
                                                                                        "今开": "open",
                                                                                        "昨收": "last_price",
                                                                                        "换手率": "exchange",
                                                                                        "市盈率-动态": 'pe',
                                                                                        "市净率": 'pb'
                                                                                        })
        return stock_board_concept_cons_em_df
    except BaseException as e:
        logger.error("同步东方财富概念信息异常:{}", e)
        return None


# web端获取新概念消息推送
def push_msg_to_we_chat_web(concept_code, concept_name):
    url = 'http://quote.eastmoney.com/center/boardlist.html#boards-' + str(concept_code)
    msg = "概念代码:" + str(concept_code) + "," + "概念名称:" + concept_name + "," + "url:   " + url
    title = "新增东财概念:" + str(concept_code) + "-" + concept_name
    push_msg_api.push_msg_to_wechat(title, msg)


# 保存新概念信息到数据库
def save_em_concept_list(concept_code, concept_name, str_day, str_now_time, concept_df_one):
    url = 'https://quote.eastmoney.com/center/boardlist.html#boards-' + str(concept_code)
    if data_frame_util.is_empty(concept_df_one):
        em_concept_list = pd.DataFrame([
            [concept_code, concept_code, concept_name, str_day, url, str_now_time, True],
        ], columns=['_id', 'concept_code', 'concept_name', 'str_day', 'url', 'str_now_time', 'success'])

        mongodb_util.save_mongo(em_concept_list, 'em_concept_list')
    else:
        concept_df_one['_id'] = concept_df_one['concept_code']
        concept_df_one.loc[:, 'str_now_time'] = str_now_time
        concept_df_one.loc[:, 'str_day'] = str_day
        concept_df_one.loc[:, 'url'] = url
        concept_df_one.loc[:, 'success'] = True
        mongodb_util.save_mongo(concept_df_one, 'em_concept_list')


# 保存新概念详细信息到数据库
def save_ths_concept_detail(new_concept_symbol_df, concept_name, str_day, str_now_time, concept_code):
    new_concept_symbol_df['_id'] = new_concept_symbol_df['symbol'] + '-' + concept_code

    new_concept_symbol_df['concept_code'] = concept_code
    new_concept_symbol_df['concept_name'] = concept_name
    new_concept_symbol_df['str_day'] = str_day
    new_concept_symbol_df['str_now_time'] = str_now_time

    new_concept_symbol_list = list(new_concept_symbol_df['symbol'])

    query_company_info = {'symbol': {'$in': new_concept_symbol_list}}
    query_field = {"first_industry": 1, "first_industry": 1, "industry": 1, "company_type": 1, "flow_mv_sp": 1,
                   "total_mv_sp": 1}
    company_info = mongodb_util.find_query_data_choose_field('company_info', query_company_info, query_field)

    company_info = company_info.set_index(['_id'], drop=True)
    new_concept_symbol_df = new_concept_symbol_df.set_index(['symbol'], drop=False)

    new_concept_symbol_df = pd.merge(new_concept_symbol_df, company_info, how='outer',
                                     left_index=True, right_index=True)
    query = {'concept_code': concept_code}
    exist_concept_detail = mongodb_util.find_query_data('em_stock_concept_detail', query)
    if data_frame_util.is_empty(exist_concept_detail):
        mongodb_util.save_mongo(new_concept_symbol_df, 'em_stock_concept_detail')
    else:
        exist_concept_detail_symbol_list = list(exist_concept_detail['symbol'])
        new_concept_symbol_df = new_concept_symbol_df.loc[~(
            new_concept_symbol_df['symbol'].isin(exist_concept_detail_symbol_list))]
        if new_concept_symbol_df.shape[0] > 0:
            mongodb_util.save_mongo(new_concept_symbol_df, 'em_stock_concept_detail')
    # update_company_info(new_concept_symbol_df, concept_code, concept_name, str_day)
    # # 公司缓存信息清除
    # common_service_fun_api.company_info_industry_cache_clear()


if __name__ == '__main__':
    get_concept_name('BK1134')

    sync_concept_detail('BK1055')
    get_max_concept_code()
