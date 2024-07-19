import sys
import os

import pandas as pd
from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.component.company.company_common_service_api as company_common_service_api

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)
mongodb_util = MongodbUtil('27017')
import mns_common.api.msg.push_msg_api as push_msg_api
import mns_scheduler.company_info.base.sync_company_base_info_api as company_info_sync_api
import mns_scheduler.company_info.clean.company_info_clean_api as company_info_clean_api
import mns_scheduler.concept.common.detaill.ths_concept_detail_api as ths_concept_detail_api
import mns_common.component.concept.ths_concept_common_service_api as ths_concept_common_service_api
import mns_common.component.company.company_common_service_new_api as company_common_service_new_api
import mns_common.utils.data_frame_util as data_frame_util
import mns_common.constant.db_name_constant as db_name_constant

max_concept_code = 886110

order_fields = [
    "index",
    "symbol",
    "name",
    "now_price",
    "chg",
    "change",
    "exchange",
    "amount",
    "concept_code",
]


# 推送到手机
def push_msg_to_we_chat_web(concept_code, concept_name, url):
    msg = "概念代码:" + str(concept_code) + "," + "概念名称:" + concept_name + "," + "url:   " + url
    title = "新增同花顺概念:" + str(concept_code) + "-" + concept_name
    push_msg_api.push_msg_to_wechat(title, msg)


# 保存新概念信息到数据库
def save_ths_concept_list(concept_code, concept_name, str_day, str_now_time):
    url = 'http://q.10jqka.com.cn/thshy/detail/code/' + str(concept_code)
    ths_concept_list = pd.DataFrame([
        [concept_code, concept_code, concept_name, str_day, url, str_now_time, True, True],
    ], columns=['_id', 'symbol', 'name', 'str_day', 'url', 'str_now_time', 'success', 'valid'])
    mongodb_util.save_mongo(ths_concept_list, 'ths_concept_list')


# 获取最大概念代码
def get_max_concept_code():
    query = {"symbol": {'$ne': 'null'}, "success": True}
    ths_concept_max = mongodb_util.descend_query(query, 'ths_concept_list', 'symbol', 1)
    if ths_concept_max.shape[0] == 0:
        concept_code = 885284
    else:
        concept_code = list(ths_concept_max['symbol'])[0]

    return concept_code


