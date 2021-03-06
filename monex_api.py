# lib
import datetime
from io import StringIO, BytesIO
import log
import logging
from lxml import html
import math
import pandas as pd
from pytz import timezone
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import time
import unittest
import urllib

logger = log.logger

# my lib
sys.path.append("./monex_onestock")
sys.path.append("./stock_strategy")

from monex_onestock import calculate_profit_rate, recode_stock_portfolio, holiday
from parse_monex_info_table import parse_monex_info_table
import setting
from stock_strategy import move_average

mf = recode_stock_portfolio.management_portfolio(recode_save_path=recode_portfolio_save_path)
monex_onestock_path = setting.monex_onestock_path
recode_portfolio_save_path = setting.recode_portfolio_save_path

class monex_api(unittest.TestCase):
    def setUp(self, pass_wd, Id):
        print("setup")
		#pwdでカレントディレクトリを確認。
		#カレントディレクトリの場所をそのまま記述。
		#seleniumを実行するファイルとChromedriverを同じ場所に格納が楽。
        self.driver = setting.driver
        self.driver.maximize_window()
        self.pass_wd = pass_wd
        self.Id = Id
        self.driver_kind = setting.driver_kind

    def login_monex(self):
        print("login")
        driver = self.driver
        #URL
        #driverの中にはサイトの構造がHTMLとして格納されている。
        driver.get("https://www.monex.co.jp/")

        #login するためには
            # ＊ログイン画面に移動
            # ＊IDを入力
            # ＊パスワードを入力
            # ＊ログインボタンを押す

        # ログイン画面に移動
        if self.driver_kind == "phantomJS":
            btn_login = driver.find_element_by_xpath('//*[@id="hd_nav"]/tbody/tr/td[3]/a')
        elif self.driver_kind == "chrome":
            btn_login = driver.find_element_by_class_name("btn_login")
        btn_login.click()

        # ログインIDを入力
        loginid = driver.find_element_by_id("loginid")
        loginid.send_keys(self.Id)

        # パスワードを入力
        passwd = driver.find_element_by_id("passwd")
        passwd.send_keys(self.pass_wd, Keys.RETURN)

        self.driver = driver

    def buy(self, code, buy_num, debug=False):
        print("buy, {}".format(code))
        driver = self.driver

        stock_trade = driver.find_element_by_class_name("side")
        stock_trade.click()

        if self.driver_kind == "phantomJS":
            code_inputer = driver.find_element_by_xpath('//*[@id="txt_order-buy"]')
        elif self.driver_kind == "chrome":
            code_inputer = driver.find_element_by_id("focuson")
        code_inputer.send_keys(str(code), Keys.RETURN)

        one_stock = driver.find_element_by_xpath('//*[@id="form01"]/div[3]/ul/li[4]/a')
        one_stock.click()

        buy_num_inputer = driver.find_element_by_id("orderNominal")
        buy_num_inputer.send_keys(str(buy_num), Keys.RETURN)

        if debug:
            print("debug buy")
        else:
            excute = driver.find_element_by_xpath('//*[@id="gn_service-lm_hakabu"]/div[7]/div/form/div[2]/div[1]/div[2]/p[2]/input')
            excute.click()

        return

    def sell(self, code, sell_num, debug=False):
        print("sell, {}".format(code))
        driver = self.driver

        if self.driver_kind == "phantomJS":
            try:
                stock_trade = driver.find_element_by_xpath('//*[@id="product_nav"]/ul/li[1]/a')
            except:
                stock_trade = driver.find_element_by_class_name("side")

        elif self.driver_kind == "chrome":
            stock_trade = driver.find_element_by_class_name("side")
        stock_trade.click()

        if self.driver_kind == "phantomJS":
            view_sell_list_btn = driver.find_element_by_xpath('//*[@id="gn_service-"]/div[6]/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/dl[2]/dd/a')
        elif self.driver_kind == "chrome":
            view_sell_list_btn = driver.find_element_by_xpath('//*[@id="gn_service-"]/div[6]/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/dl[2]/dd/a')
        view_sell_list_btn.click()

        page_source = driver.page_source
        doc = lxml.html.parse(StringIO(page_source))

        tables = doc.xpath('//*[@id="gn_custAsset-lm_custAsset"]/div[7]/div/form[1]/table[2]')
        table = tables[0]
        print(lxml.etree.tostring(table, method='html', pretty_print=True))

        table_df = pd.read_html(lxml.etree.tostring(table, method='html', pretty_print=True), header=0)
        table_df = table_df[0]

        parse_monex_info_table(table_df)
        raise("creaet parser monex info table")

        code_list = table_df.ix[:, "銘柄"].tolist()
        code_list = [re.search(r" [0-9][0-9][0-9][0-9] ", c).group(0)[1:-1] for c in code_list]
        print(code_list)


        last_day_close_list = table_df.ix[:, "現在値前日終値前日比"].tolist()
        print(last_day_close_list)
        last_day_close_list_tmp = []
        for value in last_day_close_list:
            if "-" in value:
                value = value.replace("－", "").replace(" ", "").replace(",", "")
            else:
                values = value.split(" ")
                value_len = len(values[0])
                if value_len % 2 == 0:
                    now_value = values[0][:value_len/2]
                    last_value = values[0][value_len/2:]
                else:
                    now_value = values[0][math.floor(value_len):]
                    last_value = values[0][:math.floor(value_len)]

        last_day_close_list = [value.replace("－", "").replace(" ", "").replace(",", "") for value in last_day_close_list]
        print(last_day_close_list)

        average_acquisition_cost_list = None
        possession_list = None

        ordering_list = None

        market_valuation_list = None

        valuation_loss_list = None

        valuation_loss_rate_list = None

        print(table_df)

        raise("i am looking table data")

        hold_num = table_df.ix[(table_df.ix[:, "銘柄"].str.contains(str(code))), "保有数発注数"].values[0]
        hold_num = hold_num.split("  ")
        if hold_num[0] == hold_num[1]:
            print("i can`t sell this stock")
            return
        else:
            print("i can sell this stock")

        for i in table_df.index:
            print("== {} ==".format(table_df.ix[i, "銘柄"]))
            if str(code) in table_df.ix[i, "銘柄"]:
                print(True)
                sell_num = i
            else:
                print(False)
        sell_btn_ByCode_xpath = '//*[@id="gn_custAsset-lm_custAsset"]/div[7]/div/form[1]/table[2]/tbody/tr['+str(sell_num+2)+']/td[8]/a[2]'
        sell_bnt_ByCode = driver.find_element_by_xpath(sell_btn_ByCode_xpath)
        location = sell_bnt_ByCode.location["y"] - 100
        driver.execute_script("window.scrollTo(0, %d);" %location)
        sell_bnt_ByCode.click()

        sell_btn = driver.find_element_by_xpath('//*[@id="gn_service-lm_hakabu"]/div[7]/div/form/div[2]/div[1]/div[2]/p[2]/input')
        sell_btn.click()

        if debug:
            print("debug sell")
        else:
            sell_Execution_btn = driver.find_element_by_xpath('//*[@id="gn_stock-sm_sell"]/div[7]/div/form/div/div[1]/div[2]/p[2]/input')
            sell_Execution_btn.click()

        return

    def tearDown(self):
        self.driver.close()

    @staticmethod
    def time_sleep(sleep_time=20):
        time.sleep(sleep_time)
        return

