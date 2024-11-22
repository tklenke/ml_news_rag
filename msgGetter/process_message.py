#get message text v1
# this program will require that an instance of Chrome has been
# started with a debug port available.  See chrome_with_debug.bat

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from f_filter import elements_to_html, elements_to_markdown, filter_markdown

import os

TODO: Change program to put filtered/processed .txt files in separate directory tree

#---CONSTANTS
NMAX = 12000
IDS_FILE = r'../data/msgids_aug2024.txt'
MESSAGE_DIR = r"../data/msgs"
USE_MSG_SUBDIRS = True
SAVE_RAW_HTML = False
SAVE_FILTERED_MD = True
MIN_PAUSE = 10
LOAD_PAUSE = 2
EXE_PATH = '..\\..\\chromedriver-win64\\chromedriver.exe'
BASE_URL = 'https://groups.google.com/g/cozy_builders/c/'
LLMMODEL = "llama3.2:3b"
EMBEDMODEL = "nomic-embed-text"
EMBED_PREFIX = ""
CHROMAHOST = "chroma-rag"
OLLAMAHOST = "http://ollama-rag:11434"

# Function to scrape a message page
def get_message_elements(id):
    url = BASE_URL + id
    r = []  #return array of elements

    # Navigate to the webpage you want to scrape
    driver.get(url)  
    time.sleep(random.random()*2+LOAD_PAUSE)

    #click the expand all tag
    try:
        element = driver.find_element(By.XPATH, "//div[@data-tooltip='Expand all']")
        element.click()
    except Exception as e:
       print(f"Id {id} no exapansion found")
    #wait a second to load jic
    time.sleep(2)

    elements_title = driver.find_elements(By.XPATH, "//div[@class='ThqSJd']")

    # Find all elements with the 'aria-tag' attribute having the value 'digest'
    elements_digest = driver.find_elements(By.XPATH, "//div[@role='list']")

    #put elements in to result array
    r += elements_title
    r += elements_digest

    return r

#Reads ids from a file into a list, removing trailing carriage returns and linefeeds.
#Args:    filename: The name of the file to read.
#Returns:   A list of strings, each containing a line from the file 
#           with trailing carriage returns and linefeeds removed.
def read_ids_from_file(filename):

  with open(filename, 'r') as f:
    lines = [line.rstrip() for line in f]
  return lines

#Scans a directory and subdirectories for files with a '.md' extension and returns a list of their names without the extension.
#Args:      directory: The directory to scan.
#Returns:   A list of strings containing the names of the '.md' files without the extension.
def get_md_filenames(directory):
    md_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                md_files.append(file[:-3])  # Remove the '.md' extension

    return md_files

def save_text_to_file(id, txt, ext=".txt"):
    filename = id + ext

    if USE_MSG_SUBDIRS:
        if not id[0].isalpha():
            subdir = "aDigits"
        else:
            subdir =  id.upper()[0] 
        filename = os.path.join(MESSAGE_DIR,subdir,filename)
    else:
        filename = os.path.join(MESSAGE_DIR,filename)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding='utf-8') as f:
        f.write(txt)

def process_id(msgid):
    #get raw html chunks and save
    elements = get_message_elements(msgid)
    msghtml = elements_to_html(elements)
    if SAVE_RAW_HTML:
        save_text_to_file(msgid,msghtml,".htm")
    #filter html if necessary

    #convert to markdown and save
    msgtxt = elements_to_markdown(elements)
    # add link to original message in first line
    msgtxt = f"[Original Message ID:{msgid}]({BASE_URL + msgid})\n" + msgtxt
    save_text_to_file(msgid,msgtxt,".md")

    #filter markdown for embedding and save
    embedtxt = filter_markdown(msgtxt)
    if SAVE_FILTERED_MD:
        save_text_to_file(msgid,embedtxt,".txt")

    # embed text in chromadb

    #process to categorize, extract keywords, and products, result in json
        #check json and reprocess
    


######################
##  MAIN
######################

#set up some stats
nTotalSavedThisSession = 0
tTotal = 0

#connect chromedriver
service = Service(executable_path=EXE_PATH)
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)

# get the full list of message ids
ids = read_ids_from_file(IDS_FILE)
print(f"Ids: {len(ids)}")

# get list of message ids that have been saved
ids_saved = get_md_filenames(MESSAGE_DIR)
print(f"Msgs saved: {len(ids_saved)}")

#remove the ids that have been saved from the ids
ids[:] = [x for x in ids if x not in ids_saved]
print(f"Net to complete: {len(ids)}")

# loop on the following
#   select a random message id and check that it has not been saved
#       if has been processed, remove from list and select another 
#           (NR - cleaned list above)
#       if the list is empty we are done (see while conditional)
#   get the message text and save it
#       remove from the list and select another
#   print out some stats

while (len(ids) > 0) & (nTotalSavedThisSession < NMAX):
    random_index = random.randint(0, len(ids) - 1)
    random_id = ids.pop(random_index)
    t0 = time.time()

    print(f"fetching id: {random_id}")
    process_id(random_id)

    # wait enough time
    t1 = time.time() - t0
    tTotal += t1
    if t1 < MIN_PAUSE:
        time.sleep(random.random()*MIN_PAUSE/(t1+1))

    # stats
    nTotalSavedThisSession += 1
    if nTotalSavedThisSession % 5 == 0:
       print(f"Progress This session: {nTotalSavedThisSession} To Go: {len(ids)} \
             Average Processing Time: {tTotal/float(nTotalSavedThisSession):.1f}")

# print out some stats
print(f"----STATS-----")
print(f"Msgs Processed: {nTotalSavedThisSession:.1f}")
print(f"Total Processing Time: {tTotal:.1f}")
print(f"Average Processing Time: {tTotal/float(nTotalSavedThisSession):.1f}")

# Close the browser
driver.quit()