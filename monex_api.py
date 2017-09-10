import unittest
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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
        #excute.click()

    def sell(self):
        pass

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)
    if argc != 3:
        raise Exception("input error")

    ps_wd = argvs[1]
    Id = argvs[2]

    monex = monex_api()
    monex.setUp(ps_wd, Id)

    monex.login_monex()
    monex.buy(1332, 1)
    #monex.tearDown()