# 保存新概念详细信息到数据库
def save_ths_concept_detail(new_concept_symbol_df,
                            concept_name, str_day,
                            str_now_time, concept_code):
    concept_code = int(concept_code)
    new_concept_symbol_df['symbol'] = new_concept_symbol_df['symbol'].astype(str)
    new_concept_symbol_df['_id'] = str(concept_code) + '_' + new_concept_symbol_df['symbol']
    new_concept_symbol_df['concept_code'] = concept_code
    new_concept_symbol_df['concept_name'] = concept_name

    new_concept_symbol_df['concept_name'] = new_concept_symbol_df['concept_name'].replace(" ", "")

    all_ths_concept_df = ths_concept_common_service_api.get_all_ths_concept()
    ths_concept_one_df = all_ths_concept_df.loc[all_ths_concept_df['symbol'] == int(concept_code)]

    if data_frame_util.is_empty(ths_concept_one_df):
        concept_create_day = str_day
    else:
        concept_create_day = list(ths_concept_one_df['str_day'])[0]

    new_concept_symbol_df['str_day'] = str_day
    new_concept_symbol_df['str_now_time'] = str_now_time
    new_concept_symbol_df['concept_create_day'] = concept_create_day

    new_concept_symbol_list = list(new_concept_symbol_df['symbol'])

    query_company_info = {'symbol': {'$in': new_concept_symbol_list}}
    query_company_info_key = str(query_company_info)
    query_field = {"first_industry": 1, "first_industry": 1, "industry": 1,
                   "company_type": 1, "flow_mv_sp": 1,
                   "total_mv_sp": 1}
    query_field_key = str(query_field)
    company_info = company_common_service_new_api.get_company_info_by_field(query_company_info_key, query_field_key)

    if 'industry' in new_concept_symbol_df.columns:
        del new_concept_symbol_df['industry']
    if 'company_type' in new_concept_symbol_df.columns:
        del new_concept_symbol_df['company_type']
    if 'flow_mv_sp' in new_concept_symbol_df.columns:
        del new_concept_symbol_df['flow_mv_sp']
    if 'total_mv_sp' in new_concept_symbol_df.columns:
        del new_concept_symbol_df['total_mv_sp']

    company_info = company_info.set_index(['_id'], drop=True)
    new_concept_symbol_df = new_concept_symbol_df.set_index(['symbol'], drop=False)

    new_concept_symbol_df = pd.merge(new_concept_symbol_df, company_info, how='outer',
                                     left_index=True, right_index=True)

    if 'index' not in company_info.columns:
        new_concept_symbol_df['index'] = 0

    if 'change' not in company_info.columns:
        new_concept_symbol_df['change'] = 0

    new_concept_symbol_df['concept_name'] = new_concept_symbol_df['concept_name'].replace(" ", "")

    if bool(1 - ('way' in new_concept_symbol_df.columns)):
        new_concept_symbol_df['way'] = 'symbol_sync'
    if "long" not in new_concept_symbol_df.columns:
        new_concept_symbol_df['long'] = ''
    if "short" not in new_concept_symbol_df.columns:
        new_concept_symbol_df['short'] = new_concept_symbol_df['long']
    new_concept_symbol_df = new_concept_symbol_df[[
        "_id",
        "index",
        "symbol",
        "name",
        "now_price",
        "chg",
        "change",
        "exchange",
        "amount",
        "concept_code",
        "concept_name",
        "str_day",
        "str_now_time",
        "industry",
        "flow_mv_sp",
        "total_mv_sp",
        "company_type",
        "concept_create_day",
        "way",
        "long",
        'short'
    ]]
    query_detail = {"concept_code": int(concept_code)}
    exist_concept_detail = mongodb_util.find_query_data(db_name_constant.THS_STOCK_CONCEPT_DETAIL, query_detail)
    if exist_concept_detail is None or exist_concept_detail.shape[0] == 0:
        mongodb_util.save_mongo(new_concept_symbol_df, db_name_constant.THS_STOCK_CONCEPT_DETAIL)
        # 保存到当日新增概念列表
        new_concept_symbol_df['concept_type'] = 'ths'
        mongodb_util.save_mongo(new_concept_symbol_df, db_name_constant.TODAY_NEW_CONCEPT_LIST)
    else:
        exist_concept_detail_symbol_list = list(exist_concept_detail['symbol'])
        new_concept_symbol_df = new_concept_symbol_df.loc[~(
            new_concept_symbol_df['symbol'].isin(exist_concept_detail_symbol_list))]
        if new_concept_symbol_df.shape[0] > 0:
            mongodb_util.save_mongo(new_concept_symbol_df, db_name_constant.THS_STOCK_CONCEPT_DETAIL)
            # 保存到当日新增概念列表
            new_concept_symbol_df['concept_type'] = 'ths'
            mongodb_util.save_mongo(new_concept_symbol_df, db_name_constant.TODAY_NEW_CONCEPT_LIST)
    update_company_info(new_concept_symbol_df)
    # 公司缓存信息清除
    company_common_service_api.company_info_industry_cache_clear()


# 更新公司表信息 todo 清空cache 公司表中  common_service_fun_api.py  get_company_info_industry
def update_company_info(new_concept_symbol_df):
    if new_concept_symbol_df.shape[0] > 0:
        symbol_list = list(new_concept_symbol_df['symbol'])
        company_info_sync_api.sync_company_base_info(symbol_list)
        company_info_clean_api.fix_company_industry(None)
        # 公司缓存信息清除
        company_common_service_api.company_info_industry_cache_clear()


def get_concept_detail_info_web(concept_code):
    new_concept_symbol_list = ths_concept_detail_api.get_ths_concept_detail(concept_code, None)
    if new_concept_symbol_list is None or new_concept_symbol_list.shape[0] == 0:
        return None
    new_concept_symbol_list['_id'] = str(concept_code) + '-' + new_concept_symbol_list['symbol']
    return new_concept_symbol_list
