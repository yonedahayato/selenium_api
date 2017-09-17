import unittest
import sys, time
import pandas as pd
import urllib
import lxml.html
from io import StringIO, BytesIO

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

sys.path.append("./monex_onestock")
from monex_onestock import calculate_profit_rate


class monex_api(unittest.TestCase):
    def setUp(self, pass_wd, Id):
        print("setup")
		#pwdでカレントディレクトリを確認。
		#カレントディレクトリの場所をそのまま記述。
		#seleniumを実行するファイルとChromedriverを同じ場所に格納が楽。
        self.driver = webdriver.Chrome("/Users/yoneda/github/selenium_api_youtube/chromedriver")
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

    def buy(self, code, buy_num):
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

        #excute = driver.find_element_by_class_name("btn-cmn-move btn-l s-w-210")
        excute = driver.find_element_by_xpath('//*[@id="gn_service-lm_hakabu"]/div[7]/div/form/div[2]/div[1]/div[2]/p[2]/input')
        excute.click()

    def sell(self, code):
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
        for i in table_df.index:
            print("== {} ==".format(table_df.ix[i, "銘柄"]))
            if str(code) in table_df.ix[i, "銘柄"]:
                print(True)
                sell_num = i
            else:
                print(False)
        sell_btn_ByCode_xpath = '//*[@id="gn_custAsset-lm_custAsset"]/div[7]/div/form[1]/table[2]/tbody/tr['+str(sell_num+2)+']/td[8]/a[2]'
        sell_bnt_ByCode = driver.find_element_by_xpath(sell_btn_ByCode_xpath)
        sell_bnt_ByCode.click()

        sell_btn = driver.find_element_by_xpath('//*[@id="gn_service-lm_hakabu"]/div[7]/div/form/div[2]/div[1]/div[2]/p[2]/input')
        sell_btn.click()

        sell_Execution_btn = driver.find_element_by_xpath('//*[@id="gn_stock-sm_sell"]/div[7]/div/form/div/div[1]/div[2]/p[2]/input')
        sell_Execution_btn.click()

    def tearDown(self):
        self.driver.close()

    @staticmethod
    def time_sleep(sleep_time=20):
        time.sleep(sleep_time)
        return

def main(ps_wd, Id, BuySell=None):
    monex = monex_api()
    monex.setUp(ps_wd, Id)

    monex.login_monex()

    #result_data = calculate_profit_rate.calculate_profit_rate(rate="profit_rate")
    #code = result_data.index[0]
    code = 3662

    if BuySell == "buy":
        monex.buy(str(code), 1)
    elif BuySell == "sell":
        monex.sell(str(code))
    elif BuySell == "result":
        print("result data")
        print(result_data)
    else:
        raise Exception("input buy or sell")

    monex.time_sleep()
    monex.tearDown()


if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)
    if argc != 4:
        raise Exception("input error")

    ps_wd = argvs[1]
    Id = argvs[2]
    BuySell = argvs[3]
    main(ps_wd, Id, BuySell=BuySell)
