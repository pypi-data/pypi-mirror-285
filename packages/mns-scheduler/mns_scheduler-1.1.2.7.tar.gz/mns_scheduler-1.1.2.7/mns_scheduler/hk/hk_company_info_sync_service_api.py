import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_common.api.em.east_money_stock_hk_api as east_money_stock_hk_api
import akshare as ak
import mns_common.constant.db_name_constant as db_name_constant
from mns_common.db.MongodbUtil import MongodbUtil

mongodb_util = MongodbUtil('27017')
COOKIE = 'qgqp_b_id=1e0d79428176ed54bef8434efdc0e8c3; mtp=1; ct=QVRY_s8Tiag1WfK2tSW2n03qpsX-PD8aH_rIjKVooawX8K33UVnpIofK088lD1lguWlE_OEIpQwn3PJWFPhHvSvyvYr4Zka3l4vxtZfH1Uikjtyy9z1H4Swo0rQzMKXncVzBXiOo5TjE-Dy9fcoG3ZF7UVdQ35jp_cFwzOlpK5Y; ut=FobyicMgeV51lVMr4ZJXvn-72bp0oeSOvtzifFY_U7kBFtR6og4Usd-VtBM5XBBvHq0lvd9xXkvpIqWro9EDKmv6cbKOQGyawUSMcKVP57isZCaM7lWQ6jWXajvTfvV4mIR-W_MZNK8VY0lL9W4qNMniJ6PBn_gkJsSAJCadmsyI9cxmjx--gR4m54pdF_nie_y4iWHys83cmWR2R7Bt1KKqB25OmkfCQTJJqIf7QsqangVGMUHwMC39Z9QhrfCFHKVNrlqS503O6b9GitQnXtvUdJhCmomu; pi=4253366368931142%3Bp4253366368931142%3B%E8%82%A1%E5%8F%8B9x56I87727%3BYNigLZRW%2FzMdGgVDOJbwReDWnTPHl51dB0gQLiwaCf1XY98mlJYx6eJbsoYr5Nie%2BX1L%2BzaMsec99KkX%2BT29Ds1arfST7sIBXxjUQ3dp11IPUnXy64PaBFRTHzMRWnCFJvvhc%2FAI41rXSGXolC8YMxI%2BvyPS%2BuErwgOVjC5vvsIiKeO7TLyKkhqqQJPX%2F7RWC5Sf3QLh%3Bdwjn4Xho10%2FKjqOgTWs%2FJF4%2FkdKzeuBwM8sz9aLvJovejAkCAyGMyGYA6AE67Xk2Ki7x8zdfBifF2DG%2Fvf2%2BXAYN8ZVISSEWTIXh32Z5MxEacK4JBTkqyiD93e1vFBOFQ82BqaiVmntUq0V6FrTUHGeh1gG5Sg%3D%3D; uidal=4253366368931142%e8%82%a1%e5%8f%8b9x56I87727; sid=170711377; vtpst=|; quote_lt=1; websitepoptg_api_time=1715777390466; emshistory=%5B%22%E8%BD%AC%E5%80%BA%E6%A0%87%22%2C%22%E8%BD%AC%E5%80%BA%E6%A0%87%E7%9A%84%22%5D; st_si=00364513876913; st_asi=delete; HAList=ty-116-00700-%u817E%u8BAF%u63A7%u80A1%2Cty-1-688695-%u4E2D%u521B%u80A1%u4EFD%2Cty-1-600849-%u4E0A%u836F%u8F6C%u6362%2Cty-1-603361-%u6D59%u6C5F%u56FD%u7965%2Cty-1-603555-ST%u8D35%u4EBA%2Cty-0-000627-%u5929%u8302%u96C6%u56E2%2Cty-0-002470-%u91D1%u6B63%u5927%2Cty-0-832876-%u6167%u4E3A%u667A%u80FD%2Cty-0-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cty-107-CWB-%u53EF%u8F6C%u503AETF-SPDR; st_pvi=26930719093675; st_sp=2024-04-28%2017%3A27%3A05; st_inirUrl=https%3A%2F%2Fcn.bing.com%2F; st_sn=23; st_psi=20240517111108288-113200301321-2767127768'


def get_hk_ggt_component():
    stock_hk_ggt_components_em_df = ak.stock_hk_ggt_components_em()
    stock_hk_ggt_components_em_df = stock_hk_ggt_components_em_df.rename(columns={
        "序号": "index",
        "代码": "symbol",
        "名称": "name"
    })
    return stock_hk_ggt_components_em_df


# https://quote.eastmoney.com/center/gridlist.html#hk_stocks
def sync_hk_company_info():
    hk_real_time_df = east_money_stock_hk_api.hk_real_time_quotes(COOKIE)

    hk_real_time_df = hk_real_time_df[[
        "symbol",
        "name",
        "chg",
        "total_mv",
        "flow_mv",
        "list_date",
        "industry",
        "amount",
        "now_price"
    ]]
    # 排除基金
    hk_real_time_df = hk_real_time_df.loc[hk_real_time_df['total_mv'] != '-']

    stock_hk_ggt_components_em_df = get_hk_ggt_component()
    stock_hk_ggt_components_symbol_list = list(stock_hk_ggt_components_em_df['symbol'])
    hk_real_time_df['hk_ggt'] = False
    hk_real_time_df.loc[hk_real_time_df['symbol'].isin(stock_hk_ggt_components_symbol_list), 'hk_ggt'] = True
    hk_real_time_df.loc[hk_real_time_df['industry'] == '-', 'industry'] = '其他'

    hk_real_time_df['_id'] = hk_real_time_df['symbol']

    hk_real_time_df.fillna(0, inplace=True)

    mongodb_util.save_mongo(hk_real_time_df, db_name_constant.COMPANY_INFO_HK)


if __name__ == '__main__':
    sync_hk_company_info()
