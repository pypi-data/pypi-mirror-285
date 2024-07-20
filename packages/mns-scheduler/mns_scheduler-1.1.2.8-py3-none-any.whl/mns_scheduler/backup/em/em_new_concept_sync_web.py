import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)

import datetime
import time
from loguru import logger
import mns_scheduler.backup.em.em_new_concept_sync_common_api as em_new_concept_sync_common_api


# 同步东财新概念
def sync_new_concept_data():
    concept_code = em_new_concept_sync_common_api.get_max_concept_code()
    # 装换为数字
    concept_code = int(concept_code)

    concept_code = concept_code + 1

    while concept_code < em_new_concept_sync_common_api.max_concept_code:
        try:
            now_date = datetime.datetime.now()
            str_day = now_date.strftime('%Y-%m-%d')
            str_now_time = now_date.strftime('%Y-%m-%d %H:%M:%S')
            str_concept_code = 'BK' + str(concept_code)
            new_concept_symbol_df = em_new_concept_sync_common_api.sync_concept_detail(str_concept_code)
            if new_concept_symbol_df is None or new_concept_symbol_df.shape[0] == 0:
                concept_code = concept_code + 1
                time.sleep(1)
                continue
            time.sleep(2)
            concept_df_one = em_new_concept_sync_common_api.get_concept_name(str_concept_code)
            # 获取概念名称
            concept_name = list(concept_df_one['concept_name'])[0]

            # 推送新概念信息到微信
            em_new_concept_sync_common_api.push_msg_to_we_chat_web(str_concept_code, concept_name)
            # 保存新概念信息到数据库
            em_new_concept_sync_common_api.save_em_concept_list(str_concept_code, concept_name, str_day, str_now_time,
                                                                concept_df_one)
            # 保存新概念详细信息到数据库
            em_new_concept_sync_common_api.save_ths_concept_detail(new_concept_symbol_df, concept_name, str_day,
                                                                   str_now_time, str_concept_code)

            concept_code = concept_code + 1
        except BaseException as e:
            logger.error("同步新概念异常:{},concept_code:{}", e, concept_code)
            concept_code = concept_code + 1


if __name__ == '__main__':
    sync_new_concept_data()
