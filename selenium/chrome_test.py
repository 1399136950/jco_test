from selenium import webdriver 
options = webdriver.ChromeOptions() 
options.add_argument('lang=zh_CN.UTF-8') 
options.add_argument('user-agent="User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"')
driver = webdriver.Chrome(options = options)
driver.get('https://www.baidu.com/')
print(driver.getPageSource())
driver.quit()
