from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import markdownify
import re, random, time
from pypdf import PdfReader
import requests
from io import BytesIO
import os

## Set up
DESC_KEY = 'cozybuilders'
BASE_URL = 'http://cozybuilders.org/'  # Replace with your desired URL

input_path = f"../data/{DESC_KEY}.txt"
output_dir = f"../data/{DESC_KEY}/"
pdf_dir = f"{output_dir}pdfs/"

remove_strings = []
remove_patterns = []
remove_patterns.append(r'\u202f|\ufeff|\u200b|\u2003')
remove_patterns.append(r'Click\s*on\s*the\s*thumbnail\s*to\s*see\s*the\s*larger\s*version')
remove_patterns.append(r'\S+\.(jpg|gif|pdf|htm|zip)') #any jpg, gif, pdf, htm, zip filenames
remove_patterns.append(r'Cozy\s*MKIV\s*Information')
remove_patterns.append(r'\s+')  #any double whitespace

def normalize_quotes(text):
    """Replaces fancy/curly quotes with basic straight quotes in two re.sub lines."""
    
    # 1. Replace all double curly quotes with straight double quotes
    text = re.sub(r'[“”]', '"', text) 
    
    # 2. Replace all single curly quotes/apostrophes with straight single quotes
    text = re.sub(r'[‘’]', "'", text) 
    
    return text

def filter_markdown(markdown_text):
    #remove the first line
    lines = markdown_text.splitlines()
    lines = lines[1:]
    markdown_text = '\n'.join(lines)
    markdown_text = normalize_quotes(markdown_text)
    for remove_text in remove_strings:
        markdown_text = markdown_text.replace(remove_text, " ", flags=re.IGNORECASE) 
        #use a space to stop unintended word merge
    for remove_pattern in remove_patterns:
        markdown_text = re.sub(remove_pattern, ' ', markdown_text, flags=re.IGNORECASE)
    #replace backslashes with null
    markdown_text = markdown_text.replace('\\','')
    #remove back slashes, fwd slashes, colons, square and curly brackets with a space 
    # (might help break up URLs into useful things)
    #replace any repeating characters with space
    markdown_text = re.sub(r'(.)\1{5,}|[<>\(\)\\/:{}[\]\-_#@]', '  ', markdown_text)
    #make Lycoming engne numbers one word
    markdown_text = re.sub(r"[oO0]\s*(\d{3})", r"o\1", markdown_text)
 
    return markdown_text

# Function to convert HTML to Markdown
def html_to_markdown(html):
    # Add space after html close
    html = html.replace(">", "> ")
    # Use markdownify to convert HTML to Markdown
    md = markdownify.markdownify(html, heading_style="ATX", convert=['b', 'i', 'strong', 'em', 'img', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    return md

#function to take elements array and save as html file
def elements_to_html(elements):
    rtnhtml = "<html>\n"

    for element in elements:
        # Extract the inner HTML
        inner_html = element.get_attribute('innerHTML')
        #add to return text
        rtnhtml += " " + inner_html + "\n"

    rtnhtml += "\n</html>"
    return rtnhtml

#function to extract text in list of elements and return markdown blob of text
def elements_to_markdown(elements):
    rtntxt = ""
    for element in elements:
        # Convert the HTML to Markdown
        markdown_text = html_to_markdown(element.get_attribute('innerHTML'))
        #clean up non unicode characters and remove extraneous strings
        markdown_text = re.sub(r'[\x85|\xA0|\uE83A|\uE15F|\uE5D4|\uE5D3|\uE15E|\uE154|\uE984|\uE674]', ' ', markdown_text)

        #add to return text
        rtntxt += " " + markdown_text + " "
    #remove extra spaces
    rtntxt = re.sub(r'\ +', ' ', rtntxt)
    return rtntxt



def download_pdf_to_directory(pdf_url):
    """
    Downloads a file from a URL and saves it to a specified directory.
    
    :param pdf_url: The URL of the PDF file.
    :param target_directory: The local directory where the file should be saved.
    :param file_name: The name to save the file as.
    """
    
    # 1. Ensure the directory exists
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"Created directory: {pdf_dir}")

    file_name = pdf_url.split('/')[-1] 

    # 2. Create the full local file path
    full_path = os.path.join(pdf_dir, file_name)

    print(f"Attempting to download file to: {full_path}")
    
    try:
        # 3. Send a GET request to the URL
        # stream=True is used for efficient handling of large files
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Write the content to the local file in binary mode ('wb')
        with open(full_path, 'wb') as file:
            # response.iter_content is efficient for large files, reading in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Successfully downloaded {file_name} to {full_path}")

        return full_path

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

def savePDFtoText(pdf_url,text_path):
    pdf_path = download_pdf_to_directory(pdf_url)
    bFoundText = False

    reader = PdfReader(pdf_path) 
    
    with open(text_path, 'w', encoding='utf-8') as f:
        for page in reader.pages:
            text = page.extract_text()
            if not bFoundText and len(text) > 0:
                bFoundText = True
            f.write(text)

    if bFoundText is False:
        print(f"no text found in {pdf_url} removing")
        os.remove(text_path)


def saveHtmToText(url,text_path):
        print(f"Htm")
        driver.get(url)

        # 1. Locate the <body> element.
        body_element = driver.find_element(By.TAG_NAME, "body")
        
        # 2. Find ALL descendant elements under the <body> tag.
        # The XPath `//*` selects all elements in the document. 
        # Calling `find_elements` on the 'body' element with `//*` 
        # will find all elements nested within the body.
        elements = body_element.find_elements(By.XPATH, ".//*")
        
        #msghtml = elements_to_html(elements)
        msgtxt = elements_to_markdown(elements)
        embedtxt = filter_markdown(msgtxt)

        with open(text_path,"w") as f:
                f.write(embedtxt)
        f.close()

def process_page(driver,url,output_path):
    ext = url[-3:].lower()
    print(f"processing {url} to {output_path}")
    if ext == 'pdf':
        savePDFtoText(BASE_URL+url,output_path)
    else:
        saveHtmToText(BASE_URL+url,output_path)

######################
##  MAIN
######################
service = Service(executable_path='..//..//chromedriver-win64//chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)

with open(input_path, 'r') as f:
    aUrls = [line.strip() for line in f]
f.close()
print(f"Read {len(aUrls)} lines from {input_path}")

for url in aUrls:
    if len(url) > 0:
        #replace directory and extensions with characters so we can 
        #save filename in embedding and reconstruct url in final application
        filename = url.replace("/","_-_")
        filename = filename.replace(".","___")
        output_path = output_dir+filename
        #now check to see if the file exists
        if os.path.exists(output_path):
            print(f"{url} completed. skipping...")
        else:
            process_page(driver,url,output_path)

print(f"done")