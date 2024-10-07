#get message text v1
# this program will require that an instance of Chrome has been
# started with a debug port available.  See chrome_with_debug.bat

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import markdownify
import re
import os

## Set up
base_url = 'https://groups.google.com/g/cozy_builders/c/'
remove_strings = []
remove_strings.append('Reply to authorForwardDeleteYou do not have permission to delete messages in this groupCopy linkReport messageShow')
remove_strings.append('Reply all Reply to author Forward')
remove_strings.append('You received this message because you are subscribed to the Google Groups "COZY Builders Mailing List" group.')
remove_strings.append('To unsubscribe from this group and stop receiving emails from it, send an email to cozy\_builder...@googlegroups.com.')
remove_strings.append('To view this discussion on the web visit')
remove_strings.append('original messageto Canard Aviators, Cozy Builders')
remove_strings.append('original messageto Cozy Builders')
remove_strings.append('original messageto canard\-aviators@yahoogroups.com, cozy\_builders@googlegroups.com ')
remove_strings.append('original messageto cozy\_builders@googlegroups.com')
remove_strings.append("original messageto Cozy List")
remove_strings.append('original messageto cozy\_builders, canard\-aviators@canardzone.groups.io')
remove_strings.append('original messageto COZY Builders Mailing List')
remove_strings.append('Mailing List Aviators')
remove_strings.append('Canard Aviators Mailing List')
remove_strings.append('original messageto COZY Mailing List')
remove_strings.append('COZY Builders Mailing List')
remove_strings.append('cozy\_builders@googlegroups.com')
remove_strings.append('canard\-aviators')
#remove_strings.append('original messageto')
remove_strings.append('Sent from my iPhone')
remove_strings.append('unread,')
ids_file = 'href_tags1.txt'
load_pause = 4
read_pause = 8
message_dir = 'msgs'
nMax = 5000

# Function to convert HTML to Markdown
def html_to_markdown(html):
    # Use markdownify to convert HTML to Markdown
    md = markdownify.markdownify(html, heading_style="ATX", convert=['b', 'i', 'strong', 'em', 'img', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    return md

#function to extract text in list of elements and return markdown blob of text
def get_markdown_from_elements(elements):
    rtntxt = ""
    for element in elements:
        # Extract the inner HTML
        inner_html = element.get_attribute('innerHTML')
        
        # Convert the HTML to Markdown
        markdown_text = html_to_markdown(inner_html)
        #clean up non unicode characters and remove extraneous strings
        markdown_text = re.sub(r'[^\x00-\x7F]', ' ', markdown_text)
        for remove_text in remove_strings:
            markdown_text = markdown_text.replace(remove_text, "")

        #add to return text
        rtntxt += " " + markdown_text + " "
    return rtntxt

# Function to scrape a message page
def get_message_markdown(id):
    url = base_url + id

    # Navigate to the webpage you want to scrape
    driver.get(url)  
    time.sleep(random.random()*2+load_pause)

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

    # Extract text from each element and convert to Markdown
    # Extract and convert the text
    message_markdown = f"[Original Message ID:{id}]({url})\n"
    message_markdown += get_markdown_from_elements(elements_title) + "\n"
    message_markdown += get_markdown_from_elements(elements_digest)    

    return message_markdown

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

def save_text_to_file(id, msgtxt):
    filename = id + ".md"
    if not id[0].isalpha():
        filename = "msgs/aDigits/" + filename
    else:
        filename = "msgs/" + id.upper()[0] + "/" + filename 

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(msgtxt)


######################
##  MAIN
######################

#set up some stats
nTotalSavedThisSession = 0;

#connect chromedriver
service = Service(executable_path='..//chromedriver-win32//chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)

# get the full list of message ids
ids = read_ids_from_file(ids_file)
print(f"Ids: {len(ids)}")

# get list of message ids that have been saved
ids_saved = get_md_filenames(message_dir)
print(f"Msgs saved: {len(ids_saved)}")

#remove the ids that have been saved from the ids
ids[:] = [x for x in ids if x not in ids_saved]
print(f"Net to complete: {len(ids)}")

# loop on the following
#   select a random message id and check that it has not been saved
#       if has been saved, remove from list and select another 
#           (NR - cleaned list above)
#       if the list is empty we are done (see while conditional)
#   get the message text and save it
#       remove from the list and select another
#   print out some stats
while (len(ids) > 0) & (nTotalSavedThisSession < nMax):
    random_index = random.randint(0, len(ids) - 1)
    random_id = ids.pop(random_index)

    print(f"fetching id: {random_id}")
    msgtxt = get_message_markdown(random_id)
    save_text_to_file(random_id,msgtxt)

    # wait some time
    time.sleep(random.random()*read_pause+1)

    # stats
    nTotalSavedThisSession += 1
    if nTotalSavedThisSession % 5 == 0:
       print(f"Progress This session: {nTotalSavedThisSession} To Go: {len(ids)}")


      

# print out some stats

# Close the browser
driver.quit()