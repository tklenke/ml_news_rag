#just a test program to make sure Selenium and Chrome are working correctly

import time, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.options import Options

#chrome_options = Options()
#chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
exe_path = '/mnt/c/Users/tom/Documents/projects/chromedriver-win64/chromedriver.exe'
cd_dir = '/mnt/c/Users/tom/Documents/projects/chromedriver-win64'
exe_path = '..\\..\\chromedriver-win64\\chromedriver.exe'

if not os.path.isfile(exe_path):
    print(f"Dir: {os.listdir(cd_dir)}")
    print(f"Pwd: {os.getcwd()}")
    print(f"File not found: {exe_path}")
    exit()


service = Service(executable_path=exe_path)
print(f"Service")
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
print(f"Options")
driver = webdriver.Chrome(service=service, options=options)
print(f"Driver")

driver.get('https://groups.google.com/g/cozy_builders')
print(f"Get")
time.sleep(15) # Let the user actually see something!
#search_box = driver.find_element(By.NAME,'q')
#search_box.send_keys('ChromeDriver')
#search_box.submit()
#time.sleep(15) # Let the user actually see something!
driver.close()