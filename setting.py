from selenium import webdriver

# driver
driver_kind = "phantomJS" # chrome or phantomJS
if driver_kind == "chrome":
    web_driver_path = "/Users/yoneda/github/selenium_api_youtube/chromedriver"
    driver = webdriver.Chrome(web_driver_path)
elif driver_kind == "phantomJS":
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    des_cap = dict(DesiredCapabilities.PHANTOMJS)
    des_cap['phantomjs.page.settings.userAgent'] = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36'
    )
    driver = webdriver.PhantomJS(desired_capabilities=des_cap)
else:
    raise Exception("driver error. check setting driver.")

# path
root_path = "/Users/yoneda/github/selenium_api_youtube/"
log_save_path = root_path + "log"
monex_onestock_path = root_path + "monex_onestock"
recode_portfolio_save_path = root + "recode_portfolio.csv"
