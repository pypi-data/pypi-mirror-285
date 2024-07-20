import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)
from loguru import logger

from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.utils.data_frame_util as data_frame_util
import pandas as pd
from datetime import datetime
import akshare as ak
import mns_scheduler.concept.ths.common.ths_concept_sync_common_api as ths_concept_sync_common_api

import mns_scheduler.concept.clean.ths_concept_clean_api as ths_concept_clean_api
import mns_scheduler.concept.common.detaill.ths_concept_detail_api as ths_concept_detail_api
mongodb_util = MongodbUtil('27017')


# 与概念接口对比 找出缺失数据和名称不一样的数据

def sync_new_ths_concept_by_ak_api():
    stock_board_concept_name_ths_df = ak.stock_board_concept_name_ths()
    stock_board_concept_name_ths_df = stock_board_concept_name_ths_df.rename(columns={"日期": "str_day",
                                                                                      "概念名称": "concept_name",
                                                                                      "成分股数量": "numbers",
                                                                                      "网址": "url",
                                                                                      "代码": "concept_code",
                                                                                      })

    stock_board_concept_name_ths_df['str_day'].fillna(datetime(1970, 1, 1), inplace=True)
    stock_board_concept_name_ths_df.concept_name = stock_board_concept_name_ths_df.concept_name.str.replace('（', '(')
    stock_board_concept_name_ths_df.concept_name = stock_board_concept_name_ths_df.concept_name.str.replace('）', ')')

    stock_board_concept_name_ths_df['str_day'] = stock_board_concept_name_ths_df['str_day'].apply(
        lambda x: datetime.strftime(x, '%Y-%m-%d'))

    # 同花顺概念列表
    ths_concept_list_exist = mongodb_util.find_all_data('ths_concept_list')

    for concept_one in stock_board_concept_name_ths_df.itertuples():
        try:
            exist_concept_df_one = ths_concept_list_exist.loc[
                (ths_concept_list_exist['name'] == concept_one.concept_name)
                | (ths_concept_list_exist['web_concept_code'] == concept_one.concept_code)]
            now_date = datetime.now()
            str_now_time = now_date.strftime('%Y-%m-%d %H:%M:%S')
            str_day = concept_one.str_day
            if data_frame_util.is_empty(exist_concept_df_one):
                concept_code = concept_one.concept_code

                diff_one = {
                    '_id': int(concept_code),
                    'symbol': int(concept_code),
                    'name': concept_one.concept_name,
                    'url': concept_one.url,
                    'str_day': str_day,
                    'success': True,
                    'str_now_time': str_now_time,
                    'web_concept_code': int(concept_one.concept_code),
                    'web_concept_url': concept_one.url,
                    'valid': True
                }
                diff_one_df = pd.DataFrame(diff_one, index=[1])
                mongodb_util.save_mongo(diff_one_df, 'ths_concept_list')
                url = 'http://q.10jqka.com.cn/gn/detail/code/' + str(concept_one.concept_code)
                # 新增概念信息处理
                handle_new_concept_msg(concept_code, concept_one.concept_name, url)
                new_concept_symbol_df = get_concept_detail_info_web(concept_code)
                if new_concept_symbol_df is None or new_concept_symbol_df.shape[0] == 0:
                    return None
                new_concept_symbol_df.loc[:, 'way'] = 'index_sync'
                ths_concept_sync_common_api.save_ths_concept_detail(new_concept_symbol_df, concept_one.concept_name,
                                                                    str_day,
                                                                    str_now_time, concept_code)
                logger.info("新增同花顺新概念:{}", concept_one.concept_name)
        except BaseException as e:
            logger.error("同步概念:{},信息异常:{}", concept_one.concept_name, e)


def handle_new_concept_msg(concept_code, concept_name, url):
    # 推送新概念信息到微信
    ths_concept_sync_common_api.push_msg_to_we_chat_web(concept_code, concept_name,
                                                        url)
    # 更新ths概念信息
    ths_concept_clean_api.update_ths_concept_info()


# 获取web端 新增概念详情
def get_concept_detail_info_web(concept_code):
    new_concept_symbol_list = ths_concept_detail_api.get_ths_concept_detail(concept_code, None)
    if new_concept_symbol_list is None or new_concept_symbol_list.shape[0] == 0:
        return None
    new_concept_symbol_list = new_concept_symbol_list[ths_concept_sync_common_api.order_fields]
    new_concept_symbol_list['_id'] = str(concept_code) + '-' + new_concept_symbol_list['symbol']
    return new_concept_symbol_list


if __name__ == '__main__':
    # get_concept_detail_info_web(886068)
    sync_new_ths_concept_by_ak_api()
