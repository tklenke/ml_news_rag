#just a test program to make sure Selenium and Chrome are working correctly

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.options import Options

#chrome_options = Options()
#chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

service = Service(executable_path='..//chromedriver-win32//chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)

driver.get('https://groups.google.com/g/cozy_builders');
time.sleep(15) # Let the user actually see something!
#search_box = driver.find_element(By.NAME,'q')
#search_box.send_keys('ChromeDriver')
#search_box.submit()
#time.sleep(15) # Let the user actually see something!
driver.close()