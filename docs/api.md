# 交易所期货数据

"get_cffex_daily", # 中国金融期货交易所每日交易数据
"get_cffex_rank_table", # 中国金融期货交易所前 20 会员持仓数据明细
"get_czce_daily", # 郑州商品交易所每日交易数据
"get_rank_table_czce", # 郑州商品交易所前 20 会员持仓数据明细
"get_dce_daily", # 大连商品交易所每日交易数据
"get_gfex_daily", # 广州期货交易所每日交易数据
"get_ine_daily", # 上海国际能源交易中心每日交易数据
"futures_settlement_price_sgx", # 新加坡交易所期货品种每日交易数据
"get_dce_rank_table", # 大连商品交易所前 20 会员持仓数据明细
"get_futures_daily", # 中国金融期货交易所每日基差数据
"get_rank_sum", # 四个期货交易所前 5, 10, 15, 20 会员持仓排名数据
"get_rank_sum_daily", # 每日四个期货交易所前 5, 10, 15, 20 会员持仓排名数据
"futures_dce_position_rank", # 大连商品交易所前 20 会员持仓排名数据
"get_receipt", # 大宗商品注册仓单数据
"get_roll_yield", # 某一天某品种(主力和次主力)或固定两个合约的展期收益率
"get_roll_yield_bar", # 展期收益率
"get_shfe_daily", # 上海期货交易所每日交易数据
"get_shfe_rank_table", # 上海期货交易所前 20 会员持仓数据明细
"get_shfe_v_wap", # 上海期货交易所日成交均价数据
"futures_spot_price", # 具体交易日大宗商品现货价格及相应基差数据
"futures_spot_price_previous", # 具体交易日大宗商品现货价格及相应基差数据-该接口补充历史数据
"futures_spot_price_daily" # 一段交易日大宗商品现货价格及相应基差数据
"futures_warehouse_receipt_czce" # 郑州商品交易所-交易数据-仓单日报
"futures_shfe_warehouse_receipt" # 上海期货交易所-交易数据-仓单日报
"futures_warehouse_receipt_dce" # 大连商品交易所-交易数据-仓单日报
"futures_gfex_warehouse_receipt" # 广州期货交易所-行情数据-仓单日报
"futures_rule" # 国泰君安-交易日历

# 交易所商品期权数据

"option_hist_dce" # 提供大连商品交易所商品期权数据
"option_hist_czce" # 提供郑州商品交易所商品期权数据
"option_hist_shfe" # 提供上海期货交易所商品期权数据
"option_hist_gfex" # 提供广州期货交易所商品期权数据
"option_vol_gfex" # 提供广州期货交易所-合约隐含波动率数据
"option_vol_shfe" # 提供上海期货交易所-合约隐含波动率数据
"option_hist_yearly_czce" # 郑州商品交易所-交易数据-历史行情下载-期权历史行情下载

# 中国银行间市场债券行情数据

"get_bond_market_quote" # 债券市场行情-现券市场成交行情数据
"get_bond_market_trade" # 债券市场行情-现券市场做市报价数据

# 外汇

"get_fx_spot_quote" # 人民币外汇即期报价数据
"get_fx_swap_quote" # 人民币外汇远掉报价数据
"get_fx_pair_quote" # 外币对即期报价数据

# 宏观-欧洲

"macro_euro_interest_rate" # 欧洲央行决议报告

# 宏观-主要机构

"macro_cons_gold" # 全球最大黄金 ETF—SPDR Gold Trust 持仓报告
"macro_cons_silver" # 全球最大白银 ETF--iShares Silver Trust 持仓报告
"macro_cons_opec_month" # 欧佩克报告

# 交易所金融期权数据

"get_finance_option" # 提供上海证券交易所期权数据

# 新浪财经-美股

"get_us_stock_name" # 获得美股的所有股票代码
"stock_us_spot" # 美股行情报价
"stock_us_daily" # 美股的历史数据(包括前复权因子)

# A+H 股实时行情数据和历史行情数据

"stock_zh_ah_spot" # A+H 股实时行情数据(延迟 15 分钟)
"stock_zh_ah_daily" # A+H 股历史行情数据(日频)
"stock_zh_ah_name" # A+H 股所有股票代码

# 科创板实时行情数据和历史行情数据

"stock_zh_kcb_spot" # 科创板实时行情数据
"stock_zh_kcb_daily" # 科创板历史行情数据(日频)

