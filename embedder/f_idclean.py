CB_BASE_URL = "http://cozybuilders.org/"
AE_BASE_URL = ""
NEWS_BASE_URL = "http://cozybuilders.org/newsletters/" 
CB_PREFIX = "cb__"
AE_PREFIX = "ae__"
NEWS_PREFIX = ""
FOLDER_DELIM = "_-_"
DOT_DELIM = "___"

def pathToSource(filepath):
    print(f"{filepath}")
    filepath.replace(r'\\',r'/')
    print(f"{filepath}")
    filepath.replace(r'//','/')
    filename = filepath.split('/')[-1]
    print(f"{filename}")
    if filename[-4].lower() == '.txt':
        source = filename[:-4]
    else:
        source = filename
    print(f"source:{source}")
    return source

def sourceToUrl(source):
    url = None
    return url