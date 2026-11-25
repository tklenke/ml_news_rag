# ABOUTME: Fetches the threads of the id files in data from Google Groups and saves each as
# ABOUTME: markdown and as filtered text; a thread with a collapsed post is not saved
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
from f_collapsed import count_collapsed_posts

import os

#TODO: Change program to put filtered/processed .txt files in separate directory tree

#---CONSTANTS
NMAX = 12000
MSG_ID_FILE_DIRECTORY = r'../data' 
MSG_ID_FILE_PREFIX = "msgids_"
MESSAGE_MD_DIR = r"../data/msgs_md"
MESSAGE_HTM_DIR = r"../data/msgs_htm"
MESSAGE_FILTERED_DIR = r"../data/msgs"
USE_MSG_SUBDIRS = True
SAVE_RAW_HTML = False
SAVE_RAW_MD = True
SAVE_FILTERED_MD = True
EXIT_IF_NO_PREVIOUS = True
MIN_PAUSE = 0
LOAD_PAUSE = 1
# Seconds after the "Expand all" click until a thread that still shows a collapsed post is given up
EXPAND_SECONDS = 15
EXE_PATH = '..\\..\\chromedriver-win64\\chromedriver.exe'
BASE_URL = 'https://groups.google.com/g/cozy_builders/c/'
LLMMODEL = "llama3.2:3b"
EMBEDMODEL = "nomic-embed-text"
EMBED_PREFIX = ""
CHROMAHOST = "chroma-rag"
OLLAMAHOST = "http://ollama-rag:11434"

# Function to scrape a message page
# Reads the page again until no post shows collapsed or EXPAND_SECONDS have passed
def get_message_elements(driver, id):
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
    tGiveUp = time.time() + EXPAND_SECONDS
    while True:
        time.sleep(1)

        elements_title = driver.find_elements(By.XPATH, "//div[@class='ThqSJd']")

        # Find all elements with the 'aria-tag' attribute having the value 'digest'
        elements_digest = driver.find_elements(By.XPATH, "//div[@role='list']")

        #put elements in to result array
        r = elements_title + elements_digest

        if not count_collapsed_posts(elements_to_markdown(r)) or time.time() > tGiveUp:
            return r

#Reads ids from a file into a list, removing trailing carriage returns and linefeeds.
#Args:    filename: The name of the file to read.
#Returns:   A list of strings, each containing a line from the file 
#           with trailing carriage returns and linefeeds removed.
def read_ids_from_file(filename):
  print(f"reading ids from {filename}...")
  with open(filename, 'r') as f:
    lines = [line.rstrip() for line in f]
  return lines

def get_msgids_list_files():
    all_entries = os.listdir(MSG_ID_FILE_DIRECTORY)
    file_list = []

    for f in all_entries:
        f_full = os.path.join(MSG_ID_FILE_DIRECTORY, f)
        if f.startswith(MSG_ID_FILE_PREFIX) and os.path.isfile(f_full):
            file_list.append(f_full)
    return file_list


#Scans a directory and subdirectories for files with a '.txt' extension and returns a list of their names without the extension.
#Args:      directory: The directory to scan.
#Returns:   A list of strings containing the names of the '.txt' files without the extension.
def get_txt_filenames(directory):
    md_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                md_files.append(file[:-4])  # Remove the '.txt' extension

    return md_files

def get_filename(dir, id, ext=".txt"):
    filename = id + ext

    if USE_MSG_SUBDIRS:
        if not id[0].isalpha():
            subdir = "aDigits"
        else:
            subdir =  id.upper()[0] 
        filename = os.path.join(dir,subdir,filename)
    else:
        filename = os.path.join(dir,filename)

    return filename

def save_text_to_file(dir, id, txt, ext=".txt"):
    filename = get_filename(dir, id, ext)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding='utf-8') as f:
        f.write(txt)