# 已实现波动率数据

"article_oman_rv" # O-MAN 已实现波动率
"article_rlab_rv" # Risk-Lab 已实现波动率

# FF 多因子模型数据

"ff_crr" # FF 当前因子

# 指数实时行情和历史行情

"stock_zh_index_daily" # 股票指数历史行情数据
"stock_zh_index_daily_tx" # 股票指数历史行情数据-腾讯
"stock_zh_index_daily_em" # 股票指数历史行情数据-东方财富
"stock_zh_index_spot_sina" # 股票指数实时行情数据-新浪
"stock_zh_index_spot_em" # 股票指数实时行情数据-东财

# 经济政策不确定性(EPU)指数

"article_epu_index" # 主要国家和地区的经济政策不确定性(EPU)指数

# 申万行业指数

"sw_index_third_info" # 申万三级信息
"sw_index_third_cons" # 申万三级信息成份

# 空气质量

"air_quality_hist" # 空气质量历史数据
"air_quality_rank" # 空气质量排行
"air_quality_watch_point" # 空气质量观测点历史数据
"air_city_table" # 所有城市列表

# 全国银行间同业拆借中心-市场数据-市场行情-外汇市场行情

"fx_spot_quote" # 市场行情-外汇市场行情-人民币外汇即期报价
"fx_swap_quote" # 市场行情-债券市场行情-人民币外汇远掉报价
"fx_pair_quote" # 市场行情-债券市场行情-外币对即期报价

# 能源-碳排放权

"energy_carbon_domestic" # 碳排放权-国内
"energy_carbon_bj" # 碳排放权-北京
"energy_carbon_sz" # 碳排放权-深圳
"energy_carbon_eu" # 碳排放权-国际
"energy_carbon_hb" # 碳排放权-湖北
"energy_carbon_gz" # 碳排放权-广州

# 商品现货价格指数

"spot_goods" # 商品现货价格指数

# 中国宏观杠杆率

"macro_cnbs" # 中国宏观杠杆率数据

# 金融期权

"option_finance_board" # 金融期权数据

# 期货连续合约

"futures_main_sina" # 新浪期货连续合约的历史数据

# 机构调研数据

"stock_jgdy_tj_em" # 机构调研数据-统计
"stock_jgdy_detail_em" # 机构调研数据-详细

# 股权质押数据

"stock_gpzy_profile_em" # 股权质押市场概况
"stock_gpzy_pledge_ratio_em" # 上市公司质押比例
"stock_gpzy_pledge_ratio_detail_em" # 重要股东股权质押明细
"stock_gpzy_distribute_statistics_company_em" # 质押机构分布统计-证券公司
"stock_gpzy_distribute_statistics_bank_em" # 质押机构分布统计-银行
"stock_gpzy_industry_data_em" # 上市公司质押比例-行业数据

# 商誉专题数据

"stock_sy_profile_em" # A 股商誉市场概况
"stock_sy_yq_em" # 商誉减值预期明细
"stock_sy_jz_em" # 个股商誉减值明细
"stock_sy_em" # 个股商誉明细
"stock_sy_hy_em" # 行业商誉

# 股票指数-成份股

"index_stock_cons" # 股票指数-成份股-最新成份股
"index_stock_cons_csindex" # 中证指数-成份股
"index_stock_cons_weight_csindex" # 中证指数成份股的权重
"index_stock_info" # 股票指数-成份股-所有可以的指数表
"index_stock_info_sina" # 股票指数-成份股-所有可以的指数表-新浪新接口

# 义乌小商品指数

"index_yw" # 义乌小商品指数

# 世界银行间拆借利率

"rate_interbank" # 银行间拆借利率

# 主要央行利率

"macro_bank_usa_interest_rate" # 美联储利率决议报告
"macro_bank_euro_interest_rate" # 欧洲央行决议报告
"macro_bank_newzealand_interest_rate" # 新西兰联储决议报告
"macro_bank_switzerland_interest_rate" # 瑞士央行决议报告
"macro_bank_english_interest_rate" # 英国央行决议报告
"macro_bank_australia_interest_rate" # 澳洲联储决议报告
"macro_bank_japan_interest_rate" # 日本央行决议报告
"macro_bank_russia_interest_rate" # 俄罗斯央行决议报告
"macro_bank_india_interest_rate" # 印度央行决议报告
"macro_bank_brazil_interest_rate" # 巴西央行决议报告

