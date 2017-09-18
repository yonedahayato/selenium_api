import unittest
import sys, time, logging
import pandas as pd
import urllib
import lxml.html
from io import StringIO, BytesIO

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

sys.path.append("./monex_onestock")
from monex_onestock import calculate_profit_rate, recode_stock_portfolio
mf = recode_stock_portfolio.management_portfolio()

import log
logger = log.logger

import setting

class monex_api(unittest.TestCase):
    def setUp(self, pass_wd, Id):
        print("setup")
		#pwdでカレントディレクトリを確認。
		#カレントディレクトリの場所をそのまま記述。
		#seleniumを実行するファイルとChromedriverを同じ場所に格納が楽。
        web_driver_path = setting.web_driver_path
        self.driver = webdriver.Chrome(web_driver_path)
        self.driver.maximize_window()
        self.pass_wd = pass_wd
        self.Id = Id

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
        btn_login = driver.find_element_by_class_name("btn_login")
        btn_login.click()

        # ログインIDを入力
        loginid = driver.find_element_by_id("loginid")
        loginid.send_keys(self.Id)

        # パスワードを入力
        passwd = driver.find_element_by_id("passwd")
        passwd.send_keys(self.pass_wd, Keys.RETURN)

    def buy(self, code, buy_num, debug=False):
        print("buy, {}".format(code))
        driver = self.driver

        stock_trade = driver.find_element_by_class_name("side")
        stock_trade.click()

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

        stock_trade = driver.find_element_by_class_name("side")
        stock_trade.click()

        view_sell_list_btn = driver.find_element_by_xpath('//*[@id="gn_service-"]/div[6]/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/dl[2]/dd/a')
        view_sell_list_btn.click()

        page_source = driver.page_source
        doc = lxml.html.parse(StringIO(page_source))

        tables = doc.xpath('//*[@id="gn_custAsset-lm_custAsset"]/div[7]/div/form[1]/table[2]')
        table = tables[0]
        table_df = pd.read_html(lxml.etree.tostring(table, method='html'), header=0)
        table_df = table_df[0]

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
        sell_btn_ByCode_xpath = '//*[@id="gn_custAsset-lm_custAsset"]/div[7]/div/form[1]/table[2]/tbody/tr[3]/td[8]/a[2]'
        #sell_btn_ByCode_xpath = '//*[@id="gnav"]/li[1]/a'
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
    try:
        monex = monex_api()
        monex.setUp(ps_wd, Id)
    except Exception as e:
        logger.error("fail to set up monex api :::{}".format(e))
        logger.exception("fail to set up monex api :::{}".format(e))
        raise
    else:
        logger.info("success to set up monex api")

    try:
        monex.login_monex()
    except Exception as e:
        logger.error("fail to login monex page :::{}".format(e))
        logger.exception("fail to login monex page :::{}".format(e))
        raise
    else:
        logger.info("success to login monex page")

    try:
        if BuySell in ["buy", "buysell"]:
            result_data = calculate_profit_rate.calculate_profit_rate(rate="profit_rate")
            buy_code = result_data.index[0]
    except Exception as e:
        logger.error("fail to calculate buy stock code :::{}".format(e))
        logger.exception("fail to calculate buy stock code :::{}".format(e))
        raise
    else:
        logger.info("success to calculate buy stock code")

    try:
        if BuySell in ["sell", "buysell"]:
            sell_code = mf.sell_possible_code()
    except Exception as e:
        logger.error("fail to calculate sell stock code :::{}".format(e))
        logger.exception("fail to calculate sell stock code :::{}".format(e))
    else:
        logger.info("success to calculate sell stock code")

    try:
        if BuySell == "buy":
            monex.buy(str(buy_code), 1, debug=debug)
            mf.recode_stock_portfolio("buy", str(buy_code), 1)

        elif BuySell == "sell":
            monex.sell(str(sell_code), 1, debug=debug)
            mf.recode_stock_portfolio("sell", str(sell_code), 1)

        elif BuySell == "result":
            print("resultdata")
            print(result_data)

        elif BuySell == "buysell":
            monex.buy(str(buy_code), 1, debug=debug)
            mf.recode_stock_portfolio("buy", str(buy_code), 1)

            monex.sell(str(sell_code), 1, debug=debug)
            mf.recode_stock_portfolio("sell", str(sell_code), 1)

        else:
            raise Exception("input buy or sell")

    except Exception as e:
        logger.error("fail to excute buy or sell :::{}".format(e))
        logger.exception("fail to excute buy or sell :::{}".format(e))
        raise
    else:
        logger.info("success to calculate buy or sell stock code")

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
            raise Exception("input error")
        elif argc == 4:
            debug = False

        ps_wd = argvs[1]
        Id = argvs[2]
        BuySell = argvs[3]

    except Exception as e:
        logger.error("fail to read argument")
        logger.exception("fail to read argument")
        raise Exception
    else:
        logger.info("success to read argument")

    main(ps_wd, Id, BuySell=BuySell, debug=debug)
