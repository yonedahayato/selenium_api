import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class PythonOrgSearch(unittest.TestCase):
    def setUp(self):
		#pwdでカレントディレクトリを確認。
		#カレントディレクトリの場所をそのまま記述。
		#seleniumを実行するファイルとChromedriverを同じ場所に格納が楽。
        self.driver = webdriver.Chrome("/Users/yoneda/github/selenium_api_youtube/chromedriver")

    def test_serch_in_python_org(self):
        driver = self.driver

        #youtubeのURL
        #driverの中にはサイトの構造がHTMLとして格納されている。
        driver.get("https://www.youtube.com/")
        print("driver.get")

        #youtubeの検索バーはid="masthead-search-term"
        #find_element_by_idで検索バーのidを取得してくる
        elem = driver.find_element_by_id("search")

        #yuiと検索
        elem.send_keys("yui", Keys.RETURN)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
    pos = PythonOrgSearch()
    pos.setUp()
    pos.test_serch_in_python_org()
    pos.tearDown()