# 中国

"macro_china_urban_unemployment" # 城镇调查失业率
"macro_china_shrzgm" # 社会融资规模增量统计
"macro_china_gdp_yearly" # 金十数据中心-经济指标-中国-国民经济运行状况-经济状况-中国 GDP 年率报告
"macro_china_cpi_yearly" # 金十数据中心-经济指标-中国-国民经济运行状况-物价水平-中国 CPI 年率报告
"macro_china_cpi_monthly" # 金十数据中心-经济指标-中国-国民经济运行状况-物价水平-中国 CPI 月率报告
"macro_china_ppi_yearly" # 金十数据中心-经济指标-中国-国民经济运行状况-物价水平-中国 PPI 年率报告
"macro_china_exports_yoy" # 金十数据中心-经济指标-中国-贸易状况-以美元计算出口年率报告
"macro_china_imports_yoy" # 金十数据中心-经济指标-中国-贸易状况-以美元计算进口年率
"macro_china_trade_balance" # 金十数据中心-经济指标-中国-贸易状况-以美元计算贸易帐(亿美元)
"macro_china_industrial_production_yoy" # 金十数据中心-经济指标-中国-产业指标-规模以上工业增加值年率
"macro_china_pmi_yearly" # 金十数据中心-经济指标-中国-产业指标-官方制造业 PMI
"macro_china_cx_pmi_yearly" # 金十数据中心-经济指标-中国-产业指标-财新制造业 PMI 终值
"macro_china_cx_services_pmi_yearly" # 金十数据中心-经济指标-中国-产业指标-财新服务业 PMI
"macro_china_non_man_pmi" # 金十数据中心-经济指标-中国-产业指标-中国官方非制造业 PMI
"macro_china_fx_reserves_yearly" # 金十数据中心-经济指标-中国-金融指标-外汇储备(亿美元)
"macro_china_m2_yearly" # 金十数据中心-经济指标-中国-金融指标-M2 货币供应年率
"macro_china_shibor_all" # 金十数据中心-经济指标-中国-金融指标-上海银行业同业拆借报告
"macro_china_hk_market_info" # 金十数据中心-经济指标-中国-金融指标-人民币香港银行同业拆息
"macro_china_daily_energy" # 金十数据中心-经济指标-中国-其他-中国日度沿海六大电库存数据
"macro_china_rmb" # 金十数据中心-经济指标-中国-其他-中国人民币汇率中间价报告
"macro_china_market_margin_sz" # 金十数据中心-经济指标-中国-其他-深圳融资融券报告
"macro_china_market_margin_sh" # 金十数据中心-经济指标-中国-其他-上海融资融券报告
"macro_china_au_report" # 金十数据中心-经济指标-中国-其他-上海黄金交易所报告
"macro_china_lpr" # 中国-利率-贷款报价利率
"macro_china_new_house_price" # 中国-新房价指数
"macro_china_enterprise_boom_index" # 中国-企业景气及企业家信心指数
"macro_china_national_tax_receipts" # 中国-全国税收收入
"macro_china_bank_financing" # 中国-银行理财产品发行数量
"macro_china_new_financial_credit" # 中国-新增信贷数据
"macro_china_fx_gold" # 中国-外汇和黄金储备
"macro_china_stock_market_cap" # 中国-全国股票交易统计表
"macro_china_cpi" # 中国-居民消费价格指数
"macro_china_gdp" # 中国-国内生产总值
"macro_china_ppi" # 中国-工业品出厂价格指数
"macro_china_pmi" # 中国-采购经理人指数
"macro_china_gdzctz" # 中国-城镇固定资产投资
"macro_china_hgjck" # 中国-海关进出口增减情况一览表
"macro_china_czsr" # 中国-财政收入
"macro_china_whxd" # 中国-外汇贷款数据
"macro_china_wbck" # 中国-本外币存款
"macro_china_bond_public" # 中国-债券发行

# 美国

