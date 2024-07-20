import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from mns_common.db.MongodbUtil import MongodbUtil
from loguru import logger

mongodb_util = MongodbUtil('27017')
from mns_common.db.MongodbUtilLocal import MongodbUtil as MongodbUtilLocal

mongodbUtilLocal = MongodbUtilLocal('27017')


def sync_remote_open_data(str_day):
    query_remote = {"str_day": str_day}
    realtime_quotes_now_open_df = mongodb_util.find_query_data('realtime_quotes_now_open', query_remote)
    mongodbUtilLocal.insert_mongo(realtime_quotes_now_open_df, 'realtime_quotes_now_open')


if __name__ == '__main__':
    query = {'$and': [{"_id": {"$gte": "2022-03-16"}},
                      {"_id": {"$lte": "2024-06-28"}}]}
    trade_date_list = mongodb_util.find_query_data('trade_date_list', query)
    for trade_one in trade_date_list.itertuples():
        try:
            sync_str_day = trade_one.trade_date
            sync_remote_open_data(sync_str_day)
            logger.info('str_day:{}', sync_str_day)
        except BaseException as e:
            logger.error("同步远程数据异常:{}", e)
