import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from loguru import logger

db_name_list = [
    # 'company_info', 'company_info_base', 'company_info_his', 'company_info_hk', 'de_list_stock',
    # 'em_stock_asset_liability',
    # 'em_stock_profit',
    # 'k_line_info',
    'kpl_best_choose_daily', 'kpl_best_choose_his', 'kpl_best_choose_index',
    'kpl_best_choose_index_detail',
    'kpl_his_quotes', 'recent_hot_stocks', 'self_black_stock', 'self_choose_plate', 'self_choose_stock', 'sse_info_uid',
    'stock_gdfx_free_top_10', 'stock_high_chg_pool', 'stock_interactive_question', 'stock_qfq_daily',
    'stock_qfq_monthly', 'stock_qfq_weekly', 'stock_zt_pool', 'stock_zt_pool_five', 'stock_zb_pool', 'sw_industry',
    'ths_concept_list', 'ths_stock_concept_detail', 'ths_stock_concept_detail_app', 'ths_zt_pool',
    'today_new_concept_list',
    'trade_date_list', 'realtime_quotes_now_zt_new', 'realtime_quotes_now_open', 'realtime_quotes_now_zt_new_kc_open']


def db_export(db, col):
    cmd = 'F:/mongo/bin/mongodump.exe --host ' + db + ' -d patience -c ' + col + ' -o D:/back'
    os.system(cmd)
    logger.info("export finished:{}", col)


def db_import(db, col):
    cmd = 'F:/mongo/bin/mongorestore.exe --host ' + db + ' -d patience -c ' + col + ' D:/back/patience/' + col + '.bson'
    os.system(cmd)

    path = 'D:\\back\\patience\\' + col + '.bson'
    cmd_del = 'del /F /S /Q ' + path
    os.system(cmd_del)

    logger.info("import finished:{}", col)


def collection_to_local():
    for db_name in db_name_list:
        try:
            db_export('127.0.0.1:27017', db_name)
            db_import('192.168.1.6:27017', db_name)
            logger.info("同步到集合:{}", db_name)
        except BaseException as e:
            logger.error("出现异常:{}", e)


if __name__ == '__main__':
    collection_to_local()