"macro_usa_gdp_monthly" # 金十数据中心-经济指标-美国-经济状况-美国 GDP
"macro_usa_cpi_monthly" # 金十数据中心-经济指标-美国-物价水平-美国 CPI 月率报告
"macro_usa_cpi_yoy" # 东方财富-经济数据一览-美国-CPI 年率
"macro_usa_core_cpi_monthly" # 金十数据中心-经济指标-美国-物价水平-美国核心 CPI 月率报告
"macro_usa_personal_spending" # 金十数据中心-经济指标-美国-物价水平-美国个人支出月率报告
"macro_usa_retail_sales" # 金十数据中心-经济指标-美国-物价水平-美国零售销售月率报告
"macro_usa_import_price" # 金十数据中心-经济指标-美国-物价水平-美国进口物价指数报告
"macro_usa_export_price" # 金十数据中心-经济指标-美国-物价水平-美国出口价格指数报告
"macro_usa_lmci" # 金十数据中心-经济指标-美国-劳动力市场-LMCI
"macro_usa_unemployment_rate" # 金十数据中心-经济指标-美国-劳动力市场-失业率-美国失业率报告
"macro_usa_job_cuts" # 金十数据中心-经济指标-美国-劳动力市场-失业率-美国挑战者企业裁员人数报告
"macro_usa_non_farm" # 金十数据中心-经济指标-美国-劳动力市场-就业人口-美国非农就业人数报告
"macro_usa_adp_employment" # 金十数据中心-经济指标-美国-劳动力市场-就业人口-美国 ADP 就业人数报告
"macro_usa_core_pce_price" # 金十数据中心-经济指标-美国-劳动力市场-消费者收入与支出-美国核心 PCE 物价指数年率报告
"macro_usa_real_consumer_spending" # 金十数据中心-经济指标-美国-劳动力市场-消费者收入与支出-美国实际个人消费支出季率初值报告
"macro_usa_trade_balance" # 金十数据中心-经济指标-美国-贸易状况-美国贸易帐报告
"macro_usa_current_account" # 金十数据中心-经济指标-美国-贸易状况-美国经常帐报告
"macro_usa_rig_count" # 金十数据中心-经济指标-美国-产业指标-制造业-贝克休斯钻井报告

# 金十数据中心-经济指标-美国-产业指标-制造业-美国个人支出月率报告

"macro_usa_ppi" # 金十数据中心-经济指标-美国-产业指标-制造业-美国生产者物价指数(PPI)报告
"macro_usa_core_ppi" # 金十数据中心-经济指标-美国-产业指标-制造业-美国核心生产者物价指数(PPI)报告
"macro_usa_api_crude_stock" # 金十数据中心-经济指标-美国-产业指标-制造业-美国 API 原油库存报告
"macro_usa_pmi" # 金十数据中心-经济指标-美国-产业指标-制造业-美国 Markit 制造业 PMI 初值报告
"macro_usa_ism_pmi" # 金十数据中心-经济指标-美国-产业指标-制造业-美国 ISM 制造业 PMI 报告
"macro_usa_nahb_house_market_index" # 金十数据中心-经济指标-美国-产业指标-房地产-美国 NAHB 房产市场指数报告
"macro_usa_house_starts" # 金十数据中心-经济指标-美国-产业指标-房地产-美国新屋开工总数年化报告
"macro_usa_new_home_sales" # 金十数据中心-经济指标-美国-产业指标-房地产-美国新屋销售总数年化报告
"macro_usa_building_permits" # 金十数据中心-经济指标-美国-产业指标-房地产-美国营建许可总数报告
"macro_usa_exist_home_sales" # 金十数据中心-经济指标-美国-产业指标-房地产-美国成屋销售总数年化报告
"macro_usa_house_price_index" # 金十数据中心-经济指标-美国-产业指标-房地产-美国 FHFA 房价指数月率报告
"macro_usa_spcs20" # 金十数据中心-经济指标-美国-产业指标-房地产-美国 S&P/CS20 座大城市房价指数年率报告
"macro_usa_pending_home_sales" # 金十数据中心-经济指标-美国-产业指标-房地产-美国成屋签约销售指数月率报告
"macro_usa_cb_consumer_confidence" # 金十数据中心-经济指标-美国-领先指标-美国谘商会消费者信心指数报告
"macro_usa_nfib_small_business" # 金十数据中心-经济指标-美国-领先指标-美国 NFIB 小型企业信心指数报告
"macro_usa_michigan_consumer_sentiment" # 金十数据中心-经济指标-美国-领先指标-美国密歇根大学消费者信心指数初值报告
"macro_usa_eia_crude_rate" # 金十数据中心-经济指标-美国-其他-美国 EIA 原油库存报告
"macro_usa_initial_jobless" # 金十数据中心-经济指标-美国-其他-美国初请失业金人数报告
"macro_usa_crude_inner" # 金十数据中心-经济指标-美国-其他-美国原油产量报告

