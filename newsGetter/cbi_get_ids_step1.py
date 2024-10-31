import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

## Require elements install
# selenium via pip
# chromedriver for windows see ...
# https://sites.google.com/chromium.org/driver/

## Set up
url = 'https://groups.google.com/g/cozy_builders'  # Replace with your desired URL
output_file = "href_tags1.txt"
max_pages = 600
url_prefix = 'https://groups.google.com/g/cozy_builders/c/'
nMaxSequentialDupePages = 10

service = Service(executable_path='..//..//chromedriver-win64//chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)

f = open(output_file, 'w')
last_href = ''
top_href = ''
nDupePages = 0
nSequentialDupePages = 0
page_count = 0
nTotalIds = 0
nLenUrlPrefix = len(url_prefix)

driver.get(url);
time.sleep(.2) # Let the user actually see something!

while (page_count < max_pages) & (nSequentialDupePages < nMaxSequentialDupePages):

    bTopOfPage = True

    pause_time = random.random()*2

    # Find all elements with the 'href' attribute
    href_tags = driver.find_elements(By.XPATH, "//a[@href]")

    # Write the href values to the text file
    n = 0
    for tag in href_tags:
        href = tag.get_attribute('href')
        if href.startswith(url_prefix):
            if href != last_href:
                if (bTopOfPage):
                    if href == top_href:
                        print(f"Dupe page found at page {page_count} {href}")
                        nDupePages = nDupePages + 1
                        nSequentialDupePages = nSequentialDupePages+1
                        break
                    else:
                        bTopOfPage = False
                        nSequentialDupePages = 0
                        top_href = href
                last_href = href
                f.write(href[nLenUrlPrefix:] + '\n')
                nTotalIds = nTotalIds+1
                n=n+1

    page_count=page_count+1
    print(f"Page {page_count} Wrote {n} DupePages {nDupePages} Pause {pause_time}")

    #goto next page
    element = driver.find_element(By.XPATH, "//div[@data-tooltip='Next page']")
    element.click()
    time.sleep(random.random()*2)

print(f"IDs found {nTotalIds} on {page_count} pages written to {output_file}")
print(f"{nDupePages} duplicate pages {nSequentialDupePages} sequential at end")
driver.quit()