# Saves a thread only when none of its posts is collapsed: the markdown if it was fetched,
# and the filtered text. Returns whether it was saved.
def save_thread(msgid, msgtxt, fetched):
    nCollapsed = count_collapsed_posts(msgtxt)
    if nCollapsed:
        print(f"Id {msgid} has {nCollapsed} collapsed posts, not saved")
        return False
    if fetched and SAVE_RAW_MD:
        save_text_to_file(MESSAGE_MD_DIR,msgid,msgtxt,".md")

    #filter markdown for embedding and save
    embedtxt = filter_markdown(msgtxt)
    if SAVE_FILTERED_MD:
        save_text_to_file(MESSAGE_FILTERED_DIR,msgid,embedtxt,".txt")
    return True

# Returns whether the thread is saved
def process_id(driver, msgid):
    #look for txt file, if exists done
    txtfile = get_filename(MESSAGE_FILTERED_DIR,msgid,".txt")
    if os.path.exists(txtfile):
        print(f"{txtfile} exists, skipping")
        return True
    #look for md file, if exists read
    mdfile = get_filename(MESSAGE_MD_DIR,msgid,".md")
    if os.path.exists(mdfile):
        print(f"{mdfile} exists, reading")
        with open(mdfile, 'r', encoding='utf-8') as f:
            msgtxt = f.read()
        fetched = False
    else:
        #get raw html chunks and save
        elements = get_message_elements(driver, msgid)
        msghtml = elements_to_html(elements)
        if SAVE_RAW_HTML:
            save_text_to_file(MESSAGE_HTM_DIR,msgid,msghtml,".htm")
        #filter html if necessary

        #convert to markdown and save
        msgtxt = elements_to_markdown(elements)
        # add link to original message in first line
        msgtxt = f"[Original Message ID:{msgid}]({BASE_URL + msgid})\n" + msgtxt
        fetched = True

    return save_thread(msgid, msgtxt, fetched)

    # embed text in chromadb

    #process to categorize, extract keywords, and products, result in json
        #check json and reprocess
    


######################
##  MAIN
######################

def main():
    #set up some stats
    nTotalSavedThisSession = 0
    tTotal = 0
    aIds = []
    aNotSaved = []

    #connect chromedriver
    service = Service(executable_path=EXE_PATH)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=service, options=options)

    # get the full list of message ids
    for idFile in get_msgids_list_files():
        aIds.extend(read_ids_from_file(idFile))
    print(f"Ids: {len(aIds)}")

    # get list of message ids that have been saved
    ids_saved = get_txt_filenames(MESSAGE_FILTERED_DIR)
    print(f"Msgs already filtered: {len(ids_saved)}")

    #remove the ids that have been saved from the ids
    aIds[:] = [x for x in aIds if x not in ids_saved]
    print(f"Net to complete: {len(aIds)}")

    # loop on the following
    #   select a random message id and check that it has not been saved
    #       if has been processed, remove from list and select another 
    #           (NR - cleaned list above)
    #       if the list is empty we are done (see while conditional)
    #   get the message text and save it
    #       remove from the list and select another
    #   print out some stats

    while (len(aIds) > 0) & (nTotalSavedThisSession < NMAX):
        random_index = random.randint(0, len(aIds) - 1)
        random_id = aIds.pop(random_index)
        t0 = time.time()

        print(f"fetching id: {random_id}")
        if not process_id(driver, random_id):
            aNotSaved.append(random_id)

        # wait enough time
        t1 = time.time() - t0
        tTotal += t1
        if t1 < MIN_PAUSE:
            time.sleep(random.random()*MIN_PAUSE/(t1+1))

        # stats
        nTotalSavedThisSession += 1
        if nTotalSavedThisSession % 5 == 0:
           print(f"Progress This session: {nTotalSavedThisSession} To Go: {len(aIds)} \
                 Average Processing Time: {tTotal/float(nTotalSavedThisSession):.1f}")

    # print out some stats
    if nTotalSavedThisSession:
        print(f"----STATS-----")
        print(f"Msgs Processed: {nTotalSavedThisSession:.1f}")
        print(f"Total Processing Time: {tTotal:.1f}")
        print(f"Average Processing Time: {tTotal/float(nTotalSavedThisSession):.1f}")
        print(f"Not saved, a post still collapsed: {len(aNotSaved)} {' '.join(aNotSaved)}")

    # Close the browser
    driver.quit()


if __name__ == '__main__':
    main()
