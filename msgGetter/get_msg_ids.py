import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

## Set up
startDate = '2024-09-03'
endDate = time.strftime("%Y-%m-%d", time.localtime())
url = 'https://groups.google.com/g/cozy_builders'  # Replace with your desired URL
urlBase = 'https://groups.google.com/g/cozy_builders/search?q=after%3A'
url = urlBase + startDate
output_file = f"msgids_{startDate}_{endDate}.txt"
max_pages = 600
url_prefix = 'https://groups.google.com/g/cozy_builders/c/'
nMaxSequentialDupePages = 10
nMsgIdLen = 11 #length of a google groups message ID

service = Service(executable_path='..//..//chromedriver-win64//chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)


print(f"Start Date: {startDate} to {endDate}")
f = open(output_file, 'w')
print(f"Writing to file: {output_file}")
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
                f.write(href[nLenUrlPrefix:nLenUrlPrefix+nMsgIdLen] + '\n')
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