# 宏观数据

"macro_cons_gold_volume" # 全球最大黄金 ETF—SPDR Gold Trust 持仓报告
"macro_cons_gold_change" # 全球最大黄金 ETF—SPDR Gold Trust 持仓报告
"macro_cons_gold_amount" # 全球最大黄金 ETF—SPDR Gold Trust 持仓报告
"macro_cons_silver_volume" # 全球最大白银 ETF--iShares Silver Trust 持仓报告
"macro_cons_silver_change" # 全球最大白银 ETF--iShares Silver Trust 持仓报告
"macro_cons_silver_amount" # 全球最大白银 ETF--iShares Silver Trust 持仓报告

# 债券-沪深债券

"bond_zh_hs_daily" # 债券-沪深债券-历史行情数据
"bond_zh_hs_spot" # 债券-沪深债券-实时行情数据

# 债券-沪深可转债

"bond_zh_hs_cov_daily" # 债券-沪深可转债-历史行情数据
"bond_zh_hs_cov_spot" # 债券-沪深可转债-实时行情数据
"bond_zh_cov" # 债券-可转债数据一览表
"bond_cov_comparison" # 债券-可转债数据比价
"bond_cb_jsl" # 可转债实时数据-集思录
"bond_cb_adj_logs_jsl" # 可转债转股价变动-集思录
"bond_cb_index_jsl" # 可转债-集思录可转债等权指数
"bond_cb_redeem_jsl" # 可转债-集思录可转债-强赎

# 货币

"currency_latest" # 最新货币报价
"currency_history" # 指定历史日期的所有货币报价
"currency_time_series" # 指定日期间的时间序列数据-需要权限
"currency_currencies" # 查询所支持的货币信息
"currency_convert" # 货币换算
"currency_pair_map" # 指定货币的所有可货币对的数据

# 沪深港通

"stock_hk_ggt_components_em" # 港股通成份股
"stock_hsgt_hold_stock_em" # 沪深港通持股-个股排行
"stock_hsgt_stock_statistics_em" # 沪深港通持股-每日个股统计
"stock_hsgt_institution_statistics_em" # 沪深港通持股-每日机构统计
"stock_hsgt_hist_em" # 沪深港通历史数据
"stock_hsgt_board_rank_em" # 板块排行
"stock_hsgt_fund_flow_summary_em" # 沪深港通资金流向

# 中国油价

"energy_oil_hist" # 汽柴油历史调价信息
"energy_oil_detail" # 地区油价

# 年报季报

"stock_yjyg_em" # 上市公司业绩预告
"stock_yysj_em" # 上市公司预约披露时间

# 高频数据-标普 500 指数

"hf_sp_500" # 标普 500 指数的分钟数据

# 商品期货库存数据

"futures_inventory_em" # 库存数据-东方财富

# 股票基本面数据

"stock_financial_abstract" # 财务摘要
"stock_financial_report_sina" # 三大财务报表
"stock_financial_analysis_indicator" # 财务指标
"stock_add_stock" # 股票增发
"stock_ipo_info" # 股票新股
"stock_history_dividend_detail" # 分红配股
"stock_history_dividend" # 历史分红
"stock_dividend_cninfo" # 个股历史分红

# 股票板块

"stock_sector_spot" # 板块行情
"stock_sector_detail" # 板块详情(具体股票)

# 股票信息

"stock_info_sz_name_code" # 深证证券交易所股票代码和简称
"stock_info_sh_name_code" # 上海证券交易所股票代码和简称
"stock_info_bj_name_code" # 北京证券交易所股票代码和简称
"stock_info_sh_delist" # 上海证券交易所暂停和终止上市
"stock_info_sz_delist" # 深证证券交易所暂停和终止上市
"stock_info_sz_change_name" # 深证证券交易所名称变更
"stock_info_change_name" # A 股股票曾用名列表
"stock_info_a_code_name" # A 股股票代码和简称

# A 股市盈率和市净率

