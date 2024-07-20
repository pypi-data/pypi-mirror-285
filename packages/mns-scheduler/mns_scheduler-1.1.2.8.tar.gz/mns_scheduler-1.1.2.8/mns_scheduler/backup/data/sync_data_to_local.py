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

db_name_list = [
    # 'company_info', 'company_info_base', 'company_info_his', 'company_info_hk', 'de_list_stock',
    # 'em_stock_asset_liability',
    # 'em_stock_profit',
    # 'k_line_info',
    # 'kpl_best_choose_daily',
    # 'kpl_best_choose_his',
    # 'kpl_best_choose_index',
    # 'kpl_best_choose_index_detail',
    # 'kpl_his_quotes',
    # 'stock_qfq_daily',
    # 'stock_qfq_monthly',
    # 'stock_qfq_weekly',
    # 'stock_gdfx_free_top_10',
    # 'recent_hot_stocks',
    # 'self_black_stock',
    # 'self_choose_plate', 'self_choose_stock', 'sse_info_uid',
    # 'stock_high_chg_pool', 'stock_interactive_question',
    # 'stock_zt_pool', 'stock_zt_pool_five', 'stock_zb_pool', 'sw_industry',
    # 'ths_concept_list', 'ths_stock_concept_detail','ths_zt_pool',
    # 'today_new_concept_list',
    # 'trade_date_list',
    # 'ths_stock_concept_detail_app',
    "stock_zt_pool"
]


def sync_collection_to_local():
    for db_name in db_name_list:
        try:
            df_data = mongodb_util.find_all_data(db_name)
            mongodbUtilLocal.save_mongo(df_data, db_name)
            logger.info("同步到集合:{}", db_name)
        except BaseException as e:
            logger.error("出现异常:{}", e)


if __name__ == '__main__':
    sync_collection_to_local()
