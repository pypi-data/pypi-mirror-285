import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_scheduler.concept.common.detaill.ths_concept_detail_api as ths_concept_detail_api
import mns_common.api.ths.concept.web.ths_concept_index_web as ths_concept_index_web
import datetime
import time
import mns_common.api.msg.push_msg_api as push_msg_api
from loguru import logger
import mns_scheduler.concept.ths.common.ths_concept_sync_common_api as ths_concept_sync_common_api
import mns_scheduler.concept.clean.ths_concept_clean_api as ths_concept_clean_api
from mns_common.db.MongodbUtil import MongodbUtil

mongodb_util = MongodbUtil('27017')


# 获取web端 新增概念详情
def get_concept_detail_info_web(concept_code):
    new_concept_symbol_list = ths_concept_detail_api.get_ths_concept_detail(concept_code, None)
    if new_concept_symbol_list is None or new_concept_symbol_list.shape[0] == 0:
        return None
    new_concept_symbol_list = new_concept_symbol_list[ths_concept_sync_common_api.order_fields]
    new_concept_symbol_list['_id'] = str(concept_code) + '-' + new_concept_symbol_list['symbol']
    return new_concept_symbol_list


# web端获取新概念消息推送
def push_msg_to_we_chat_web(concept_code, concept_name):
    url = 'http://q.10jqka.com.cn/thshy/detail/code/' + str(concept_code)
    msg = "概念代码:" + str(concept_code) + "," + "概念名称:" + concept_name + "," + "url:   " + url
    title = "新增同花顺概念:" + str(concept_code) + "-" + concept_name
    push_msg_api.push_msg_to_wechat(title, msg)


#     # 同步同花顺新增概念指数通过web端接口爬取
def sync_new_concept_data_by_web():
    concept_code = ths_concept_sync_common_api.get_max_concept_code()
    concept_code = concept_code + 1

    while concept_code < ths_concept_sync_common_api.max_concept_code:
        try:
            now_date = datetime.datetime.now()
            str_day = now_date.strftime('%Y-%m-%d')
            str_now_time = now_date.strftime('%Y-%m-%d %H:%M:%S')
            new_concept_symbol_df = get_concept_detail_info_web(concept_code)
            if new_concept_symbol_df is None or new_concept_symbol_df.shape[0] == 0:
                concept_code = concept_code + 1
                time.sleep(1)
                continue
            time.sleep(2)
            concept_name = ths_concept_index_web.get_concept_name(concept_code)
            concept_name = concept_name.replace('（', '(')
            concept_name = concept_name.replace('）', ')')

            url = 'http://q.10jqka.com.cn/thshy/detail/code/' + str(concept_code)
            # 推送新概念信息到微信
            handle_new_concept_msg(concept_code, concept_name, url)
            # 保存新概念信息到概念列表
            ths_concept_sync_common_api.save_ths_concept_list(concept_code, concept_name, str_day, str_now_time)
            # 保存新概念详细信息到数据库
            new_concept_symbol_df.loc[:, 'way'] = 'index_sync'
            ths_concept_sync_common_api.save_ths_concept_detail(new_concept_symbol_df, concept_name, str_day,
                                                                str_now_time, concept_code)

            concept_code = concept_code + 1
        except BaseException as e:
            logger.error("同步新概念异常:{},concept_code:{}", e, concept_code)
            concept_code = concept_code + 1


def handle_new_concept_msg(concept_code, concept_name, url):
    # 推送新概念信息到微信
    ths_concept_sync_common_api.push_msg_to_we_chat_web(concept_code, concept_name,
                                                        url)
    # 更新ths概念信息
    ths_concept_clean_api.update_ths_concept_info()


if __name__ == '__main__':
    # code = 886025
    # push_msg_to_we_chat_web(code, name)
    # get_concept_detail_info_web(886026)
    # get_concept_detail_info_web(886035)
    sync_new_concept_data_by_web()
