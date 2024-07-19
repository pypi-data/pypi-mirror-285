import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)

import time
import datetime
from mns_common.db.MongodbUtil import MongodbUtil
import mns_scheduler.concept.ths.common.ths_concept_sync_common_api as ths_concept_sync_common_api

mongodb_util = MongodbUtil('27017')


# 通过概念指数同步所有概念下的股票组成

# 同步概念下所有股票组成
def update_concept_all_detail_info():
    query = {"symbol": {'$exists': True}}
    new_concept_list = mongodb_util.find_query_data("ths_concept_list", query)
    new_concept_list = new_concept_list.sort_values(by=['symbol'], ascending=False)
    if new_concept_list.shape[0] > 0:
        for one_concept in new_concept_list.itertuples():
            now_date_time = datetime.datetime.now()
            str_day = now_date_time.strftime('%Y-%m-%d')
            str_now_time = now_date_time.strftime('%Y-%m-%d %H:%M:%S')
            new_concept_symbol_df = ths_concept_sync_common_api.get_concept_detail_info_web(one_concept.symbol)

            if new_concept_symbol_df is None or new_concept_symbol_df.shape[0] == 0:
                time.sleep(10)
                continue
            time.sleep(1)
            new_concept_symbol_df.loc[:, 'way'] = 'index_sync'
            ths_concept_sync_common_api.save_ths_concept_detail(new_concept_symbol_df, one_concept.name,
                                                                str_day, str_now_time, one_concept.symbol)


if __name__ == '__main__':
    now_date = datetime.datetime.now()
    begin_date = now_date.strftime('%Y-%m-%d %H:%M:%S')
    print('同步开始:' + begin_date)
    update_concept_all_detail_info()
    now_date = datetime.datetime.now()
    end_date = now_date.strftime('%Y-%m-%d %H:%M:%S')
    print('同步结束:' + end_date)