def main(ps_wd, Id, BuySell=None, debug=False):
    # auto
    if BuySell == "auto":
        BuySell = "buysell"
        try:
            utc_now = datetime.datetime.now(timezone('UTC'))
            jst_now = utc_now.astimezone(timezone('Asia/Tokyo'))
            search_day = jst_now + datetime.timedelta(days=1)

            weekday = search_day.weekday()
            # mon: 0, tue: 1, wed: 2, thu: 3, fri: 4, sat: 5, sun: 6
            search_day_str = str(search_day.date())
            print("{} is {}".format(search_day, weekday))

            if holiday.holiday_check(search_day_str) or weekday in [5, 6]:
                Holiday_Flag = True
                raise Exception("{} is holiday".format(search_day_str))

            else:
                Holiday_Flag = False

        except Exception as e:
            logger.error("fail to compute holiday :::{}".format(e))
            logger.exception("fail to compute holiday :::{}".format(e))
            raise
        else:
            logger.info("success to compute holiday, {} is not holiday".format(search_day_str))

    try: # seting
        monex = monex_api()
        monex.setUp(ps_wd, Id)
    except Exception as e:
        logger.error("fail to set up monex api :::{}".format(e))
        logger.exception("fail to set up monex api :::{}".format(e))
        raise
    else:
        logger.info("success to set up monex api")

    try: # login
        monex.login_monex()
    except Exception as e:
        logger.error("fail to login monex page :::{}".format(e))
        logger.exception("fail to login monex page :::{}".format(e))
        raise
    else:
        logger.info("success to login monex page")

    # searching buy code or sell code
    if BuySell in ["buy", "buysell"]:
        try:
            flag_calculate_profit_rate = False
            flag_move_average = True

            if flag_calculate_profit_rate:
                buy_code_result_data = calculate_profit_rate.calculate_profit_rate(rate="profit_rate")
                buy_code = buy_code_result_data.index[0]

                buy_profit = buy_code_result_data.loc[buy_code]["profit"]
                buy_profit_rate = buy_code_result_data.loc[buy_code]["profit_rate"]
                if buy_profit_rate == 0:
                    raise Exception("buy profit rate is 0")

            elif flag_move_average:
                window = 75 # 移動平均の期間（日）
                ma = move_average.move_average(value_type="Close", window=window)
                buy_code = ma.buy_codes()
                buy_profit = "Nan"
                buy_profit_rate = "Nan"

        except Exception as e:
            logger.error("fail to calculate buy stock code :::{}".format(e))
            logger.exception("fail to calculate buy stock code :::{}".format(e))
            raise(e)
        else:
            logger.info("success to calculate buy stock code")

    if BuySell in ["sell", "buysell"]:
        try:
            sell_code = mf.sell_possible_code()
        except Exception as e:
            logger.error("fail to calculate sell stock code :::{}".format(e))
            logger.exception("fail to calculate sell stock code :::{}".format(e))
            sell_code = None
        else:
            logger.info("success to calculate sell stock code")

    # action buy or sell and record result
    try:
        if BuySell == "buy":
            try:
                monex.buy(str(buy_code), 1, debug=debug)
                mf.recode_stock_portfolio("buy", str(buy_code), 1, profit=buy_profit, profit_rate=buy_profit_rate)
            except Exception as e:
                logger.error("fail to excute buy action :::{}".format(e))
                logger.exception("fail to excute buy action :::{}".format(e))

                raise(e)
            else:
                logger.info("success to excute buy action")

        elif BuySell == "sell":
            try:
                if sell_code == None:
                    raise("not error, but sell_code is None")

                monex.sell(str(sell_code), 1, debug=debug)
                mf.recode_stock_portfolio("sell", str(sell_code), 1)
            except Exception as e:
                logger.error("fail to excute sell action :::{}".format(e))
                logger.exception("fail to excute sell action :::{}".format(e))
                with open("selenium_error.html", "w") as f:
                    f.write(monex.driver.page_source)
                monex.driver.set_window_size(1024, 768)
                monex.driver.save_screenshot('selenium_error.png')
                raise(e)

            else:
                logger.info("success to excute sell action")

        elif BuySell == "result":
            print("result data")
            print(buy_code_result_data)

        elif BuySell == "buysell":
            # sell
            try:
                if sell_code == None:
                    raise("not error, but sell_code is None")

                monex.sell(str(sell_code), 1, debug=debug)
                mf.recode_stock_portfolio("sell", str(sell_code), 1)
            except Exception as e:
                logger.error("fail to excute sell(BuySell) action :::{}".format(e))
                logger.exception("fail to excute sell(BuySell) action :::{}".format(e))
            else:
                logger.info("success to excute sell(BuySell) action")

            #buy
            try:
                monex.buy(str(buy_code), 1, debug=debug)
                mf.recode_stock_portfolio("buy", str(buy_code), 1, profit=buy_profit, profit_rate=buy_profit_rate)
            except Exception as e:
                logger.error("fail to excute buy(BuySell) action :::{}".format(e))
                logger.exception("fail to excute buy(BuySell) action :::{}".format(e))
            else:
                logger.info("success to excute buy(BuySell) action")

        else:
            raise Exception("{} is invalid. search program process".format(BuySell))

    except Exception as e:
        logger.error("fail to excute action :::{}".format(e))
        logger.exception("fail to excute action :::{}".format(e))
        raise

    else:
        logger.info("success to excute action")

    monex.time_sleep()
    monex.tearDown()

if __name__ == "__main__":
    try:
        argvs = sys.argv
        argc = len(argvs)
        if argc == 5:
            debug = argvs[4]
            if debug == "debug":
                debug = True
            else:
                raise Exception("input error for debug")
        elif argc != 4:
            raise Exception("input error. input argc!=4")
        elif argc == 4:
            debug = False

        ps_wd = argvs[1]
        Id = argvs[2]
        BuySell = argvs[3]
        if BuySell not in ["buy", "sell", "result", "buysell", "auto"]:
            raise Exception("input error. action input")

    except Exception as e:
        logger.error("fail to read argument")
        logger.exception("fail to read argument")
        raise Exception(e)

    else:
        logger.info("success to read argument")

    main(ps_wd, Id, BuySell=BuySell, debug=debug)