"stock_market_pe_lg" # 乐咕乐股-主板市盈率
"stock_index_pe_lg" # 乐咕乐股-指数市盈率
"stock_market_pb_lg" # 乐咕乐股-主板市净率
"stock_index_pb_lg" # 乐咕乐股-指数市净率
"stock_hk_indicator_eniu" # 港股股个股市盈率、市净率和股息率指标
"stock_a_high_low_statistics" # 创新高和新低的股票数量
"stock_a_below_net_asset_statistics" # 破净股统计

# 中证指数

"stock_zh_index_hist_csindex" # 中证指数
"stock_zh_index_value_csindex" # 中证指数-指数估值

# 工业增加值增长

"macro_china_gyzjz" # 工业增加值增长

# 存款准备金率

"macro_china_reserve_requirement_ratio" # 存款准备金率

# 社会消费品零售总额

"macro_china_consumer_goods_retail" # 社会消费品零售总额

# 海关进出口增减情况

"macro_china_hgjck" # 海关进出口增减情况

# 全社会用电分类情况表

"macro_china_society_electricity" # 全社会用电分类情况表

# 全社会客货运输量

"macro_china_society_traffic_volume" # 全社会客货运输量

# 邮电业务基本情况

"macro_china_postal_telecommunicational" # 邮电业务基本情况

# 国际旅游外汇收入构成

"macro_china_international_tourism_fx" # 国际旅游外汇收入构成

# 民航客座率及载运率

"macro_china_passenger_load_factor" # 民航客座率及载运率

# 航贸运价指数

"macro_china_freight_index" # 航贸运价指数

# 央行货币当局资产负债

"macro_china_central_bank_balance" # 央行货币当局资产负债

# FR007 利率互换曲线历史数据

"macro_china_swap_rate" # FR007 利率互换曲线历史数据

# 收盘收益率曲线历史数据

"bond_china_close_return" # 收盘收益率曲线历史数据

# 保险业经营情况

"macro_china_insurance" # 保险业经营情况

# 货币供应量

"macro_china_supply_of_money" # 货币供应量

# 央行黄金和外汇储备

"macro_china_foreign_exchange_gold" # 央行黄金和外汇储备

# 商品零售价格指数

"macro_china_retail_price_index" # 商品零售价格指数

# 国房景气指数

"macro_china_real_estate" # 国房景气指数

# 大宗交易

"stock_dzjy_sctj" # 大宗交易-市场统计
"stock_dzjy_mrmx" # 大宗交易-每日明细
"stock_dzjy_mrtj" # 大宗交易-每日统计
"stock_dzjy_hygtj" # 大宗交易-活跃 A 股统计
"stock_dzjy_yybph" # 大宗交易-营业部排行
"stock_dzjy_hyyybtj" # 大宗交易-活跃营业部统计
"stock_dzjy_yybph" # 大宗交易-营业部排行

# 中国货币供应量

"macro_china_money_supply" # 中国货币供应量

# 融资融券

"stock_margin_sse" # 上海证券交易所-融资融券汇总
"stock_margin_detail_sse" # 上海证券交易所-融资融券详情

# 中美国债收益率

"bond_zh_us_rate" # 中美国债收益率

# 分红配送

"stock_fhps_em" # 分红配送

# 三大表报

"stock_zcfz_em" # 三大表报-资产负债表
"stock_zcfz_bj_em" # 三大表报-资产负债表-北交所
"stock_lrb_em" # 三大表报-利润表
"stock_xjll_em" # 三大表报-现金流量表

# 首发企业申报

"stock_ipo_declare_em" # 首发企业申报

# 行业板块

"stock_board_industry_index_ths" # 同花顺-行业板块-指数日频数据

# 概念板块

"stock_board_concept_index_ths" # 同花顺-概念板块-指数日频数据

# 汽车销量

"car_sale_rank_gasgoo" # 盖世汽车-汽车行业制造企业数据库-销量数据
"car_market_total_cpca" # 乘联会-统计数据-总体市场
"car_market_man_rank_cpca" # 乘联会-统计数据-厂商排名
"car_market_cate_cpca" # 乘联会-统计数据-车型大类
"car_market_country_cpca" # 乘联会-统计数据-国别细分市场
"car_market_segment_cpca" # 乘联会-统计数据-级别细分市场
"car_market_fuel_cpca" # 乘联会-统计数据-新能源细分市场

# 增发

"stock_qbzf_em" # 增发

