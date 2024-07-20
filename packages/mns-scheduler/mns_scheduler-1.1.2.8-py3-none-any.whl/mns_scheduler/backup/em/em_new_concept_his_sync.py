import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)

import akshare as ak
from loguru import logger
from datetime import datetime
import mns_common.utils.date_handle_util as date_handle_util
import mns_common.db.MongodbUtil as MongodbUtil
import mns_scheduler.backup.em.em_new_concept_sync_common_api as em_new_concept_sync_common_api
import mns_common.api.em.em_concept_index_api as em_concept_index_api

mongodb_util = MongodbUtil('27017')


# 同步概念k线
def sync_concept_k_line(symbol, period, start_date, end_date, adjust):
    try:
        stock_board_concept_hist_em_df = ak.stock_board_concept_hist_em(
            symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust
        )
        stock_board_concept_hist_em_df = stock_board_concept_hist_em_df.rename(columns={"日期": "date",
                                                                                        "开盘": "open",
                                                                                        "收盘": "close",
                                                                                        "最高": "high",
                                                                                        "最低": "low",
                                                                                        "涨跌幅": "chg",
                                                                                        "涨跌额": "change",
                                                                                        "成交量": "volume",
                                                                                        "成交额": "amount",
                                                                                        "振幅": "pct_chg",
                                                                                        "换手率": "exchange"
                                                                                        })

        return stock_board_concept_hist_em_df
    except BaseException as e:
        logger.error("同步东方财富概念信息异常:{}", e)
        return None


# 同步所有历史概念数据
def sync_his_em_concept():
    now_date = datetime.now()
    str_day = now_date.strftime('%Y-%m-%d')

    all_concept_list = em_concept_index_api.sync_all_concept()
    for stock_one in all_concept_list.itertuples():
        try:
            stock_one_df_copy = all_concept_list.loc[all_concept_list['concept_code'] == stock_one.concept_code]
            stock_one_df = stock_one_df_copy.copy()

            stock_board_concept_hist_em_df = sync_concept_k_line(
                symbol=stock_one.concept_name, period="daily", start_date="19980729",
                end_date=date_handle_util.no_slash_date(str_day), adjust="qfq"
            )
            stock_board_concept_hist_em_df = stock_board_concept_hist_em_df.sort_values(by=['date'], ascending=True)
            stock_board_concept_hist_em_df_first_day = stock_board_concept_hist_em_df.iloc[0:1]

            list_date = list(stock_board_concept_hist_em_df_first_day['date'])[0]
            str_now_time = list_date + " " + "09:10:00"
            stock_one_df.loc[:, 'str_now_time'] = str_now_time

            stock_one_df.loc[:, 'str_day'] = list_date

            stock_one_df['_id'] = stock_one_df['concept_code']
            stock_one_df['url'] = "http://quote.eastmoney.com/center/boardlist.html#boards-" + stock_one.concept_code
            stock_one_df['success'] = True

            mongodb_util.save_mongo(stock_one_df, 'em_concept_list')
            #
            concept_detail_list = em_new_concept_sync_common_api.sync_concept_detail(stock_one.concept_code)

            concept_detail_list.loc[:, 'concept_code'] = stock_one.concept_code
            concept_detail_list.loc[:, 'concept_name'] = stock_one.concept_name
            concept_detail_list.loc[:, 'str_day'] = list_date

            concept_detail_list.loc[:, 'str_now_time'] = str_now_time

            concept_detail_list['_id'] = concept_detail_list['symbol'] + '-' + concept_detail_list['concept_code']

            mongodb_util.insert_mongo(concept_detail_list, 'em_stock_concept_detail')
        except BaseException as e:
            logger.error("发生异常:{}", e)
            continue


if __name__ == '__main__':
    # all_concept = sync_all_concept()
    # all_concept = all_concept.loc[~(all_concept['list_day'] == '-')]
    # all_concept = all_concept.sort_values(by=['list_day'], ascending=False)
    sync_his_em_concept()
    # stock_board_concept_hist_em_df = sync_concept_k_line(
    #     symbol="车联网", period="daily", start_date="20220101", end_date="20221128", adjust=""
    # )
    # sync_concept_detail('MLOps概念')
