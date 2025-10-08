import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

## Require elements install
# selenium via pip
# chromedriver for windows see ...
# https://sites.google.com/chromium.org/driver/

## Set up
DESC_KEY = 'cozybuilders'
BASE_URL = 'http://cozybuilders.org/'  # Replace with your desired URL
SKIP_FOLDERS = ['newsletters','mail_list','2004_Western_Trip','2005_Go_West_Trip','2005_Instrument_Training',
                '2005_OSH_Trip','2006_OSH_Trip','2007_Rough_River','logbook']  #don't index these folders
SKIP_EXTENSIONS = ['pdf','doc']  #chunk these extensions but don't look for urls in them
INVALID_EXTENSIONS = ['jpg','mp3','gif','xls','wav','zip','dwg','dxf']  #these files are not to be turned into chunks
MAX_PAGES = 100

service = Service(executable_path='..//..//chromedriver-win64//chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)

output_file = f"../data/{DESC_KEY}.txt"
output_dir = f"../data/{DESC_KEY}/"

#maybe more elegant to do this recursively, but I'm gonna make a full list of all the endpoint
# pages in the website being scraped, then use that list to pull the data from the pages.

f = open(output_file, 'w')
os.makedirs(output_dir, exist_ok=True)

page_count = 0
dPagesScraped = {}
nLenBaseUrl = len(BASE_URL)
url = ""

#scrape site for endpoint pages on this site
while (page_count < MAX_PAGES and url is not None):
    dPagesScraped[url] = True
    url = BASE_URL + url
    print(f"Searching {url}")
    driver.get(url)
    nUrlsThisPage = 0
    
    # Find all elements with the 'href' attribute
    href_tags = driver.find_elements(By.XPATH, "//a[@href]")

    # Write the href values to the text file
    n = 0
    for tag in href_tags:
        href = tag.get_attribute('href')
        if href.startswith(BASE_URL):
            #remove the anchor inside a page if exists
            href = href.split('#', 1)[0]
            if href[nLenBaseUrl:] not in dPagesScraped:
                folder = href[nLenBaseUrl:].split('/', 1)[0]
                if folder not in SKIP_FOLDERS:
                    #skip endpoint pages
                    ext = href[-3:].lower()
                    #skip these extensions
                    if ext not in INVALID_EXTENSIONS:
                        #don't drill into these extentions for urls
                        if  ext in SKIP_EXTENSIONS:
                            dPagesScraped[href[nLenBaseUrl:]] = True
                        else:
                            dPagesScraped[href[nLenBaseUrl:]] = False
            nUrlsThisPage += 1

    page_count=page_count+1
    print(f"Page {page_count} Found {nUrlsThisPage}")
    url = None

    for key, val in dPagesScraped.items():
        if val is False:
            url = key
            break
print(f"Found {len(dPagesScraped.keys())} endpoint urls")
for key in sorted(dPagesScraped.keys()):
    f.write(f"{key}\n")
f.close()

print(f"done")
driver.quit()