# 配股

"stock_pg_em" # 配股

# 中行人民币牌价历史数据查询

"currency_boc_sina" # 中行人民币牌价历史数据查询

# 港股财报

"stock_financial_hk_report_em" # 东方财富-港股-财务报表-三大报表
"stock_financial_hk_analysis_indicator_em" # 东方财富-港股-财务分析-主要指标

# 债券报表-债券发行-国债发行

"bond_treasure_issue_cninfo" # 债券报表-债券发行-国债发行

# 债券报表-债券发行-地方债发行

"bond_local_government_issue_cninfo" # 债券报表-债券发行-地方债

# 债券报表-债券发行-企业债发行

"bond_corporate_issue_cninfo" # 债券报表-债券发行-企业债

# 债券报表-债券发行-可转债发行

"bond_cov_issue_cninfo" # 债券报表-债券发行-可转债发行

# 债券报表-债券发行-可转债转股

"bond_cov_stock_issue_cninfo" # 债券报表-债券发行-可转债转股

# 上海黄金交易所

"spot_hist_sge" # 上海黄金交易所-历史行情走势
"spot_quotations_sge" # 上海黄金交易所-实时行情走势
"spot_golden_benchmark_sge" # 上海金基准价
"spot_silver_benchmark_sge" # 上海银基准价

# 指数历史数据

"index_zh_a_hist" # 中国股票指数历史数据

# 指数分时数据

"index_zh_a_hist_min_em" # 中国股票指数-指数分时数据

# 中国宏观

"macro_china_insurance_income" # 原保险保费收入
"macro_china_mobile_number" # 手机出货量
"macro_china_vegetable_basket" # 菜篮子产品批发价格指数
"macro_china_agricultural_product" # 农产品批发价格总指数
"macro_china_agricultural_index" # 农副指数
"macro_china_energy_index" # 能源指数
"macro_china_commodity_price_index" # 大宗商品价格
"macro_global_sox_index" # 费城半导体指数
"macro_china_yw_electronic_index" # 义乌小商品指数-电子元器件
"macro_china_construction_index" # 建材指数
"macro_china_construction_price_index" # 建材价格指数
"macro_china_lpi_index" # 物流景气指数
"macro_china_bdti_index" # 原油运输指数
"macro_china_bsi_index" # 超灵便型船运价指数

# 50ETF 期权波动率指数

"index_option_50etf_qvix" # 50ETF 期权波动率指数

# 50ETF 期权波动率指数 QVIX-分时

"index_option_50etf_min_qvix" # 50ETF 期权波动率指数 QVIX-分时

# 300 ETF 期权波动率指数

"index_option_300etf_qvix" # 300 ETF 期权波动率指数

# 300 ETF 期权波动率指数 QVIX-分时

"index_option_300etf_min_qvix" # 300 ETF 期权波动率指数 QVIX-分时

# 500 ETF 期权波动率指数

"index_option_500etf_qvix" # 500 ETF 期权波动率指数

# 500 ETF 期权波动率指数 QVIX-分时

"index_option_500etf_min_qvix" # 500 ETF 期权波动率指数 QVIX-分时

# 创业板 期权波动率指数

"index_option_cyb_qvix" # 创业板 期权波动率指数

# 创业板 期权波动率指数 QVIX-分时

"index_option_cyb_min_qvix" # 创业板 期权波动率指数 QVIX-分时

# 科创板 期权波动率指数

"index_option_kcb_qvix" # 科创板 期权波动率指数

# 科创板 期权波动率指数 QVIX-分时

"index_option_kcb_min_qvix" # 科创板 期权波动率指数 QVIX-分时

# 深证 100ETF 期权波动率指数

"index_option_100etf_qvix" # 深证 100ETF 期权波动率指数

# 深证 100ETF 期权波动率指数 QVIX-分时

"index_option_100etf_min_qvix" # 深证 100ETF 期权波动率指数 QVIX-分时

# 中证 300 股指 期权波动率指数

"index_option_300index_qvix" # 中证 300 股指 期权波动率指数

# 中证 300 股指 期权波动率指数 QVIX-分时

"index_option_300index_min_qvix" # 中证 300 股指 期权波动率指数 QVIX-分时

# 中证 1000 股指 期权波动率指数

"index_option_1000index_qvix" # 中证 1000 股指 期权波动率指数

# 中证 1000 股指 期权波动率指数 QVIX-分时

"index_option_1000index_min_qvix" # 中证 1000 股指 期权波动率指数 QVIX-分时

# 上证 50 股指 期权波动率指数

"index_option_50index_qvix" # 上证 50 股指 期权波动率指数

# 上证 50 股指 期权波动率指数 QVIX-分时

"index_option_50index_min_qvix" # 上证 50 股指 期权波动率指数 QVIX-分时

# 申万指数实时行情

"index_realtime_sw" # 申万指数实时行情

# 申万指数历史行情

"index_hist_sw" # 申万指数历史行情

# 申万宏源研究-行业分类-全部行业分类

"stock_industry_clf_hist_sw" # 申万宏源研究-行业分类-全部行业分类

# 申万指数分时行情

"index_min_sw" # 申万指数分时行情

# 申万指数成分股

"index_component_sw" # 申万指数成分股

# 申万宏源研究-指数分析

"index_analysis_daily_sw" # 申万宏源研究-指数分析-日报表
"index_analysis_weekly_sw" # 申万宏源研究-指数分析-周报表
"index_analysis_monthly_sw" # 申万宏源研究-指数分析-月报表
"index_analysis_week_month_sw" # 申万宏源研究-指数分析-周/月-日期序列
"index_realtime_fund_sw" # 申万宏源研究-申万指数-指数发布-基金指数-实时行情
"index_hist_fund_sw" # 申万宏源研究-申万指数-指数发布-基金指数-历史行情

# 统计局接口

"macro_china_nbs_nation" # 国家统计局全国数据通用接口
"macro_china_nbs_region" # 国家统计局地区数据通用接口

# 数库-A 股新闻情绪指数

"index_news_sentiment_scope" # 数库-A 股新闻情绪指数

# 同花顺-数据中心-宏观数据-新增人民币贷款

"macro_rmb_loan" # 同花顺-数据中心-宏观数据-新增人民币贷款

# 同花顺-数据中心-宏观数据-人民币存款余额

"macro_rmb_deposit" # 同花顺-数据中心-宏观数据-人民币存款余额

# QDII

"qdii_e_index_jsl" # 集思录-T+0 QDII-欧美市场-欧美指数
"qdii_e_comm_jsl" # 集思录-T+0 QDII-欧美市场-商品
"qdii_a_index_jsl" # 集思录-T+0 QDII-亚洲市场-亚洲指数

# 美股财报

"stock_financial_us_report_em" # 东方财富-美股-财务报表-三大报表
"stock_financial_us_analysis_indicator_em" # 东方财富-美股-财务分析-主要指标

# 东方财富网-行情中心-外汇市场-所有汇率

"forex_spot_em" # 东方财富网-行情中心-外汇市场-所有汇率-实时行情数据
"forex_hist_em" # 东方财富网-行情中心-外汇市场-所有汇率-历史行情数据

# 东方财富网-行情中心-全球指数

"index_global_spot_em" # 东方财富网-行情中心-全球指数-实时行情数据
"index_global_hist_em" # 东方财富网-行情中心-全球指数-历史行情数据

# 新浪财经-行情中心-环球市场

"index_global_name_table" # 新浪财经-行情中心-环球市场-名称代码映射表
"index_global_hist_em" # 新浪财经-行情中心-环球市场-历史行情

# 股本结构

"stock_zh_a_gbjg_em" # 股本结构

# 质押式回购

"bond_sh_buy_back_em" # 上证质押式回购
"bond_sz_buy_back_em" # 深证质押式回购
"bond_buy_back_hist_em" # 质押式回购-历史数据

# 中证指数网站-指数列表

"index_csindex_all" # 中证指数网站-指数列表

# 中国外汇交易中心暨全国银行间同业拆借中心-基准-外汇市场-外汇掉期曲线-外汇掉漆 C-Swap 定盘曲线

"fx_c_swap_cm" # 中国外汇交易中心暨全国银行间同业拆借中心-基准-外汇市场-外汇掉期曲线-外汇掉漆 C-Swap 定盘曲线

# 股票期权

"option_current_day_szse" # 深圳证券交易所-期权子网-行情数据-当日合约
"option_current_day_sse" # 上海证券交易所-产品-股票期权-信息披露-当日合约

# 期权合约信息

"option_contract_info_ctp" # 期权合约信息
